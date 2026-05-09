"""
tabs/introduccion.py  —  Pestaña de Introducción
"""
import dash_bootstrap_components as dbc
from dash import html, dcc
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from data.loader import load_df


# Total muertes nacionales por causa 1999-2017
TOTALES = {
    "Heart disease":           12_222_640,
    "Cancer":                  10_843_644,
    "Stroke":                   2_726_523,
    "CLRD":                     2_594_927,
    "Unintentional injuries":   2_347_820,
    "Alzheimer's disease":      1_494_816,
    "Diabetes":                 1_399_943,
    "Influenza and pneumonia":  1_094_641,
    "Kidney disease":             858_613,
    "Suicide":                    697_016,
}

CAUSA_COLORES = {
    "Heart disease":           "#f0b8b8",
    "Cancer":                  "#c5b8f0",
    "Unintentional injuries":  "#fde8b0",
    "CLRD":                    "#b8d8f0",
    "Stroke":                  "#f7c5e0",
    "Alzheimer's disease":     "#d4f0b8",
    "Diabetes":                "#f0d4b8",
    "Influenza and pneumonia": "#b8f0e8",
    "Kidney disease":          "#b8c5f0",
    "Suicide":                 "#f0b8d4",
}

MAX_TOTAL = max(TOTALES.values())


def layout():
    hero = dbc.Row(dbc.Col(html.Div([
        html.Div("", className="display-1 text-center mb-3"),
        html.H1("Leading Causes of Death in the United States",
                className="display-5 fw-bold text-center mb-2",
                style={"color": "#001f3f"}),
        html.P("Análisis histórico 1999–2017 · NCHS / Centers for Disease Control and Prevention",
               className="lead text-center mb-4",
               style={"color": "#4a6080"}),
        html.Hr(style={"borderColor": "#001f3f", "borderWidth": "2px"}),
    ]), width=12), className="mb-4")

    cards = dbc.Row([
        _card("Fuente Oficial",
              "National Center for Health Statistics (NCHS), rama estadística del CDC. "
              "Los datos provienen del Sistema Nacional de Estadísticas Vitales, que registra "
              "todos los certificados de defunción de los 50 estados y D.C."),
        _card("Cobertura Temporal",
              "El dataset abarca 19 años (1999–2017), permitiendo identificar tendencias "
              "de largo plazo, puntos de inflexión epidemiológicos y el impacto de políticas "
              "públicas de salud en la mortalidad estadounidense."),
        _card("Metodología CDC",
              "Las tasas de mortalidad se ajustan por año usando la población estándar "
              "de EE.UU. del año 2000, lo que elimina sesgos demográficos y permite "
              "comparaciones válidas entre estados con distintas estructuras etarias."),
        _card("Cobertura Geográfica",
              "Datos desagregados para los 50 estados, el Distrito de Columbia y el "
              "total nacional, con 10 causas de muerte más 'All causes', clasificadas "
              "según el ICD-10 (Clasificación Internacional de Enfermedades)."),
    ], className="mb-4")

    # Causas con barra de total de muertes — sin emojis
    causas_rows_col1 = []
    causas_rows_col2 = []
    for i, (causa, total) in enumerate(TOTALES.items()):
        color = CAUSA_COLORES.get(causa, "#ccc")
        pct   = total / MAX_TOTAL * 100
        item  = html.Div([
            dbc.Row([
                dbc.Col(html.Span(causa, className="fw-semibold small",
                                  style={"color": "white"}), width=8),
                dbc.Col(html.Span(f"{total:,}", className="text-muted small text-end",
                                  style={"fontSize": "0.75rem"}), width=4),
            ], className="mb-1 align-items-center"),
            dbc.Progress(value=pct, max=100,
                         style={"height": "8px", "borderRadius": "4px",
                                "backgroundColor": "#f0f0f0"},
                         color=None,
                         className="mb-3"),
            # Barra coloreada custom
        ], style={"position": "relative"})

        # Versión con div de color manual (más control)
        item2 = html.Div([
            dbc.Row([
                dbc.Col(html.Span(causa, className="fw-semibold small",
                                  style={"color": "#3a3a5c", "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"}), width=7),
                dbc.Col(html.Span(f"{total:,} muertes", className="text-end text-muted",
                                  style={"fontSize": "0.72rem", "display": "block", "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"}), width=5),
            ], className="mb-1 align-items-center"),
            html.Div(
                html.Div(style={"width": f"{pct:.1f}%", "height": "8px",
                                "background": "#001f3f", "borderRadius": "4px",
                                "transition": "width 0.5s ease"}),
                style={"background": "#f0f0f0", "borderRadius": "4px",
                       "height": "8px", "marginBottom": "10px"}
            ),
        ])
        if i < 5:
            causas_rows_col1.append(item2)
        else:
            causas_rows_col2.append(item2)

    causas_card = dbc.Card([
        dbc.CardHeader(html.H5("Las 10 Causas Líderes de Muerte Analizadas (Total 1999–2017)",
                               className="mb-0 fw-bold", style={"color": "white",
                               "background": "#001f3f"})),
        dbc.CardBody(dbc.Row([
            dbc.Col(causas_rows_col1, md=6),
            dbc.Col(causas_rows_col2, md=6),
        ]), style={"background": "white"})
    ], className="shadow-sm border-0 mb-4", style={"borderRadius": "12px", "overflow": "hidden"})

    # Navegacion clickeable — sin emojis, con Store trigger
    nav_items_fila1 = [
        ("tab-marco",       "Marco Teórico",      "Variables y fundamentos ICD-10",          "#001f3f"),
        ("tab-metodologia", "Metodología",         "Dataset, tasas ajustadas y limpieza",     "#001f3f"),
        ("tab-evolucion",   "Evolución de Tasas",  "Series temporales por causa y estado",    "#001f3f"),
        ("tab-ranking",     "Ranking por Año",     "Top causas con slider interactivo",       "#001f3f"),
        ("tab-despair",     "Deaths of Despair",   "Suicidio y lesiones no intencionales",    "#001f3f"),
        ("tab-geo",         "Análisis Geográfico", "Mapa coroplético interactivo",            "#001f3f"),
    ]
    nav_items_fila2 = [
        ("tab-wv",    "Caso: West Virginia",  "El estado con mayor crisis de opioides", "#001f3f"),
        ("tab-limit", "Limitaciones",         "Alcances y restricciones del análisis",  "#001f3f"),
        ("tab-conclu","Conclusiones",         "Hallazgos y recomendaciones finales",    "#001f3f"),
    ]

    nav_card = dbc.Card([
        dbc.CardHeader(html.H5("Estructura del Dashboard",
                               className="mb-0 fw-bold", style={"color": "white",
                               "background": "#001f3f"})),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(_nav_btn(tid, titulo, desc, color), md=2, className="mb-3")
                for tid, titulo, desc, color in nav_items_fila1
            ]),
            dbc.Row([
                dbc.Col(_nav_btn(tid, titulo, desc, color), md=2, className="mb-3")
                for tid, titulo, desc, color in nav_items_fila2
            ] + [dbc.Col(md=6)]),  # relleno
        ], style={"background": "white"})
    ], className="shadow-sm border-0 mb-4", style={"borderRadius": "12px", "overflow": "hidden"})

    return dbc.Container([html.Br(), hero, cards, causas_card, nav_card, html.Br()], fluid=True)


