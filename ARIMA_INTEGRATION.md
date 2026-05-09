# 📊 Integración de Pronóstico ARIMA en NCHS Dashboard

## ✅ Cambios Realizados

Se ha agregado una nueva pestaña **"Pronóstico ARIMA"** al dashboard NCHS con pronósticos de series de tiempo interactivos.

### Archivos Modificados

1. **`app.py`**
   - ✅ Importación de `pronostico_arima` 
   - ✅ Agregado a `TABS_CONFIG`
   - ✅ Separador de sección "PRONÓSTICO"

2. **`requirements.txt`**
   - ✅ Agregado: `statsmodels==0.14.0`
   - ✅ Agregado: `scikit-learn==1.4.2`

### Archivos Nuevos

3. **`tabs/pronostico_arima.py`**
   - ✅ Nueva pestaña con interfaz ARIMA completa
   - ✅ Parámetros ajustables (p, d, q)
   - ✅ Gráficos interactivos con pronóstico
   - ✅ Métricas: RMSE, MAE, AIC
   - ✅ Validación con conjunto de prueba
   - ✅ Intervalo de confianza (95%)

---

## 🚀 Instalación y Ejecución Local

### Paso 1: Instalar Dependencias

```bash
cd nchs_dashboard_v2
pip install -r requirements.txt
```

### Paso 2: Ejecutar el Dashboard

```bash
python app.py
```

El dashboard estará disponible en `http://localhost:8080`

---

## 🌐 Despliegue en Google Cloud Run

### Paso 1: Preparar el Proyecto

El `Dockerfile` existente funcionará sin cambios. Solo asegúrate de que:

1. **requirements.txt está actualizado** ✅ (ya incluye statsmodels y sklearn)
2. **app.py está listo** ✅ (ya importa pronostico_arima)
3. **pronostico_arima.py está en `/tabs`** ✅ (agregado)

### Paso 2: Build y Deploy (Opción 1: Cloud Run)

```bash
# Desde la raíz del proyecto
gcloud builds submit --tag gcr.io/PROJECT_ID/nchs-dashboard
gcloud run deploy nchs-dashboard \
  --image gcr.io/PROJECT_ID/nchs-dashboard \
  --platform managed \
  --region us-central1 \
  --port 8080
```

Reemplaza `PROJECT_ID` con tu ID de proyecto de GCP.

### Paso 2b: Deploy (Opción 2: Cloud Run desde GitHub)

Si tu código está en GitHub:
1. Conecta el repositorio en Cloud Run
2. Configura el deploy automático
3. GCP se encargará del resto

---

## 📋 Descripción de la Pestaña ARIMA

### Componentes Principales

#### 🎛️ Panel de Control

**Selecciones:**
- 🌍 **Estado / Nivel Nacional**: Selecciona qué geografía analizar
- 💀 **Causa de Muerte**: Selecciona la causa (Heart disease, Cancer, etc.)

**Parámetros ARIMA:**
- **P (AutoRegressive)**: 0-5 (términos autorregresivos)
- **D (Differencing)**: 0-3 (diferenciación para estacionariedad)
- **Q (Moving Average)**: 0-5 (términos de error rezagados)
- **Años a Pronosticar**: 1-10 (horizonte de pronóstico)

#### 📈 Gráfico Interactivo

Muestra:
- **Línea azul**: Datos históricos (1999-2017)
- **Línea naranja**: Conjunto de prueba (validación)
- **Línea verde punteada**: Predicciones en test
- **Línea roja punteada**: Pronóstico futuro
- **Área sombreada roja**: Intervalo de confianza (95%)

#### 📊 Métricas de Desempeño

- **RMSE**: Error cuadrático raíz (menor = mejor)
- **MAE**: Error absoluto medio (en unidades de tasa)
- **AIC**: Criterio de información de Akaike (penaliza complejidad)
- **Observaciones**: Total de años de datos disponibles

#### 📋 Resumen del Modelo

Tabla ASCII con:
- Parámetros ARIMA utilizados
- Número de observaciones (train/test)
- Métricas de validación
- Información de interpretación

---

## 💡 Cómo Usar la Nueva Pestaña

### Caso de Uso 1: Pronóstico de Suicidios

