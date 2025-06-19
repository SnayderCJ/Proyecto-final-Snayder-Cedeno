import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib
from datetime import datetime, timedelta

# Generar datos simulados
np.random.seed(42)
fechas = [datetime(2025, 6, 1) + timedelta(days=i) for i in range(20)]
hora_inicio = [datetime.strptime(f"{np.random.randint(6, 20)}:{np.random.choice([0, 15, 30, 45])}", "%H:%M").time() for _ in range(20)]
duraciones = [np.random.randint(25, 120) for _ in range(20)]  # entre 25 y 120 minutos
hora_fin = [(datetime.combine(datetime.today(), hi) + timedelta(minutes=d)).time() for hi, d in zip(hora_inicio, duraciones)]

df = pd.DataFrame({
    "fecha": fechas,
    "hora_inicio": hora_inicio,
    "hora_fin": hora_fin
})

df['duracion_min'] = duraciones
df['hora_inicio_decimal'] = df['hora_inicio'].apply(lambda t: t.hour + t.minute / 60)
df['dia_semana'] = pd.to_datetime(df['fecha']).dt.weekday

# Simular productividad como target
df['productividad'] = (
    df['duracion_min'] * 0.6 +
    df['hora_inicio_decimal'] * 1.5 +
    df['dia_semana'] * 2 +
    np.random.normal(0, 10, len(df))
)
df['productividad'] = np.clip(df['productividad'], 0, 100)

# Entrenar modelo
X = df[['duracion_min', 'hora_inicio_decimal', 'dia_semana']]
y = df['productividad']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

modelo = RandomForestRegressor(n_estimators=100, random_state=42)
modelo.fit(X_train, y_train)

# Evaluar
y_pred = modelo.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f"MSE del modelo: {mse:.2f}")

# Guardar modelo
joblib.dump(modelo, 'planner/ml/productividad_model.pkl')
print("✅ Modelo guardado como productividad_model.pkl")
