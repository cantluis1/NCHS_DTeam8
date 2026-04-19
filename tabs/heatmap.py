"""
tabs/heatmap.py  —  Heatmap de Tasas por Estado y Año
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
from data.loader import load_df


def layout():
    df    = load_df()
    causas = sorted([c for c in df["Cause Name"].unique() if c != "All causes"])

    header = html.Div([
        html.H2("🔲 Heatmap de Mortalidad", className="fw-bold mb-1", style={"color": "#3a3a5c"}),
        html.P("Tasa ajustada por edad: estados (filas) × años (columnas). Selecciona la causa.",
               className="text-muted lead"),
        html.Hr(style={"borderColor": "#b8d8f0"}),
    ], className="mb-4")

    control = dbc.Card([
        dbc.CardBody(dbc.Row([
            dbc.Col([
                dbc.Label("🦠 Causa de muerte", className="fw-semibold small"),
                dcc.Dropdown(
                    id="heat-causa",
                    options=[{"label": c, "value": c} for c in causas],
                    value="Unintentional injuries",
                    clearable=False,
                    style={"fontSize": "0.9rem"},
                ),
            ], md=5),
            dbc.Col([
                dbc.Label("📐 Escala de color", className="fw-semibold small"),
                dbc.RadioItems(
                    id="heat-escala",
                    options=[
                        {"label": " Secuencial (Reds)", "value": "Reds"},
                        {"label": " Divergente (RdBu_r)", "value": "RdBu_r"},
                        {"label": " Viridis", "value": "Viridis"},
                    ],
                    value="Reds",
                    inline=True,
                    className="small mt-1",
                ),
            ], md=5),
            dbc.Col([
                dbc.Label("🗺️ Excluir 'United States'", className="fw-semibold small"),
                dbc.Switch(id="heat-excluir-us", value=True, className="mt-2"),
            ], md=2),
        ]))
    ], className="shadow-sm border-0 mb-3", style={"borderRadius": "12px"})

    heatmap_card = dbc.Card(
        dcc.Graph(id="heat-graph", config={"displayModeBar": True},
                  style={"height": "620px"}),
        className="shadow-sm border-0 p-2 mb-3", style={"borderRadius": "12px"}
    )

    fila_extras = dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader(html.H6("📊 Top 10 estados — tasa promedio",
                                   className="mb-0 fw-bold", style={"color": "#3a3a5c"})),
            dbc.CardBody(dcc.Graph(id="heat-top10", config={"displayModeBar": False},
                                   style={"height": "300px"})),
        ], className="shadow-sm border-0", style={"borderRadius": "12px"}), md=6),
        dbc.Col(dbc.Card([
            dbc.CardHeader(html.H6("📉 Bottom 10 estados — tasa promedio",
                                   className="mb-0 fw-bold", style={"color": "#3a3a5c"})),
            dbc.CardBody(dcc.Graph(id="heat-bot10", config={"displayModeBar": False},
                                   style={"height": "300px"})),
        ], className="shadow-sm border-0", style={"borderRadius": "12px"}), md=6),
    ], className="mb-4")

    return dbc.Container([html.Br(), header, control, heatmap_card, fila_extras, html.Br()], fluid=True)


@callback(
    Output("heat-graph", "figure"),
    Output("heat-top10", "figure"),
    Output("heat-bot10", "figure"),
    Input("heat-causa", "value"),
    Input("heat-escala", "value"),
    Input("heat-excluir-us", "value"),
)
def update_heat(causa, escala, excluir_us):
    df = load_df()
    dff = df[df["Cause Name"] == causa].copy()
    if excluir_us:
        dff = dff[dff["State"] != "United States"]

    pivot = dff.pivot_table(index="State", columns="Year", values="Rate", aggfunc="mean")
    pivot = pivot.sort_values(pivot.columns[-1], ascending=False)

    # ── Heatmap ──
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[str(c) for c in pivot.columns],
        y=pivot.index.tolist(),
        colorscale=escala,
        hoverongaps=False,
        hovertemplate="<b>%{y}</b><br>Año %{x}<br>Tasa: %{z:.1f}<extra></extra>",
        colorbar=dict(title="Tasa/100k", thickness=14),
    ))
    fig.update_layout(
        title=f"Heatmap: {causa} — Tasa ajustada por estado y año",
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="sans-serif", size=10, color="#3a3a5c"),
        margin=dict(l=140, r=60, t=50, b=50),
        xaxis=dict(title="Año", tickangle=-45),
        yaxis=dict(title=""),
    )

    # ── Top / Bottom 10 ──
    promedios = pivot.mean(axis=1).reset_index()
    promedios.columns = ["State", "AvgRate"]
    promedios = promedios.sort_values("AvgRate", ascending=False)

    top10 = promedios.head(10)
    bot10 = promedios.tail(10).sort_values("AvgRate")

    fig_top = go.Figure(go.Bar(
        x=top10["AvgRate"], y=top10["State"], orientation="h",
        marker_color="#f0b8b8",
        text=top10["AvgRate"].apply(lambda x: f"{x:.1f}"),
        textposition="outside",
        hovertemplate="%{y}: %{x:.1f}/100k<extra></extra>",
    ))
    fig_top.update_layout(**_lbase(), xaxis_title="Tasa promedio/100k", margin=dict(l=130, r=50, t=20, b=30))

    fig_bot = go.Figure(go.Bar(
        x=bot10["AvgRate"], y=bot10["State"], orientation="h",
        marker_color="#b8e8c5",
        text=bot10["AvgRate"].apply(lambda x: f"{x:.1f}"),
        textposition="outside",
        hovertemplate="%{y}: %{x:.1f}/100k<extra></extra>",
    ))
    fig_bot.update_layout(**_lbase(), xaxis_title="Tasa promedio/100k", margin=dict(l=130, r=50, t=20, b=30))

    return fig, fig_top, fig_bot


def _lbase():
    return dict(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="sans-serif", size=10, color="#3a3a5c"),
    )
