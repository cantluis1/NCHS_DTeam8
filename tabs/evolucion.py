"""
tabs/evolucion.py  —  Evolución de Tasas de Mortalidad
Serie temporal interactiva con filtros por causa y estado.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
from data.loader import load_df, CAUSA_COLORES


def layout():
    df = load_df()
    causas    = sorted([c for c in df["Cause Name"].unique() if c != "All causes"])
    estados   = ["United States"] + sorted([s for s in df["State"].unique() if s != "United States"])

    header = html.Div([
        html.H2(" Evolución de Tasas de Mortalidad",
                className="fw-bold mb-1", style={"color": "#001f3f"}),
        html.P("Serie temporal de tasas ajustadas por año (por 100,000 habitantes), 1999–2017.",
               className="text-muted lead"),
        html.Hr(style={"borderColor": "#b8e8c5"}),
    ], className="mb-4")

    controles = dbc.Card([
        dbc.CardBody(dbc.Row([
            dbc.Col([
                dbc.Label(" Estado / Nivel Nacional", className="fw-semibold small"),
                dcc.Dropdown(
                    id="evol-estado",
                    options=[{"label": e, "value": e} for e in estados],
                    value="United States",
                    clearable=False,
                    style={"fontSize": "0.9rem"},
                ),
            ], md=5),
            dbc.Col([
                dbc.Label(" Causas a mostrar", className="fw-semibold small"),
                dcc.Dropdown(
                    id="evol-causas",
                    options=[{"label": c, "value": c} for c in causas],
                    value=["Heart disease", "Cancer", "Stroke", "Suicide"],
                    multi=True,
                    style={"fontSize": "0.9rem"},
                ),
            ], md=5),
            dbc.Col([
                dbc.Label(" Métrica", className="fw-semibold small"),
                dbc.RadioItems(
                    id="evol-metrica",
                    options=[
                        {"label": " Tasa ajustada", "value": "Rate"},
                        {"label": " Muertes absolutas", "value": "Deaths"},
                    ],
                    value="Rate",
                    inline=True,
                    className="small mt-1",
                ),
            ], md=2),
        ]))
    ], className="shadow-sm border-0 mb-3", style={"borderRadius": "12px"})

    grafico = dbc.Card([
        dbc.CardHeader(html.H6("Evolución de Tasas de Mortalidad", className="mb-0 fw-bold")),
        dbc.CardBody(dcc.Graph(id="evol-graph", config={"displayModeBar": True},
                  style={"height": "440px"}), className="p-2"),
    ], className="shadow-sm border-0 mb-3", style={"borderRadius": "12px"})

    anotaciones = dbc.Card([
        dbc.CardHeader(html.H6(" Eventos Históricos Clave", className="mb-0 fw-bold",
                               style={"color": "white"})),
        dbc.CardBody(dbc.Row([
            _evento("2001", "Anthrax + post-9/11", "Pico en influenza y enfermedades respiratorias.", "#fde8b0"),
            _evento("2008", "Gran Recesión",        "Aumento de suicidios y lesiones no intencionales.", "#f0b8b8"),
            _evento("2012", "Crisis opioides",      "Escalada de muertes por sobredosis en EE.UU.", "#f7c5e0"),
            _evento("2017", "Fin del dataset",      "Mayor tasa histórica de lesiones no intencionales.", "#c5b8f0"),
        ]))
    ], className="shadow-sm border-0 mb-4", style={"borderRadius": "12px"})

    return dbc.Container([html.Br(), header, controles, grafico, anotaciones, html.Br()], fluid=True)


@callback(
    Output("evol-graph", "figure"),
    Input("evol-estado", "value"),
    Input("evol-causas", "value"),
    Input("evol-metrica", "value"),
)
def update_evol(estado, causas, metrica):
    df = load_df()
    if not causas:
        causas = ["Heart disease"]

    dff = df[(df["State"] == estado) & (df["Cause Name"].isin(causas))]
    dff = dff.sort_values("Year")

    y_label = "Tasa ajustada por año (por 100k)" if metrica == "Rate" else "Número de muertes"
    titulo  = f"Evolución en {estado} — {y_label}"

    fig = go.Figure()
    for causa in causas:
        sub = dff[dff["Cause Name"] == causa]
        color = CAUSA_COLORES.get(causa, "#aaa")
        fig.add_trace(go.Scatter(
            x=sub["Year"], y=sub[metrica],
            mode="lines+markers",
            name=causa,
            line=dict(color=color, width=2.5),
            marker=dict(size=6, color=color),
            hovertemplate=f"<b>{causa}</b><br>Año: %{{x}}<br>{y_label}: %{{y:,.1f}}<extra></extra>",
        ))

    # Línea vertical: crisis opioides 2012
    fig.add_vline(x=2012, line_dash="dot", line_color="#aaa", line_width=1,
                  annotation_text="Crisis opioides", annotation_position="top right",
                  annotation_font_size=10, annotation_font_color="#888")

    fig.update_layout(
        title=titulo,
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="sans-serif", size=12, color="#3a3a5c"),
        margin=dict(l=50, r=30, t=50, b=40),
        xaxis=dict(title="Año", dtick=2, gridcolor="#f0f0f0"),
        yaxis=dict(title=y_label, gridcolor="#f0f0f0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    return fig


def _evento(año, titulo, desc, color):
    return dbc.Col(html.Div([
        html.Span(año, className="badge px-2 py-1 me-2",
                  style={"background": color, "color": "#3a3a5c", "borderRadius": "6px"}),
        html.Strong(titulo + ": ", className="small"),
        html.Span(desc, className="text-muted small"),
    ], className="mb-2"))
