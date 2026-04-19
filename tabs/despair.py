"""
tabs/despair.py  —  Deaths of Despair
Análisis de suicidio y lesiones no intencionales (opioides/sobredosis).
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
    df  = load_df()
    estados = sorted([s for s in df["State"].unique() if s != "United States"])

    header = html.Div([
        html.H2("Deaths of Despair", className="fw-bold mb-1", style={"color": "#001f3f"}),
        html.P("Suicidio y lesiones no intencionales (sobredosis/accidentes): la crisis silenciosa de EE.UU.",
               className="text-muted lead"),
        html.Hr(style={"borderColor": "#f0b8b8"}),
    ], className="mb-4")

    concepto = dbc.Alert([
        html.Strong("¿Qué son las Deaths of Despair? "),
        "Término acuñado por los economistas Anne Case y Angus Deaton en 2015 para describir "
        "el aumento de muertes por suicidio, sobredosis de drogas/alcohol y enfermedades "
        "hepáticas alcohólicas en adultos sin educación universitaria. En este dataset las "
        "aproximamos con ",
        html.Strong("Suicide + Unintentional injuries"),
        " (que incluye la mayor parte de sobredosis).",
    ], color="light", className="border mb-4",
       style={"borderLeft": "4px solid #f0b8b8 !important", "borderRadius": "8px"})

    # KPIs nacionales 2017
    nat  = load_df()
    nat  = nat[nat["State"] == "United States"]
    sui17 = nat[(nat["Cause Name"] == "Suicide") & (nat["Year"] == 2017)]["Rate"].values
    inj17 = nat[(nat["Cause Name"] == "Unintentional injuries") & (nat["Year"] == 2017)]["Rate"].values
    sui99 = nat[(nat["Cause Name"] == "Suicide") & (nat["Year"] == 1999)]["Rate"].values
    inj99 = nat[(nat["Cause Name"] == "Unintentional injuries") & (nat["Year"] == 1999)]["Rate"].values

    kpis = dbc.Row([
        _kpi("", "Tasa suicidio 2017",        f"{sui17[0]:.1f}", "por 100,000", "#001f3f"),
        _kpi("", "Cambio suicidio 99→17",     f"+{((sui17[0]-sui99[0])/sui99[0]*100):.0f}%", "vs 1999", "#001f3f"),
        _kpi("", "Tasa lesiones no int. 2017", f"{inj17[0]:.1f}", "por 100,000", "#001f3f"),
        _kpi("", "Cambio lesiones 99→17",      f"+{((inj17[0]-inj99[0])/inj99[0]*100):.0f}%", "vs 1999", "#001f3f"),
    ], className="mb-4")

    grafico_nac = dbc.Card([
        dbc.CardHeader(html.H6("Evolución Nacional — Ambas causas (1999–2017)",
                               className="mb-0 fw-bold", style={"color": "white"})),
        dbc.CardBody(dcc.Graph(id="despair-nac", config={"displayModeBar": False},
                               style={"height": "300px"})),
    ], className="shadow-sm border-0 mb-3", style={"borderRadius": "12px"})

    controles = dbc.Card([
        dbc.CardBody(dbc.Row([
            dbc.Col([
                dbc.Label("Comparar estados (máx. 8)", className="fw-semibold small"),
                dcc.Dropdown(
                    id="despair-estados",
                    options=[{"label": e, "value": e} for e in estados],
                    value=["West Virginia", "New Hampshire", "Ohio", "Kentucky", "Mississippi"],
                    multi=True,
                    style={"fontSize": "0.9rem"},
                ),
            ], md=8),
            dbc.Col([
                dbc.Label("Causa", className="fw-semibold small"),
                dbc.RadioItems(
                    id="despair-causa",
                    options=[
                        {"label": " Unintentional injuries", "value": "Unintentional injuries"},
                        {"label": " Suicide",                "value": "Suicide"},
                    ],
                    value="Unintentional injuries",
                    className="small mt-1",
                ),
            ], md=4),
        ]))
    ], className="shadow-sm border-0 mb-3", style={"borderRadius": "12px"})

    grafico_est = dbc.Card([
        dbc.CardHeader(html.H6("Comparativa por Estado",
                               className="mb-0 fw-bold", style={"color": "white"})),
        dbc.CardBody(dcc.Graph(id="despair-estados-graph", config={"displayModeBar": False},
                               style={"height": "340px"})),
    ], className="shadow-sm border-0 mb-4", style={"borderRadius": "12px"})

    contexto = dbc.Card([
        dbc.CardHeader(html.H5("Contexto Socioeconómico", className="mb-0 fw-bold",
                               style={"color": "white"})),
        dbc.CardBody(dbc.Row([
            dbc.Col(_dato("", "Crisis de Opioides",
                "A partir de 2010, la prescripción masiva de opioides (OxyContin, Vicodin) "
                "disparó las sobredosis en comunidades rurales. West Virginia, Ohio y Kentucky "
                "lideran las tasas más altas del país."), md=4),
            dbc.Col(_dato("", "Desindustrialización",
                "El colapso de la industria minera y manufacturera en los estados del 'Rust Belt' "
                "y Appalachia generó desempleo estructural, pérdida de identidad y desesperanza "
                "en comunidades que antes dependían de esas industrias."), md=4),
            dbc.Col(_dato("", "Desigualdad en Acceso a Salud",
                "Los estados con menores tasas de cobertura médica y mayor proporción de población "
                "rural presentan tasas más altas de Deaths of Despair, reflejando barreras de "
                "acceso a tratamiento de adicciones y salud mental."), md=4),
        ]))
    ], className="shadow-sm border-0 mb-4", style={"borderRadius": "12px"})

    return dbc.Container([
        html.Br(), header, concepto, kpis,
        grafico_nac, controles, grafico_est, contexto, html.Br()
    ], fluid=True)


@callback(Output("despair-nac", "figure"), Input("despair-causa", "value"))
def update_nac(causa_sel):
    df  = load_df()
    nat = df[(df["State"] == "United States") &
             (df["Cause Name"].isin(["Suicide", "Unintentional injuries"]))].sort_values("Year")
    fig = go.Figure()
    for causa in ["Suicide", "Unintentional injuries"]:
        sub = nat[nat["Cause Name"] == causa]
        fig.add_trace(go.Scatter(
            x=sub["Year"], y=sub["Rate"],
            mode="lines+markers", name=causa,
            line=dict(color=CAUSA_COLORES.get(causa, "#aaa"), width=2.5),
            marker=dict(size=6),
            fill="tozeroy", fillcolor='rgba(90,79,207,0.12)',
        ))
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="sans-serif", size=11, color="#3a3a5c"),
        margin=dict(l=40, r=20, t=20, b=30),
        xaxis=dict(title="Año", dtick=2, gridcolor="#f0f0f0"),
        yaxis=dict(title="Tasa/100k", gridcolor="#f0f0f0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    return fig


@callback(
    Output("despair-estados-graph", "figure"),
    Input("despair-estados", "value"),
    Input("despair-causa", "value"),
)
def update_estados(estados, causa):
    df  = load_df()
    if not estados:
        estados = ["West Virginia"]
    estados = estados[:8]
    dff = df[(df["State"].isin(estados)) & (df["Cause Name"] == causa)].sort_values("Year")

    paleta = ["#f0b8b8","#c5b8f0","#fde8b0","#b8d8f0",
              "#f7c5e0","#d4f0b8","#f0d4b8","#b8f0e8"]
    fig = go.Figure()
    for i, estado in enumerate(estados):
        sub = dff[dff["State"] == estado]
        fig.add_trace(go.Scatter(
            x=sub["Year"], y=sub["Rate"],
            mode="lines+markers", name=estado,
            line=dict(color=paleta[i % len(paleta)], width=2),
            marker=dict(size=5),
            hovertemplate=f"<b>{estado}</b><br>%{{x}}: %{{y:.1f}}/100k<extra></extra>",
        ))
    fig.update_layout(
        title=f"{causa} — Comparativa por estado",
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="sans-serif", size=11, color="#3a3a5c"),
        margin=dict(l=40, r=20, t=40, b=30),
        xaxis=dict(title="Año", dtick=2, gridcolor="#f0f0f0"),
        yaxis=dict(title="Tasa/100k", gridcolor="#f0f0f0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    return fig


def _kpi(icon, titulo, valor, sub, bg):
    return dbc.Col(dbc.Card([dbc.CardBody([
        html.Div(icon, className="fs-2 mb-1"),
        html.H6(titulo, className="small", style={"color": "white"}),
        html.H4(valor, className="fw-bold mb-0", style={"color": "white"}),
        html.Small(sub, style={"color": "white"}),
    ], className="text-center")], className="h-100 shadow-sm border-0",
        style={"background": bg, "borderRadius": "12px"}), md=3, className="mb-3")


def _dato(icon, titulo, desc):
    return html.Div([
        html.Div(icon + " " + titulo, className="fw-bold mb-2 small", style={"color": "white"}),
        html.P(desc, className="text-muted small mb-0"),
    ])
