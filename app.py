"""
app.py — Dashboard NCHS: Leading Causes of Death in the United States
Arquitectura modular: cada pestaña es un archivo independiente en /tabs.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html

# ── Importar layouts de pestañas ─────────────────────────────────────────
from tabs import (
    introduccion,
    marco_teorico,
    metodologia,
    evolucion,
    ranking,
    despair,
    geografico,
    west_virginia,
    metricas_modelos,
    modelos_adicionales,
    modelo_ets,
    regresion_lineal,
    comparacion_modelos,
    limitaciones,
    conclusiones,
)

# ── App ───────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.LITERA, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True,
    title="NCHS Dashboard · Leading Causes of Death",
)
server = app.server

# ── Configuración de pestañas ─────────────────────────────────────────────
TABS_CONFIG = [
    ("tab-intro",           "Introducción",              introduccion),
    ("tab-marco",           "Marco Teórico",             marco_teorico),
    ("tab-metodologia",     "Metodología",               metodologia),
    ("tab-evolucion",       "Evolución de Tasas",        evolucion),
    ("tab-ranking",         "Ranking por Año",           ranking),
    ("tab-despair",         "Deaths of Despair",         despair),
    ("tab-geo",             "Análisis Geográfico",       geografico),
    ("tab-wv",              "Caso: West Virginia",       west_virginia),
    ("tab-metricas",        "Métricas de Modelos",       metricas_modelos),
    ("tab-mod-adicionales", "Modelos Adicionales",       modelos_adicionales),
    ("tab-ets",             "Modelo ETS",                modelo_ets),
    ("tab-regresion",       "Regresión Lineal",          regresion_lineal),
    ("tab-comparacion",     "Comparación",               comparacion_modelos),
    ("tab-limit",           "Limitaciones",              limitaciones),
    ("tab-conclu",          "Conclusiones",              conclusiones),
]

# Separadores visuales de sección en la barra de tabs
SEPARADORES = {
    "tab-evolucion":       "ANÁLISIS EXPLORATORIO",
    "tab-mod-adicionales": "MODELOS ADICIONALES",
    "tab-limit":           "CIERRE",
}


def _build_nav():
    """Sidebar de navegación tipo Shiny."""
    items = []
    for tab_id, label, _ in TABS_CONFIG:
        # Separador de sección
        if tab_id in SEPARADORES:
            items.append(html.Div(
                SEPARADORES[tab_id],
                className="px-3 pt-3 pb-1",
                style={"fontSize": "0.68rem", "letterSpacing": "0.08em",
                       "color": "#8888aa", "fontWeight": "700", "textTransform": "uppercase"}
            ))
        items.append(
            html.Div(
                label,
                id={"type": "nav-item", "tab": tab_id},
                n_clicks=0,
                className="nav-link-item px-3 py-2",
                style={"cursor": "pointer", "fontSize": "0.88rem", "borderRadius": "6px",
                       "transition": "background 0.15s", "color": "#dde0f0"},
            )
        )
    return items


app.layout = html.Div([
    # ── Sidebar ──────────────────────────────────────────────────────────
    html.Div([
        # Logo / título
        html.Div([
            html.Img(
                src="https://flagcdn.com/w40/us.png",
                width="36", height="24",
                style={"borderRadius": "3px", "objectFit": "cover",
                       "flexShrink": "0", "boxShadow": "0 1px 3px rgba(0,0,0,0.3)"}
            ),
            html.Div([
                html.Div("NCHS Dashboard", className="fw-bold",
                         style={"fontSize": "0.95rem", "color": "white", "lineHeight": "1.2"}),
                html.Div("Leading Causes of Death",
                         style={"fontSize": "0.68rem", "color": "#8888aa"}),
            ]),
        ], className="d-flex align-items-center gap-2 px-3 py-3 mb-2",
           style={"borderBottom": "1px solid #3a3a5c"}),

        # Items de navegación
        html.Div(_build_nav(), id="nav-container"),

        # Créditos
        html.Div([
            html.Hr(style={"borderColor": "#3a3a5c"}),
            html.Small("NCHS / CDC · 1999–2017", className="text-muted px-3",
                       style={"fontSize": "0.68rem"}),
        ], className="mt-auto pb-2"),
    ], id="sidebar",
       style={
           "width": "220px", "minWidth": "220px", "height": "100vh",
           "background": "#1e1e2e", "overflowY": "auto",
           "display": "flex", "flexDirection": "column",
           "position": "fixed", "top": 0, "left": 0, "zIndex": 100,
       }),

    # ── Contenido principal ───────────────────────────────────────────────
    html.Div([
        # Store para la pestaña activa
        dcc.Store(id="active-tab", data="tab-intro"),

        # Contenido dinámico
        html.Div(id="main-content",
                 style={"minHeight": "100vh", "backgroundColor": "#fafafa"}),
    ], style={"marginLeft": "220px", "flex": 1}),

], style={"display": "flex", "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"})


# ── Callback: navegación ──────────────────────────────────────────────────
@app.callback(
    Output("main-content", "children"),
    Output("nav-container", "children"),
    Input("active-tab", "data"),
)
def render_content(active_tab):
    tab_map = {tid: mod for tid, _, mod in TABS_CONFIG}
    modulo  = tab_map.get(active_tab, introduccion)
    content = modulo.layout()

    # Reconstruir nav con ítem activo destacado
    items = []
    for tab_id, label, _ in TABS_CONFIG:
        if tab_id in SEPARADORES:
            items.append(html.Div(
                SEPARADORES[tab_id],
                className="px-3 pt-3 pb-1",
                style={"fontSize": "0.68rem", "letterSpacing": "0.08em",
                       "color": "#8888aa", "fontWeight": "700", "textTransform": "uppercase"}
            ))
        is_active = (tab_id == active_tab)
        items.append(
            html.Div(
                label,
                id={"type": "nav-item", "tab": tab_id},
                n_clicks=0,
                className="nav-link-item px-3 py-2",
                style={
                    "cursor": "pointer", "fontSize": "0.88rem", "borderRadius": "6px",
                    "background": "#5a4fcf" if is_active else "transparent",
                    "color": "white" if is_active else "#dde0f0",
                    "fontWeight": "600" if is_active else "400",
                    "transition": "background 0.15s",
                },
            )
        )
    return content, items


# Callback para capturar clicks en items de navegación (sidebar + intro cards)
app.clientside_callback(
    """
    function(sidebar_clicks, intro_clicks, current_tab) {
        const ctx = dash_clientside.callback_context;
        if (!ctx || !ctx.triggered || ctx.triggered.length === 0) {
            return current_tab;
        }
        const first = ctx.triggered[0];
        if (!first || first.value === null || first.value === 0) {
            return current_tab;
        }
        const triggered_id = first.prop_id;
        if (!triggered_id || triggered_id === 'active-tab.data') {
            return current_tab;
        }
        try {
            const id_obj = JSON.parse(triggered_id.split('.')[0]);
            if (id_obj && id_obj.tab) {
                return id_obj.tab;
            }
        } catch(e) {}
        return current_tab;
    }
    """,
    Output("active-tab", "data"),
    Input({"type": "nav-item",   "tab": dash.ALL}, "n_clicks"),
    Input({"type": "intro-nav",  "tab": dash.ALL}, "n_clicks"),
    Input("active-tab", "data"),
)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
