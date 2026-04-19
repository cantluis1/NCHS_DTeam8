"""
tabs/geografico.py  —  Análisis Geográfico (mapa coroplético)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
from data.loader import load_df


def layout():
    df    = load_df()
    causas = sorted([c for c in df["Cause Name"].unique() if c != "All causes"]) + ["All causes"]
    años   = sorted(df["Year"].unique())

    header = html.Div([
        html.H2(" Análisis Geográfico", className="fw-bold mb-1", style={"color": "#001f3f"}),
        html.P("Mapa coroplético interactivo: distribución geográfica de la mortalidad en EE.UU.",
               className="text-muted lead"),
        html.Hr(style={"borderColor": "#d4f0b8"}),
    ], className="mb-4")

    controles = dbc.Card([
        dbc.CardBody(dbc.Row([
            dbc.Col([
                dbc.Label(" Causa de muerte", className="fw-semibold small"),
                dcc.Dropdown(
                    id="geo-causa",
                    options=[{"label": c, "value": c} for c in causas],
                    value="Unintentional injuries",
                    clearable=False,
                    style={"fontSize": "0.9rem"},
                ),
            ], md=5),
            dbc.Col([
                dbc.Label(" Año", className="fw-semibold small"),
                dcc.Slider(
                    id="geo-año",
                    min=int(min(años)), max=int(max(años)), step=1,
                    value=2017,
                    marks={int(y): str(y) for y in años if int(y) % 3 == 0 or y in [min(años), max(años)]},
                    tooltip={"placement": "bottom", "always_visible": True},
                ),
            ], md=5),
            dbc.Col([
                dbc.Label(" Escala", className="fw-semibold small"),
                dbc.RadioItems(
                    id="geo-escala",
                    options=[
                        {"label": " Reds", "value": "Reds"},
                        {"label": " Blues", "value": "Blues"},
                        {"label": " Plasma", "value": "Plasma"},
                    ],
                    value="Reds",
                    inline=True,
                    className="small mt-1",
                ),
            ], md=2),
        ]))
    ], className="shadow-sm border-0 mb-3", style={"borderRadius": "12px"})

    mapa = dbc.Card([
        dbc.CardHeader(html.H6("Mapa Coroplético — Tasa Ajustada por Estado", className="mb-0 fw-bold")),
        dbc.CardBody(dcc.Graph(id="geo-map", config={"displayModeBar": True},
                  style={"height": "460px"}), className="p-1"),
    ], className="shadow-sm border-0 mb-3", style={"borderRadius": "12px"})

    # Bubble chart controls
    burbuja_controles = dbc.Card([
        dbc.CardBody(dbc.Row([
            dbc.Col([
                dbc.Label("Causa:", className="fw-semibold small"),
                dcc.Dropdown(
                    id="geo-burbuja-causa",
                    options=[{"label": c, "value": c} for c in sorted([c for c in __import__('data.loader', fromlist=['load_df']).load_df()["Cause Name"].unique()])],
                    value="All causes",
                    clearable=False,
                    style={"fontSize": "0.9rem"},
                ),
            ], md=6),
            dbc.Col([
                dbc.Label("Año:", className="fw-semibold small"),
                dcc.Slider(
                    id="geo-burbuja-año",
                    min=1999, max=2017, step=1,
                    value=2017,
                    marks={y: str(y) for y in range(1999, 2018, 2)},
                    tooltip={"placement": "bottom", "always_visible": True},
                ),
            ], md=6),
        ]))
    ], className="shadow-sm border-0 mb-3", style={"borderRadius": "12px"})

    burbuja_card = dbc.Card([
        dbc.CardHeader(html.H6("Top 10 Estados — Tasa Ajustada vs Muertes Absolutas", className="mb-0 fw-bold")),
        dbc.CardBody(dcc.Graph(id="geo-scatter", config={"displayModeBar": True},
                               style={"height": "480px"})),
    ], className="shadow-sm border-0 mb-3", style={"borderRadius": "12px"})

    ranking_card = dbc.Card([
        dbc.CardHeader(html.H6("Ranking de estados — año seleccionado",
                               className="mb-0 fw-bold", style={"color": "white"})),
        dbc.CardBody(dcc.Graph(id="geo-bar", config={"displayModeBar": False},
                               style={"height": "300px"})),
    ], className="shadow-sm border-0 mb-4", style={"borderRadius": "12px"})

    return dbc.Container([html.Br(), header, controles, mapa, burbuja_controles, burbuja_card, ranking_card, html.Br()], fluid=True)


@callback(
    Output("geo-map",     "figure"),
    Output("geo-bar",     "figure"),
    Input("geo-causa", "value"),
    Input("geo-año",   "value"),
    Input("geo-escala","value"),
)
def update_geo(causa, año, escala):
    df  = load_df()
    dff = df[(df["Cause Name"] == causa) & (df["Year"] == año) &
             (df["State"] != "United States") & df["StateCode"].notna()].copy()

    # ── Mapa coroplético ──
    fig_map = px.choropleth(
        dff,
        locations="StateCode",
        locationmode="USA-states",
        color="Rate",
        color_continuous_scale=escala,
        scope="usa",
        hover_name="State",
        hover_data={"Rate": ":.1f", "Deaths": ":,", "StateCode": False},
        labels={"Rate": "Tasa/100k", "Deaths": "Muertes"},
        title=f"{causa} — {año}",
    )
    fig_map.update_layout(
        geo=dict(
            showlakes=True, lakecolor="rgb(180,220,240)",
            showocean=True, oceancolor="rgb(180,220,240)",
            showcoastlines=True, coastlinecolor="rgb(100,140,180)",
            showland=True, landcolor="rgb(240,235,220)",
            showcountries=True, countrycolor="rgb(180,180,180)",
            showframe=False,
            bgcolor="rgb(210,230,245)",
            projection_type="albers usa",
        ),
        coloraxis_colorbar=dict(title="Tasa/100k", thickness=14),
        margin=dict(l=0, r=0, t=50, b=0),
        font=dict(family="sans-serif", size=11, color="#3a3a5c"),
        paper_bgcolor="rgb(210,230,245)",
    )

    # ── Barplot top 15 estados ──
    top15 = dff.nlargest(15, "Rate").sort_values("Rate")
    colores = ["#f0b8b8" if s == "West Virginia" else "#c5b8f0" for s in top15["State"]]
    fig_bar = go.Figure(go.Bar(
        x=top15["Rate"], y=top15["State"], orientation="h",
        marker_color=colores,
        text=top15["Rate"].apply(lambda x: f"{x:.1f}"),
        textposition="outside",
        hovertemplate="%{y}: %{x:.1f}/100k<extra></extra>",
    ))
    fig_bar.update_layout(**_lbase(), xaxis_title="Tasa/100k",
                          title=f"Top 15 estados — {año}",
                          margin=dict(l=130, r=50, t=40, b=30))

    return fig_map, fig_bar


def _lbase():
    return dict(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="sans-serif", size=11, color="#3a3a5c"),
    )

@callback(
    Output("geo-scatter", "figure"),
    Input("geo-burbuja-causa", "value"),
    Input("geo-burbuja-año",   "value"),
)
def update_bubble(causa, año):
    import numpy as np
    df  = load_df()
    dff = df[(df["Cause Name"] == causa) & (df["Year"] == año) &
             (df["State"] != "United States") & df["StateCode"].notna()].copy()

    # Top 15 por tasa ajustada
    top15 = dff.nlargest(15, "Rate").reset_index(drop=True)
    top15["Ranking"] = top15.index + 1

    # Tamaño y color de burbuja por tasa
    max_rate = top15["Rate"].max()
    bubble_size = (top15["Rate"] / max_rate * 60 + 15).tolist()
    # Color escala navy gradient
    colors = [f"rgba(0, 31, 63, {0.35 + 0.65 * (r / max_rate):.2f})" for r in top15["Rate"]]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=top15["Rate"],
        y=top15["Ranking"],
        mode="markers+text",
        text=top15["State"].apply(lambda s: s.replace("West Virginia", "W. Virginia")),
        textposition="middle right",
        textfont=dict(size=10, color="#3a3a5c"),
        marker=dict(
            size=bubble_size,
            color=colors,
            line=dict(color="white", width=1.5),
            opacity=0.85,
        ),
        customdata=top15[["State", "Deaths", "Rate", "Ranking"]].values,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Ranking: #%{customdata[3]}<br>"
            "Tasa: %{customdata[2]:.1f}/100k<br>"
            "Muertes: %{customdata[1]:,}<extra></extra>"
        ),
    ))

    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="sans-serif", size=11, color="#3a3a5c"),
        title=f"Top 15 estados — Mayor tasa ajustada: {año}",
        xaxis=dict(title="Tasa ajustada por 100,000 habitantes", gridcolor="#f0f0f0", zeroline=False),
        yaxis=dict(
            title="Posición en el ranking",
            autorange="reversed",
            tickvals=list(range(1, 16)),
            gridcolor="#f0f0f0",
            zeroline=False,
        ),
        margin=dict(l=40, r=120, t=50, b=50),
    )

    # Anotación explicativa
    fig.add_annotation(
        text="<b>Cómo leer este gráfico:</b> Cada burbuja es un estado del Top 15 por mayor tasa ajustada. "
             "El eje X muestra la tasa ajustada por 100,000 hab., el eje Y indica la posición en el ranking "
             "(1 = mayor tasa), y el <b>tamaño de la burbuja</b> refleja la tasa ajustada — a mayor tasa, más grande y más oscura.",
        xref="paper", yref="paper",
        x=0, y=-0.18,
        showarrow=False,
        font=dict(size=10, color="#555"),
        align="left",
        xanchor="left",
    )

    return fig