1. Abre la pestaña **"Pronóstico ARIMA"**
2. Selecciona **Estado**: "West Virginia"
3. Selecciona **Causa**: "Suicide"
4. Ajusta **P=1, D=1, Q=1** (valores por defecto)
5. Pronóstica **5 años** adelante
6. Observa la tendencia y el intervalo de confianza

### Caso de Uso 2: Optimizar Parámetros

1. Comienza con **ARIMA(1,1,1)**
2. Incrementa **P gradualmente** si el pronóstico es plano
3. Incrementa **Q** si hay patrones de error
4. Busca **minimizar RMSE** sin sobre-ajustar
5. Compara **AIC** entre modelos diferentes

### Caso de Uso 3: Análisis Comparativo

1. Selecciona una causa (ej: "Heart disease")
2. Compara pronósticos entre estados diferentes
3. Examina cómo varían las tendencias geográficamente
4. Usa los intervalos de confianza para decisiones

---

## ⚙️ Ajustes Técnicos Recomendados

### Si es Lento en Cloud Run

1. **Aumentar memoria**: En la consola de Cloud Run, asigna más RAM
   
   ```bash
   gcloud run deploy nchs-dashboard \
     --memory 1Gi \
     --cpu 1
   ```

2. **Caché de datos**: El `load_df()` usa `@lru_cache`, así que no se recarga cada vez

### Si Hay Errores de ARIMA

- **"Series is not stationary"**: Incrementa **D**
- **"ARIMA did not converge"**: Reduce **P, D, Q**
- **"Insufficient data"**: Usa menos años de pronóstico

---

## 🔧 Personalización

### Cambiar Colores

En `pronostico_arima.py`, línea ~290:

```python
# Cambiar colores de las líneas
fig.add_trace(go.Scatter(
    line=dict(color="#e74c3c", width=2.5, dash="dash"),  # ← Aquí
    ...
))
```

### Cambiar Número de Observaciones en Train/Test

En `pronostico_arima.py`, línea ~240:

```python
# De: split_idx = max(int(len(y) * 0.8), len(y) - 5)
# A:  split_idx = max(int(len(y) * 0.7), len(y) - 5)  # 70% train, 30% test
```

### Agregar Más Métricas

Importa desde `sklearn.metrics`:

```python
from sklearn.metrics import mean_absolute_percentage_error

mape = mean_absolute_percentage_error(y_test, pred_test)
```

---

## 🧪 Testing Local

### Test Rápido de Importación

```python
# En terminal Python
python -c "from tabs import pronostico_arima; print('✅ ARIMA importa correctamente')"
```

### Test del Callback

```bash
# Ejecutar con debug habilitado
python app.py  # debug=False en prod, True en dev
```

---

## 📞 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'statsmodels'"

```bash
pip install statsmodels scikit-learn
```

### Error: "PronosticoARIMA" no aparece en el dashboard

1. Verifica que `pronostico_arima.py` esté en `/tabs`
2. Verifica que `app.py` importe correctamente
3. Reinicia el servidor

### Gráfico muestra "Error al entrenar ARIMA"

Puede ocurrir si:
- Hay menos de 5 datos históricos para esa causa/estado
- Los parámetros (p, d, q) son incompatibles con los datos
- Intenta reducir p, d, q o cambiar la causa/estado

---

## 📚 Referencias

- **Statsmodels ARIMA**: https://www.statsmodels.org/stable/generated/statsmodels.tsa.arima.model.ARIMA.html
- **Dash Documentation**: https://dash.plotly.com/
- **Google Cloud Run**: https://cloud.google.com/run/docs

---

## ✨ Próximos Pasos Opcionales

1. **SARIMA**: Agregar estacionalidad
2. **Backtesting**: Evaluar predicciones históricas
3. **Exportar Predicciones**: Descargar CSV/Excel
4. **Comparación de Modelos**: ARIMA vs ExponentialSmoothing
5. **Alertas**: Notificar si la predicción cruza umbrales

---

**¡Listo para desplegar en Cloud Run! 🚀**

Para re-desplegar:

```bash
git add .
git commit -m "Add ARIMA forecasting module"
git push origin main
# Cloud Run se actualiza automáticamente si está configurado
```
