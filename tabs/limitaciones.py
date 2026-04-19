"""
tabs/limitaciones.py  —  Limitaciones del Estudio
"""
import dash_bootstrap_components as dbc
from dash import html


def layout():
    header = html.Div([
        html.H2(" Limitaciones", className="fw-bold mb-1", style={"color": "#001f3f"}),
        html.P("Alcances, restricciones metodológicas y advertencias de interpretación.",
               className="text-muted lead"),
        html.Hr(style={"borderColor": "#f0b8b8"}),
    ], className="mb-4")

    intro = dbc.Alert([
        html.Strong(" Nota: "),
        "El reconocimiento explícito de las limitaciones es parte fundamental del rigor "
        "científico. Las visualizaciones presentadas en este dashboard son descriptivas "
        "y no implican causalidad."
    ], color="light", className="border mb-4")

    lim_datos = dbc.Card([
        dbc.CardHeader(html.H5(" Limitaciones de los Datos", className="mb-0 fw-bold",
                               style={"color": "white"})),
        dbc.CardBody([
            _lim("", "Cobertura temporal hasta 2017",
                 "El dataset cubre únicamente 1999–2017. No incluye la pandemia de COVID-19 "
                 "(2020–), que alteró radicalmente el perfil de mortalidad en EE.UU., ni los "
                 "datos más recientes sobre fentanilo y opioides sintéticos.", "Alta"),
            _lim("", "Supresión de datos por privacidad",
                 "Conteos de muertes < 20 en estados pequeños son suprimidos (celda vacía o nula) "
                 "para proteger la privacidad de individuos. Esto puede subestimar tasas en "
                 "Wyoming, Vermont, Dakota del Norte y otros estados pequeños.", "Moderada"),
            _lim("", "Categorías ICD-10 agrupadas",
                 "El dataset usa categorías resumidas ('Unintentional injuries') que agregan "
                 "múltiples causas específicas (sobredosis, accidentes viales, caídas). No es "
                 "posible desagregar solo sobredosis sin datos adicionales del NVSS.", "Alta"),
            _lim("", "Ausencia de variables socioeconómicas",
                 "El dataset no incluye raza/etnicidad, nivel educativo, ingreso ni cobertura de "
                 "seguro médico. Estas variables son críticas para entender las disparidades "
                 "geográficas observadas.", "Alta"),
        ])
    ], className="shadow-sm border-0 mb-4", style={"borderRadius": "12px"})

    lim_analisis = dbc.Card([
        dbc.CardHeader(html.H5(" Limitaciones del Análisis", className="mb-0 fw-bold",
                               style={"color": "white"})),
        dbc.CardBody([
            _lim("", "Análisis exclusivamente descriptivo",
                 "Este dashboard no realiza inferencia estadística ni pruebas de hipótesis "
                 "formales. Las tendencias observadas son correlacionales, no causales. "
                 "No se aplicaron modelos de regresión ni análisis multivariante.", "Alta"),
            _lim("", "Deaths of Despair: aproximación imperfecta",
                 "La categoría 'Unintentional injuries' incluye accidentes de tráfico, caídas "
                 "y otras causas además de sobredosis. La aproximación sobrestima Deaths of "
                 "Despair en poblaciones con alta accidentalidad laboral.", "Moderada"),
            _lim("", "Comparación entre estados sin ajuste poblacional adicional",
                 "Aunque se usa la tasa ajustada por edad, no se controla por densidad "
                 "poblacional, ruralidad, ingreso mediano ni estructura racial, factores "
                 "que confunden la comparación directa entre estados.", "Moderada"),
            _lim("", "Sesgo de detección en certificados de defunción",
                 "La calidad del registro varía entre estados y períodos. Algunos estados "
                 "históricamente han subregistrado ciertos tipos de muerte (ej. suicidios "
                 "codificados como accidentes) o tenido mayor retraso en el procesamiento.", "Baja"),
        ])
    ], className="shadow-sm border-0 mb-4", style={"borderRadius": "12px"})

    lim_viz = dbc.Card([
        dbc.CardHeader(html.H5(" Limitaciones del Dashboard", className="mb-0 fw-bold",
                               style={"color": "white"})),
        dbc.CardBody([
            _lim("", "Sin análisis a nivel condado",
                 "El nivel de desagregación más fino disponible es el estado. El análisis "
                 "a nivel condado (disponible en CDC WONDER) revelaría disparidades "
                 "intraestatal mucho más pronunciadas, especialmente en WV y Appalachia.", "Alta"),
            _lim("", "Sin comparación internacional",
                 "No se incluye contexto comparativo con otros países de la OCDE, lo que "
                 "limitaría evaluar si las tendencias son específicas de EE.UU. o son "
                 "fenómenos globales.", "Baja"),
            _lim("", "Datos no actualizados automáticamente",
                 "El dashboard usa el CSV descargado manualmente. No hay integración con "
                 "la API de data.cdc.gov para actualizaciones en tiempo real.", "Baja"),
        ])
    ], className="shadow-sm border-0 mb-4", style={"borderRadius": "12px"})

    mejoras = dbc.Card([
        dbc.CardHeader(html.H5(" Extensiones Recomendadas",
                               className="mb-0 fw-bold", style={"color": "white"})),
        dbc.CardBody(dbc.Row([
            dbc.Col(_mejora("", "Integración API",
                "Conectar directamente con data.cdc.gov mediante Socrata API para datos actualizados."), md=3),
            dbc.Col(_mejora("", "Nivel condado",
                "Usar CDC WONDER para análisis a nivel de county con covariables socioeconómicas."), md=3),
            dbc.Col(_mejora("", "Modelos predictivos",
                "Aplicar ARIMA o Prophet para proyectar tendencias de mortalidad a 2025+."), md=3),
            dbc.Col(_mejora("", "Análisis de equidad",
                "Incorporar datos de raza/etnicidad del NVSS para analizar disparidades raciales."), md=3),
        ]))
    ], className="shadow-sm border-0 mb-4", style={"borderRadius": "12px"})

    return dbc.Container([html.Br(), header, intro, lim_datos, lim_analisis, lim_viz, mejoras, html.Br()], fluid=True)


def _lim(dot, titulo, desc, impacto):
    color = {"Alta": "danger", "Moderada": "warning", "Baja": "info"}.get(impacto, "secondary")
    return html.Div([
        dbc.Row([
            dbc.Col(html.Span(dot, className="fs-5"), width="auto"),
            dbc.Col([
                dbc.Row([
                    dbc.Col(html.Strong(titulo, style={"color": "white"})),
                    dbc.Col(dbc.Badge(f"Impacto: {impacto}", color=color, className="ms-2"), width="auto"),
                ], align="center"),
                html.P(desc, className="text-muted small mt-1 mb-0"),
            ])
        ], align="start", className="mb-3")
    ])


def _mejora(icon, titulo, desc):
    return html.Div([
        html.P(icon + " " + titulo, className="fw-bold small mb-1", style={"color": "white"}),
        html.P(desc, className="text-muted small mb-0"),
    ], className="p-2")