# ── helpers ────────────────────────────────────────────────────────────────
def _card(titulo, texto):
    return dbc.Col(html.Div([
        html.Div(
            html.H6(titulo, className="fw-bold mb-0",
                    style={"color": "white", "fontSize": "0.85rem", "letterSpacing": "0.03em"}),
            className="px-3 py-2",
            style={"background": "#001f3f", "borderRadius": "8px 8px 0 0"}
        ),
        html.Div(
            html.P(texto, className="small mb-0",
                   style={"color": "#2c3e50", "lineHeight": "1.65"}),
            className="p-3",
            style={"background": "white", "borderRadius": "0 0 8px 8px",
                   "border": "1px solid #dee2e6", "borderTop": "none"}
        ),
    ], className="h-100", style={"borderRadius": "8px", "overflow": "hidden",
                                  "boxShadow": "0 2px 8px rgba(0,31,63,0.10)"}),
    md=3, className="mb-3")


def _nav_btn(tab_id, titulo, desc, color):
    """Card clickeable que actualiza el Store de navegación."""
    return html.Div(
        id={"type": "intro-nav", "tab": tab_id},
        n_clicks=0,
        children=html.Div([
            html.Div(
                html.P(titulo, className="fw-semibold text-center mb-0",
                       style={"color": "white", "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
                              "fontSize": "0.88rem"}),
                className="px-2 py-2",
                style={"background": "#001f3f", "borderRadius": "8px 8px 0 0"}
            ),
            html.Div(
                html.P(desc, className="text-center mb-0",
                       style={"fontSize": "0.72rem", "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
                              "color": "#2c3e50", "lineHeight": "1.4"}),
                className="p-2",
                style={"background": "white", "borderRadius": "0 0 8px 8px",
                       "border": "1px solid #dee2e6", "borderTop": "none"}
            ),
        ], className="h-100",
           style={"borderRadius": "8px", "overflow": "hidden", "cursor": "pointer",
                  "boxShadow": "0 2px 8px rgba(0,31,63,0.10)",
                  "transition": "transform 0.15s, box-shadow 0.15s"}),
    )
