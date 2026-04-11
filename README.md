# NCHS Dashboard · Principales Causas de Muerte en Estados Unidos

Dashboard interactivo para el análisis exploratorio de datos de mortalidad en Estados Unidos (1999–2017), desarrollado con Python, Dash y Plotly. Los datos provienen del **National Center for Health Statistics (NCHS)**, rama estadística del CDC.

---

## Contexto

Comprender las tendencias de mortalidad a largo plazo es fundamental para la política de salud pública, la investigación académica y la toma de decisiones basada en evidencia. Este dashboard permite explorar cómo han evolucionado las principales causas de muerte en EE.UU. a lo largo de casi dos décadas, identificar disparidades geográficas entre estados y analizar el fenómeno conocido como **Deaths of Despair** — el aumento sostenido de muertes por suicidio y lesiones no intencionales asociadas a la crisis de opioides.

La herramienta está diseñada tanto como instrumento analítico como recurso de presentación, ofreciendo visualizaciones interactivas que transforman datos crudos en narrativas claras.

---

## Cómo ejecutar la aplicación

Todos los archivos necesarios para ejecutar la aplicación localmente se encuentran dentro de la carpeta `nchs_dashboard`. El dashboard fue desarrollado con Python usando la librería Dash (asegúrate de tener Python instalado en tu computador).

**1. (Opcional)** Se recomienda usar un entorno virtual para evitar conflictos con otras librerías:

```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

**2.** Instala las dependencias (archivo ubicado dentro de la carpeta `nchs_dashboard`):

```bash
pip install -r requirements.txt
```

**3.** Inicia la aplicación (dentro de la carpeta `nchs_dashboard`):

```bash
python app.py
```

**4.** Accede al dashboard en tu navegador:

```
http://localhost:8080/
```

---

## Estructura del Dashboard

| Pestaña | Contenido |
|---------|-----------|
| **Introducción** | Resumen general, métricas clave y navegación del dashboard |
| **Marco Teórico** | Fundamentos conceptuales y clasificación ICD-10 |
| **Metodología** | Descripción del dataset, limpieza y decisiones analíticas |
| **Evolución de Tasas** | Series temporales interactivas por causa y estado (1999–2017) |
| **Ranking por Año** | Gráfico animado con el ranking de las 10 causas líderes por año |
| **Deaths of Despair** | Análisis de suicidio y lesiones no intencionales (crisis de opioides) |
| **Análisis Geográfico** | Mapa coroplético de tasas de mortalidad por estado |
| **Caso: West Virginia** | Estudio de caso del estado más afectado por la crisis de opioides |
| **Limitaciones** | Alcance metodológico, advertencias e interpretación de los datos |
| **Conclusiones** | Hallazgos principales, implicaciones de política pública y reflexión final |

---

## Datos

- **Fuente:** National Center for Health Statistics (NCHS) / Centers for Disease Control and Prevention (CDC)
- **Período:** 1999–2017
- **Cobertura:** 50 estados + Distrito de Columbia + total nacional
- **Causas:** 10 principales causas de muerte + All causes (clasificación ICD-10)
- **Métrica:** Tasa de mortalidad ajustada por edad por cada 100,000 habitantes (estandarizada a la población de EE.UU. del año 2000)

---

## Tecnologías utilizadas

- **Python** — lenguaje principal
- **Dash** — framework para aplicaciones web
- **Plotly** — visualizaciones interactivas
- **Dash Bootstrap Components** — layout y componentes de interfaz
- **Pandas** — procesamiento de datos

---

## Equipo

Este proyecto fue desarrollado como ejercicio académico de análisis de datos usando información públicamente disponible del NCHS/CDC.
