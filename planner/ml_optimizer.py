import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from datetime import datetime, timedelta
from .models import Event

class TaskOptimizer:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.label_encoders = {
            'event_type': LabelEncoder(),
            'priority': LabelEncoder()
        }
    
    def _extract_features(self, events):
        """
        Extrae características de los eventos para el entrenamiento.
        """
        features = []
        for event in events:
            # Convertir hora del día a valor numérico (0-24)
            start_hour = event.start_time.hour + event.start_time.minute / 60.0
            duration = (event.end_time - event.start_time).total_seconds() / 3600.0  # duración en horas
            
            # Codificar variables categóricas
            event_type_encoded = self.label_encoders['event_type'].fit_transform([event.event_type])[0]
            priority_encoded = self.label_encoders['priority'].fit_transform([event.priority])[0]
            
            # Características del evento
            feature_vector = [
                start_hour,  # hora de inicio
                duration,    # duración
                event_type_encoded,
                priority_encoded,
                event.start_time.weekday(),  # día de la semana (0-6)
                1 if event.is_completed else 0,  # estado de completitud
            ]
            features.append(feature_vector)
        
        return np.array(features)
    
    def _extract_targets(self, events):
        """
        Extrae los valores objetivo para el entrenamiento (productividad/éxito del horario).
        """
        # Por ahora, usamos una métrica simple basada en completitud y prioridad
        targets = []
        for event in events:
            priority_score = {
                'alta': 3,
                'media': 2,
                'baja': 1
            }.get(event.priority, 2)
            
            # Calcular score basado en completitud y prioridad
            score = priority_score
            if event.is_completed:
                score *= 1.5
                
            targets.append(score)
        
        return np.array(targets)
    
    def train(self, user_events):
        """
        Entrena el modelo con los eventos históricos del usuario.
        """
        if len(user_events) < 5:  # Necesitamos un mínimo de datos para entrenar
            return False
            
        X = self._extract_features(user_events)
        y = self._extract_targets(user_events)
        
        self.model.fit(X, y)
        return True
    
    def optimize_schedule(self, user_events, start_date, end_date):
        """
        Genera sugerencias de optimización para el horario, evitando conflictos de tiempo.
        """
        if not self.train(user_events):
            return []
            
        suggestions = []
        current_events = [e for e in user_events if start_date <= e.start_time.date() <= end_date]
        
        # Generar posibles horarios alternativos
        for event in current_events:
            best_score = -1
            best_time = None
            
            # Probar diferentes horas del día
            for hour in range(8, 20):  # 8am a 8pm
                test_time = event.start_time.replace(hour=hour, minute=0)
                
                # Crear feature vector para esta hora
                feature_vector = np.array([[
                    hour + 0.0,  # hora de inicio
                    (event.end_time - event.start_time).total_seconds() / 3600.0,
                    self.label_encoders['event_type'].transform([event.event_type])[0],
                    self.label_encoders['priority'].transform([event.priority])[0],
                    test_time.weekday(),
                    1 if event.is_completed else 0
                ]])
                
                # Predecir score para este horario
                score = self.model.predict(feature_vector)[0]
                
                if score > best_score:
                    best_score = score
                    best_time = test_time
            
            # Si encontramos un mejor horario, crear sugerencia
            if best_time and best_time != event.start_time:
                duration = event.end_time - event.start_time
                suggestions.append({
                    'event_id': event.id,
                    'title': event.title,
                    'current_time': event.start_time,
                    'suggested_time': best_time,
                    'suggested_end_time': best_time + duration,
                    'improvement_score': best_score,
                    'reason': self._get_suggestion_reason(event, best_time)
                })
        
        return sorted(suggestions, key=lambda x: x['improvement_score'], reverse=True)
    
    def _get_suggestion_reason(self, event, suggested_time):
        """
        Genera una explicación para la sugerencia de cambio de horario.
        """
        current_hour = event.start_time.hour
        suggested_hour = suggested_time.hour
        
        if event.event_type == 'tarea':
            if suggested_hour < 12:
                return "Las tareas suelen ser más productivas en la mañana"
            elif suggested_hour < 17:
                return "Este horario tiene mejor rendimiento para tareas"
        elif event.event_type == 'clase':
            return "Este horario se alinea mejor con tu patrón de clases"
        elif event.event_type == 'descanso':
            if suggested_hour > current_hour:
                return "Un descanso más tarde puede ser más beneficioso"
            else:
                return "Un descanso más temprano puede mejorar tu productividad"
                
        return "Este horario puede mejorar tu productividad"