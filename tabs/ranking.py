"""
tabs/ranking.py  —  Ranking de Causas por Año
Bar chart animado + slider de año.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback, dash_table
import plotly.graph_objects as go
import pandas as pd
from data.loader import load_df, CAUSA_COLORES


def layout():
    df  = load_df()
    nat = df[(df["State"] == "United States") & (df["Cause Name"] != "All causes")]
    años = sorted(nat["Year"].unique())

    header = html.Div([
        html.H2(" Ranking de Causas por Año",
                className="fw-bold mb-1", style={"color": "#001f3f"}),
        html.P("Ordenamiento de las 10 causas líderes según tasa ajustada por edad. Mueve el slider.",
               className="text-muted lead"),
        html.Hr(style={"borderColor": "#fde8b0"}),
    ], className="mb-4")

    slider_card = dbc.Card([
        dbc.CardBody([
            dbc.Label(" Selecciona el Año", className="fw-semibold"),
            dcc.Slider(
                id="rank-año",
                min=int(min(años)), max=int(max(años)), step=1,
                value=2017,
                marks={int(y): {"label": str(y), "style": {"fontSize": "0.7rem"}} for y in años},
                tooltip={"placement": "bottom", "always_visible": True},
            ),
        ])
    ], className="shadow-sm border-0 mb-3", style={"borderRadius": "12px"})

    fila_graficos = dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader(html.H6("Ranking de causas", className="mb-0 fw-bold")),
            dbc.CardBody(dcc.Graph(id="rank-bar", config={"displayModeBar": False},
                      style={"height": "400px"}), className="p-2"),
        ], className="shadow-sm border-0", style={"borderRadius": "12px"}
        ), md=7, className="mb-3"),
        dbc.Col([
            dbc.Card(html.Div(id="rank-tabla-div"), className="shadow-sm border-0 p-3",
                     style={"borderRadius": "12px"}),
        ], md=5, className="mb-3"),
    ])

    evolucion_top3 = dbc.Card([
        dbc.CardHeader(html.H6(" Evolución histórica — Top 3 causas",
                               className="mb-0 fw-bold", style={"color": "white"})),
        dbc.CardBody(dcc.Graph(id="rank-top3-evol", config={"displayModeBar": False},
                               style={"height": "260px"})),
    ], className="shadow-sm border-0 mb-4", style={"borderRadius": "12px"})

    return dbc.Container([
        html.Br(), header, slider_card, fila_graficos, evolucion_top3, html.Br()
    ], fluid=True)


@callback(
    Output("rank-bar", "figure"),
    Output("rank-tabla-div", "children"),
    Output("rank-top3-evol", "figure"),
    Input("rank-año", "value"),
)
def update_ranking(año):
    df  = load_df()
    nat = df[(df["State"] == "United States") & (df["Cause Name"] != "All causes")]
    año_df = nat[nat["Year"] == año].sort_values("Rate", ascending=True)

    colores = "#001f3f"

    # ── Bar chart horizontal ──
    fig_bar = go.Figure(go.Bar(
        x=año_df["Rate"],
        y=año_df["Cause Name"],
        orientation="h",
        marker_color=colores,
        text=año_df["Rate"].apply(lambda x: f"{x:.1f}"),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Tasa: %{x:.1f} por 100k<extra></extra>",
    ))
    fig_bar.update_layout(
        title=f"Ranking de causas — {año}",
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="sans-serif", size=11, color="#3a3a5c"),
        margin=dict(l=160, r=60, t=50, b=40),
        xaxis=dict(title="Tasa ajustada por 100,000", gridcolor="#f0f0f0"),
        yaxis=dict(title=""),
    )

    # ── Tabla de ranking ──
    tabla_df = año_df.sort_values("Rate", ascending=False).reset_index(drop=True)
    tabla_df.index += 1
    _recs = [{"index_col": i+1, "Causa": r["Cause Name"],
               "Tasa/100k": round(float(r["Rate"]),1), "Muertes": int(r["Deaths"])}
              for i, r in enumerate(tabla_df[["Cause Name","Rate","Deaths"]].to_dict("records"))]
    tabla = dash_table.DataTable(
        data=_recs,
        columns=[
            {"name": "#",         "id": "index_col"},
            {"name": "Causa",     "id": "Causa"},
            {"name": "Tasa/100k", "id": "Tasa/100k", "type": "numeric",
             "format": {"specifier": ".1f"}},
            {"name": "Muertes",   "id": "Muertes",   "type": "numeric",
             "format": {"specifier": ","}},
        ],
        style_table={"overflowX": "auto"},
        style_header={"backgroundColor": "#f5f3ff", "fontWeight": "bold",
                       "fontSize": "0.82rem", "color": "#3a3a5c"},
        style_cell={"fontSize": "0.82rem", "padding": "6px 10px", "color": "#3a3a5c"},
        style_data_conditional=[
            {"if": {"row_index": 0},
             "backgroundColor": "#fff0f0", "fontWeight": "bold"},
        ],
        page_size=11,
        sort_action="native",
    )

    # ── Top 3 evolución histórica ──
    top3 = año_df.nlargest(3, "Rate")["Cause Name"].tolist()
    hist = nat[nat["Cause Name"].isin(top3)].sort_values("Year")

    fig_evol = go.Figure()
    for causa in top3:
        sub = hist[hist["Cause Name"] == causa]
        color = CAUSA_COLORES.get(causa, "#aaa")
        fig_evol.add_trace(go.Scatter(
            x=sub["Year"], y=sub["Rate"],
            mode="lines+markers", name=causa,
            line=dict(color=color, width=2),
            marker=dict(size=5),
        ))
    fig_evol.add_vline(x=año, line_dash="dash", line_color="#5a4fcf", line_width=1.5)
    fig_evol.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="sans-serif", size=11, color="#3a3a5c"),
        margin=dict(l=40, r=20, t=20, b=30),
        xaxis=dict(dtick=3, gridcolor="#f0f0f0"),
        yaxis=dict(title="Tasa/100k", gridcolor="#f0f0f0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    return fig_bar, tabla, fig_evol
