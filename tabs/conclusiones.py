"""
tabs/conclusiones.py  —  Conclusiones y Hallazgos Finales
"""
import dash_bootstrap_components as dbc
from dash import html


def layout():
    header = html.Div([
        html.H2(" Conclusiones", className="fw-bold mb-1", style={"color": "#001f3f"}),
        html.P("Síntesis de hallazgos, implicaciones de política pública y reflexión final.",
               style={"color": "#4a6080"}, className="lead"),
        html.Hr(style={"borderColor": "#001f3f"}),
    ], className="mb-4")

    resumen = dbc.Card([
        dbc.CardBody(dbc.Row([
            dbc.Col(html.Div("", className="display-3 text-center"), md=2),
            dbc.Col([
                html.H5("Síntesis del Análisis", className="fw-bold", style={"color": "#001f3f"}),
                html.P(
                    "El análisis del dataset NCHS (1999–2017) revela transformaciones profundas "
                    "en el perfil de mortalidad de los Estados Unidos. Mientras enfermedades "
                    "crónicas tradicionales (cardiopatías, cáncer) muestran tendencias "
                    "descendentes gracias a avances médicos, las Deaths of Despair presentan "
                    "una escalada alarmante que refleja una crisis socioeconómica y de salud "
                    "pública sin precedentes en la historia reciente del país.",
                    style={"color": "#2c3e50"}, className="mb-0"
                )
            ], md=10)
        ], align="center"))
    ], className="shadow-sm border-0 mb-4",
       style={"background": "white", "borderRadius": "12px", "borderLeft": "5px solid #001f3f"})

    hallazgos = dbc.Card([
        dbc.CardHeader(html.H5(" Hallazgos Principales", className="mb-0 fw-bold",
                               style={"color": "white"})),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(_hallazgo("1", "Descenso de enfermedades cardiovasculares",
                    "La tasa ajustada de enfermedades cardíacas cayó de ~340/100k en 1999 a ~165/100k "
                    "en 2017 (−52%), el mayor descenso en términos absolutos. El cáncer también bajó "
                    "sostenidamente, reflejando mejoras en detección temprana y tratamiento.",
                    "#f5f3ff", "#5a4fcf"), md=6),
                dbc.Col(_hallazgo("2", "Explosión de lesiones no intencionales",
                    "Único grupo entre las 10 causas que muestra incremento sostenido: de 35.3/100k "
                    "en 1999 a 49.4/100k en 2017 (+40%). Directamente vinculado a la crisis de "
                    "opioides prescriptos y, desde 2013, al fentanilo ilícito.",
                    "#fff0f6", "#c94f8a"), md=6),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col(_hallazgo("3", "Alzheimer: la epidemia silenciosa",
                    "La tasa de Alzheimer casi se duplicó en el período: de 16.5 a 31.0/100k. "
                    "Combina el envejecimiento poblacional con mayor reconocimiento diagnóstico "
                    "en certificados de defunción. Proyecta seguir creciendo.",
                    "#f0faf5", "#2d7a4f"), md=6),
                dbc.Col(_hallazgo("4", "Disparidad geográfica extrema",
                    "West Virginia registra tasas de lesiones no intencionales 2.5x el promedio "
                    "nacional en 2017. Mississippi, Alabama y Louisiana lideran en enfermedades "
                    "cardíacas. Hawaii y Minnesota consistentemente presentan las tasas más bajas.",
                    "#fef9e7", "#b07d00"), md=6),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col(_hallazgo("5", "Suicidio: tendencia ascendente sin freno",
                    "La tasa de suicidio aumentó de 10.5 a 14.0/100k (+33%) en el período. "
                    "Sin picos drásticos pero con pendiente continua. Estados rurales del "
                    "Oeste (Montana, Wyoming, Alaska) muestran tasas sistemáticamente más altas.",
                    "#f0f4ff", "#3a5fcf"), md=6),
                dbc.Col(_hallazgo("6", "Influenza: alta volatilidad interanual",
                    "La mortalidad por influenza muestra variabilidad extrema entre años "
                    "(5.7–17.5/100k), dependiente de la virulencia de la cepa anual. "
                    "La temporada 2003–2004 fue particularmente letal.",
                    "#fff8f0", "#b06000"), md=6),
            ]),
        ])
    ], className="shadow-sm border-0 mb-4", style={"borderRadius": "12px"})

    politica = dbc.Card([
        dbc.CardHeader(html.H5(" Implicaciones de Política Pública",
                               className="mb-0 fw-bold", style={"color": "white"})),
        dbc.CardBody(dbc.Row([
            dbc.Col(_politica("", "Regulación farmacéutica",
                "La crisis de opioides demanda regulación estricta de la prescripción de analgésicos, "
                "mayor disponibilidad de naloxona y expansión de programas MAT (Medication-Assisted Treatment)."), md=3),
            dbc.Col(_politica("", "Salud mental",
                "El aumento del suicidio requiere inversión masiva en salud mental comunitaria, "
                "especialmente en zonas rurales donde el acceso a psicólogos y psiquiatras "
                "es mínimo o inexistente."), md=3),
            dbc.Col(_politica("", "Alzheimer y envejecimiento",
                "Se necesita planificación anticipada de infraestructura de cuidado para adultos "
                "mayores, financiamiento de investigación en Alzheimer y capacitación de "
                "cuidadores formales e informales."), md=3),
            dbc.Col(_politica("", "Equidad geográfica",
                "Las disparidades entre estados reflejan inequidades estructurales que requieren "
                "políticas diferenciadas: mayor financiamiento federal para estados con "
                "infraestructura de salud deficiente."), md=3),
        ]))
    ], className="shadow-sm border-0 mb-4", style={"borderRadius": "12px"})

    cierre = dbc.Card([
        dbc.CardBody(html.Div([
            html.Div("", className="display-4 text-center mb-3"),
            html.H5("Reflexión Final", className="fw-bold text-center", style={"color": "#001f3f"}),
            html.P(
                "Los datos de mortalidad son mucho más que estadísticas: representan historias "
                "humanas, decisiones políticas y estructuras sociales. Este análisis demuestra "
                "que la epidemiología descriptiva, cuando se combina con contexto socioeconómico "
                "y herramientas de visualización interactiva, puede transformar números en "
                "narrativas que impulsan cambios reales en política pública.",
                style={"color": "#2c3e50"}, className="text-center"
            ),
            html.P(
                "Datos fuente: NCHS / CDC · Período: 1999–2017 · Desarrollado con Python · Dash · Plotly",
                style={"color": "#6a8aaa"}, className="text-center small fst-italic mb-0"
            ),
        ], className="py-2"))
    ], className="shadow-sm border-0 mb-4",
       style={"background": "white", "borderRadius": "12px", "borderLeft": "5px solid #001f3f"})

    return dbc.Container([html.Br(), header, resumen, hallazgos, politica, cierre, html.Br()], fluid=True)


