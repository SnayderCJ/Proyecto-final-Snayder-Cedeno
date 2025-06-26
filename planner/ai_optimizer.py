import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import GradientBoostingClassifier
import joblib
import os
import json
from django.conf import settings

class SmartScheduleOptimizer:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), 'trained_models')
        
        self.model_path = model_path
        self.model = None
        self.encoders = None
        self.scaler = None
        self.metadata = None
        self.is_loaded = False
        
        self.load_model()
    
    def load_model(self):
        try:
            model_file = os.path.join(self.model_path, 'smart_scheduler_model.joblib')
            encoders_file = os.path.join(self.model_path, 'smart_scheduler_encoders.joblib')
            scaler_file = os.path.join(self.model_path, 'smart_scheduler_scaler.joblib')
            metadata_file = os.path.join(self.model_path, 'smart_scheduler_metadata.json')
            
            if all(os.path.exists(f) for f in [model_file, encoders_file, scaler_file]):
                self.model = joblib.load(model_file)
                self.encoders = joblib.load(encoders_file)
                self.scaler = joblib.load(scaler_file)
                
                # Cargar metadatos si existe
                if os.path.exists(metadata_file):
                    with open(metadata_file, 'r') as f:
                        self.metadata = json.load(f)
                
                self.is_loaded = True
                print(f"✅ Modelo cargado exitosamente desde {self.model_path}")
                
                if self.metadata:
                    print(f"📊 Versión del modelo: {self.metadata.get('version', 'N/A')}")
                    print(f"📅 Entrenado el: {self.metadata.get('trained_date', 'N/A')}")
                
            else:
                print(f"❌ No se encontraron todos los archivos del modelo en {self.model_path}")
                self.is_loaded = False
                
        except Exception as e:
            print(f"❌ Error al cargar el modelo: {str(e)}")
            self.is_loaded = False
    
    def validate_event_data(self, event_data):
        required_fields = ['event_type', 'priority', 'duration', 'weekday']
        for field in required_fields:
            if field not in event_data:
                raise ValueError(f"Campo requerido faltante: {field}")
        
        valid_event_types = ["tarea", "clase", "examen", "proyecto", "estudio", "descanso", "personal", "otro"]
        if event_data['event_type'] not in valid_event_types:
            raise ValueError(f"Tipo de evento no válido: {event_data['event_type']}")
        
        valid_priorities = ["alta", "media", "baja"]
        if event_data['priority'] not in valid_priorities:
            raise ValueError(f"Prioridad no válida: {event_data['priority']}")
        
        return True

    def process_due_date(self, due_date, start_date=None):
        if not due_date:
            return None, 999
        
        if start_date is None:
            start_date = datetime.now().date()
        elif isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        elif isinstance(start_date, datetime):
            start_date = start_date.date()
        
        if isinstance(due_date, str):
            try:
                due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
            except ValueError:
                try:
                    due_date = datetime.strptime(due_date, '%Y-%m-%dT%H:%M:%S').date()
                except ValueError:
                    return None, 999
        elif isinstance(due_date, datetime):
            due_date = due_date.date()
        
        days_to_deadline = (due_date - start_date).days
        return due_date, max(0, days_to_deadline)

    def transform_data(self, df):
        if not self.is_loaded:
            raise ValueError("El modelo no está cargado. Verifica los archivos del modelo.")
        
        df = df.copy()
        
        df['event_type_encoded'] = self.encoders['event_type'].transform(df['event_type'])
        df['priority_encoded'] = self.encoders['priority'].transform(df['priority'])

        numeric_features = ['start_hour', 'duration', 'weekday', 'days_to_deadline']
        df[numeric_features] = self.scaler.transform(df[numeric_features])

        return df[['start_hour', 'duration', 'event_type_encoded',
                 'priority_encoded', 'weekday', 'days_to_deadline']]

    def predict_best_schedule(self, event_data, user_events=None):
        """Predice el mejor horario para un evento verificando disponibilidad"""
        if not self.is_loaded:
            raise ValueError("El modelo no está cargado. Verifica los archivos del modelo.")

        self.validate_event_data(event_data)

        due_date, days_to_deadline = self.process_due_date(
            event_data.get('due_date'), 
            event_data.get('start_date')
        )

        resultados = []
        for hora in range(6, 23):  
            event_test = event_data.copy()
            event_test['start_hour'] = hora
            event_test['days_to_deadline'] = days_to_deadline

            is_available = self._check_time_availability(
                hora, event_data.get('duration', 1), 
                event_data.get('start_date'), user_events
            )

            df_test = pd.DataFrame([event_test])
            X = self.transform_data(df_test)

            prob = self.model.predict_proba(X)[0][1]
            score = self._calculate_score(prob, hora, event_test)
            

            if not is_available:
                score *= 0.1  

            resultados.append({
                'hora': hora,
                'probabilidad': prob,
                'score': score,
                'hora_formateada': f"{hora:02d}:00",
                'disponible': is_available  
            })

        df_result = pd.DataFrame(resultados)
        mejor = df_result.loc[df_result['score'].idxmax()]

        return {
            'mejor_hora': int(mejor['hora']),
            'mejor_hora_formateada': mejor['hora_formateada'],
            'probabilidad': float(mejor['probabilidad']),
            'score': float(mejor['score']),
            'confianza': self._calculate_confidence(df_result),
            'disponible': bool(mejor['disponible']),  # ✅ NUEVO
            'todas_opciones': df_result.to_dict('records')
        }

    def _calculate_score(self, prob, hora, event):
        """Calcula el score mejorado con más factores"""
        score = prob
        
        if event['priority'] == 'alta':
            score *= 1.3
        elif event['priority'] == 'baja':
            score *= 0.8

        if event['event_type'] in ['estudio', 'tarea', 'proyecto']:
            if 9 <= hora <= 11 or 15 <= hora <= 17:  # Horas de mayor concentración
                score *= 1.3
            elif hora >= 20:
                score *= 0.7
        elif event['event_type'] == 'clase':
            if 8 <= hora <= 18:  
                score *= 1.1
        elif event['event_type'] in ['descanso', 'personal']:
            if hora >= 18 or hora <= 8: 
                score *= 1.2


        if event.get('days_to_deadline', 999) <= 1:
            score *= 1.4
        elif event.get('days_to_deadline', 999) <= 3:
            score *= 1.2

        return score

    def _calculate_confidence(self, df_result):

        scores = df_result['score'].values
        max_score = scores.max()
        mean_score = scores.mean()
        
        confidence = min(1.0, (max_score - mean_score) / mean_score + 0.5)
        return float(confidence)

    def optimize_schedule(self, events_queryset, start_date, end_date):
        if not self.is_loaded:
            raise ValueError("El modelo no está cargado. Verifica los archivos del modelo.")
        
        suggestions = []
        
        for event in events_queryset:
            try:
                event_data = {
                    'event_type': self._map_django_event_type(event.event_type),
                    'priority': self._map_django_priority(event.priority),
                    'duration': self._calculate_duration(event.start_time, event.end_time),
                    'weekday': event.start_time.weekday(),
                    'due_date': event.due_date,
                    'start_date': start_date
                }
                
                
                prediction = self.predict_best_schedule(event_data)
                
                current_date = event.start_time.date()
                suggested_datetime = datetime.combine(
                    current_date, 
                    datetime.min.time().replace(hour=prediction['mejor_hora'])
                )
                suggested_end_datetime = suggested_datetime + timedelta(hours=event_data['duration'])
                
                if suggested_datetime.hour != event.start_time.hour:
                    suggestions.append({
                        'event_id': event.id,
                        'title': event.title,
                        'current_time': event.start_time.isoformat(),
                        'suggested_time': suggested_datetime.isoformat(),
                        'suggested_end_time': suggested_end_datetime.isoformat(),
                        'improvement_score': round((prediction['score'] - 0.5) * 100, 1),
                        'confianza': prediction['confianza'],
                        'mejor_hora': prediction['mejor_hora'],
                        'todas_opciones': prediction['todas_opciones'],
                        'reason': self._generate_reason(event_data, prediction)
                    })
                    
            except Exception as e:
                print(f"Error procesando evento {event.id}: {str(e)}")
                continue
        
        return suggestions

    def _map_django_event_type(self, django_type):
        mapping = {
            'task': 'tarea',
            'class': 'clase', 
            'exam': 'examen',
            'project': 'proyecto',
            'study': 'estudio',
            'break': 'descanso',
            'personal': 'personal',
            'other': 'otro'
        }
        return mapping.get(django_type, 'otro')

    def _map_django_priority(self, django_priority):
        mapping = {
            'high': 'alta',
            'medium': 'media',
            'low': 'baja'
        }
        return mapping.get(django_priority, 'media')

    def _calculate_duration(self, start_time, end_time):
        duration = (end_time - start_time).total_seconds() / 3600
        return round(duration, 1)

    def _generate_reason(self, event_data, prediction):
        reasons = []
        
        if prediction['confianza'] > 0.8:
            reasons.append("Alta confianza en la predicción")
        
        if event_data['event_type'] in ['estudio', 'tarea']:
            if 9 <= prediction['mejor_hora'] <= 11:
                reasons.append("Horario óptimo para concentración matutina")
            elif 15 <= prediction['mejor_hora'] <= 17:
                reasons.append("Horario ideal para productividad vespertina")
        
        if event_data['priority'] == 'alta':
            reasons.append("Prioridad alta requiere horario premium")
        
        if event_data.get('days_to_deadline', 999) <= 3:
            reasons.append("Proximidad del deadline sugiere este horario")
        
        if prediction.get('disponible', True):
            reasons.append("Horario disponible sin conflictos")
        
        return ". ".join(reasons) if reasons else "Optimización basada en patrones de productividad"

    def _check_time_availability(self, hora, duration, start_date, user_events):
      
        if not user_events:
            return True
            
        from django.utils import timezone
            
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        elif isinstance(start_date, datetime):
            start_date = start_date.date()
            
        proposed_start = datetime.combine(start_date, datetime.min.time().replace(hour=hora))
        proposed_end = proposed_start + timedelta(hours=duration)
        
        if timezone.is_aware(user_events[0].start_time if user_events else None):
            proposed_start = timezone.make_aware(proposed_start)
            proposed_end = timezone.make_aware(proposed_end)
        

        for event in user_events:
            if (event.start_time <= proposed_start < event.end_time):
                return False
                
            if (event.start_time < proposed_end <= event.end_time):
                return False
                
            if (proposed_start <= event.start_time and proposed_end >= event.end_time):
                return False
        
        return True
