"""
tabs/modelos_adicionales.py — Sección 12: Introducción a la Comparación de Modelos
Traduce tab_intro_modelos.R → Dash / Python
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import dash_bootstrap_components as dbc
from dash import html

NAVY = "#1D3557"
AZUL = "#457B9D"


def layout():
    header = html.Div([
        html.Span("Sección 12 · Modelos Predictivos", style={
            "display": "inline-block",
            "background": "rgba(255,255,255,0.12)", "border": "1px solid rgba(255,255,255,0.2)",
            "color": "#a8d8f0", "fontSize": "0.72rem", "fontWeight": "700",
            "letterSpacing": "1.2px", "textTransform": "uppercase",
            "padding": "3px 10px", "borderRadius": "20px", "marginBottom": "10px"
        }),
        html.H3([html.I(className="fas fa-book-open me-2"),
                 "Comparación de Modelos Predictivos"],
                style={"color": "#fff", "fontWeight": "800", "margin": "0 0 5px"}),
        html.P([
            "Validación empírica del ARIMA frente a ETS y Regresión Lineal. ",
            "Unintentional Injuries – West Virginia (1999–2017)."
        ], style={"color": "rgba(255,255,255,0.72)", "fontSize": "0.855rem",
                  "lineHeight": "1.5", "margin": "0", "maxWidth": "760px"}),
    ], style={
        "background": "linear-gradient(135deg, #0f2340 0%, #1D3557 60%, #2a4a72 100%)",
        "borderRadius": "14px", "padding": "22px 28px", "marginBottom": "20px",
        "boxShadow": "0 4px 20px rgba(29,53,87,0.15)"
    })

    cuerpo = html.Div([
        html.P([
            "El modelo ", html.Strong("ARIMA(0,1,0) with drift"),
            " fue implementado en la sección anterior como estándar metodológico ",
            "en epidemiología de series de mortalidad. Sin embargo, la selección ",
            "de un modelo predictivo requiere validación empírica frente a alternativas."
        ], style={"fontSize": "0.92rem", "lineHeight": "1.85", "color": "#2c2c2c", "marginBottom": "12px"}),
        html.P([
            "En esta sección se implementan dos modelos adicionales, ",
            html.Strong(" ETS (Suavizamiento Exponencial de Holt)"),
            " y ", html.Strong(" Regresión Lineal con tendencia temporal"),
            ", y se realiza una comparación sistemática que justifica la elección final ",
            "mediante criterios de información, validación cruzada de series de tiempo ",
            "y diagnóstico de residuos."
        ], style={"fontSize": "0.92rem", "lineHeight": "1.85", "color": "#2c2c2c", "marginBottom": "12px"}),
        html.P([
            "El foco es la serie de ",
            html.Strong("Unintentional Injuries – West Virginia"),
            ", por ser la causa de mayor crecimiento en el último año y la de mayor ",
            "relevancia para política pública dentro del eje central del caso de estudio."
        ], style={"fontSize": "0.92rem", "lineHeight": "1.85", "color": "#2c2c2c", "marginBottom": "0"}),
    ], style={
        "background": "#fff", "border": "1px solid #dee2e6", "borderTop": "none",
        "borderRadius": "0 0 10px 10px", "padding": "26px 28px 22px", "marginBottom": "20px"
    })

    def tarjeta(seccion, icono, titulo, descripcion, tab_destino, label_btn):
        return html.Div([
            html.P(seccion, style={
                "margin": "0 0 4px", "fontSize": "0.68rem", "fontWeight": "700",
                "textTransform": "uppercase", "letterSpacing": "0.9px", "color": NAVY
            }),
            html.P([html.I(className=f"fas fa-{icono} me-2"), titulo],
                   style={"margin": "0 0 6px", "fontSize": "0.97rem", "fontWeight": "700", "color": NAVY}),
            html.P(descripcion, style={"margin": "0 0 14px", "fontSize": "0.82rem",
                                       "color": "#555", "lineHeight": "1.55"}),
            html.Button([
                html.I(className=f"fas fa-{icono} me-2"),
                html.Span(label_btn)
            ],
            id={"type": "intro-nav", "tab": tab_destino},
            n_clicks=0,
            style={
                "background": NAVY, "color": "#fff", "borderRadius": "6px",
                "padding": "6px 14px", "fontSize": "0.8rem", "fontWeight": "600",
                "border": "none", "cursor": "pointer"
            })
        ], style={
            "background": "#fff", "borderRadius": "8px", "padding": "18px 20px",
            "border": "1px solid #dee2e6", "borderLeft": f"4px solid {NAVY}",
            "boxShadow": "0 1px 4px rgba(0,0,0,0.05)"
        })

    grid = html.Div([
        dbc.Row([
            dbc.Col(tarjeta(
                "Sección 13", "wave-square", "Modelo ETS",
                "Suavizamiento exponencial con selección automática por AICc. Componentes Error, Trend y Seasonality.",
                "tab-ets", "Modelo ETS"
            ), md=6, className="mb-3"),
            dbc.Col(tarjeta(
                "Sección 14", "ruler", "Regresión Lineal",
                "Benchmark OLS con tendencia temporal. ŷₜ = β₀ + β₁·t + εₜ. Modelo de referencia mínimo.",
                "tab-regresion", "Regresión Lineal"
            ), md=6, className="mb-3"),
        ]),
        dbc.Row([
            dbc.Col(tarjeta(
                "Secciones 15–16", "scale-balanced", "Comparación y Selección del Modelo Óptimo",
                "Evaluación sistemática mediante AIC/AICc/BIC, diagnóstico de residuos (Ljung-Box) "
                "y validación cruzada de series de tiempo (tsCV). Justificación del modelo final.",
                "tab-comparacion", "Comparación de Modelos"
            ), md=12, className="mb-3"),
        ])
    ])

    return dbc.Container([
        html.Br(),
        header,
        cuerpo,
        grid,
        html.Br(),
    ], fluid=True)