def _hallazgo(num, titulo, desc, bg, color):
    return html.Div([
        html.Div([
            html.Span(num, className="rounded-circle d-inline-flex align-items-center "
                      "justify-content-center fw-bold me-2",
                      style={"width": "28px", "height": "28px", "background": color,
                             "color": "white", "fontSize": "0.85rem", "flexShrink": "0"}),
            html.Strong(titulo, style={"color": "white", "fontSize": "0.9rem"}),
        ], className="d-flex align-items-center px-3 py-2",
           style={"background": "#001f3f", "borderRadius": "8px 8px 0 0"}),
        html.Div(
            html.P(desc, className="small mb-0", style={"color": "#2c3e50", "lineHeight": "1.65"}),
            className="p-3",
            style={"background": "white", "borderRadius": "0 0 8px 8px",
                   "border": "1px solid #dee2e6", "borderTop": "none"}
        ),
    ], className="mb-3",
       style={"borderRadius": "8px", "overflow": "hidden",
              "boxShadow": "0 2px 8px rgba(0,31,63,0.10)"})


def _politica(icon, titulo, desc):
    return html.Div([
        html.P(icon + " " + titulo, className="fw-bold small mb-1", style={"color": "#001f3f"}),
        html.P(desc, className="small mb-0", style={"color": "#2c3e50"}),
    ], className="p-2")
