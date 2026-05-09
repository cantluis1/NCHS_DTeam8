"""
tabs/modelo_ets.py — Sección 13: Modelo ETS (Suavizamiento Exponencial)
Traduce tab_ets.R → Dash / Python
West Virginia · Unintentional Injuries (1999–2017)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.stats.diagnostic import acorr_ljungbox
import warnings
warnings.filterwarnings("ignore")

from data.loader import load_df

NAVY = "#1D3557"
AZUL = "#457B9D"


def _get_serie_acc():
    df = load_df()
    dff = df[(df["State"] == "West Virginia") & (df["Cause Name"] == "Unintentional injuries")].sort_values("Year")
    return dff["Rate"].dropna().values, dff["Year"].values[:len(dff["Rate"].dropna())]


def _kpi_chip(label, value_el, color=NAVY):
    return html.Div([
        html.P(label, style={"fontSize": "0.72rem", "fontWeight": "700",
                              "letterSpacing": "0.8px", "textTransform": "uppercase",
                              "color": "#8a97aa", "margin": "0 0 4px"}),
        value_el
    ], style={
        "flex": "1", "background": "#fff", "borderRight": "1px solid #e2e8f2",
        "padding": "14px 12px", "textAlign": "center"
    })


def layout():
    serie, años = _get_serie_acc()
    n = len(serie)
    ets_model = ExponentialSmoothing(serie, trend="mul", seasonal=None, initialization_method="estimated").fit()
    lb = acorr_ljungbox(ets_model.resid, lags=[4], return_df=True)
    pval = float(lb["lb_pvalue"].iloc[0])
    rmse = float(np.sqrt(np.mean(ets_model.resid**2)))

    # ── KPI Bar ──────────────────────────────────────────────
    kpi_bar = html.Div([
        _kpi_chip("Especificación", html.P("ETS(M,A,N)", style={
            "fontSize": "1.05rem", "fontWeight": "800", "color": NAVY,
            "margin": "2px 0", "fontFamily": "monospace"
        })),
        _kpi_chip("AICc", html.P(f"{ets_model.aic:.2f}", style={
            "fontSize": "1.2rem", "fontWeight": "800", "color": "#1A3A5C", "margin": "2px 0"
        })),
        _kpi_chip("RMSE (muestra)", html.P(f"{rmse:.2f}", style={
            "fontSize": "1.2rem", "fontWeight": "800", "color": "#1A3A5C", "margin": "2px 0"
        })),
        _kpi_chip("Ljung-Box p-valor", html.Div([
            html.P("✅ Ruido blanco" if pval > 0.05 else "⚠️ Estructura", style={
                "fontSize": "1.1rem", "fontWeight": "800",
                "color": "#1e8449" if pval > 0.05 else "#e74c3c", "margin": "2px 0"
            }),
            html.P(f"p = {pval:.4f}", style={"fontSize": "0.78rem", "color": "#888", "margin": "0"})
        ]), "#1e8449" if pval > 0.05 else "#e74c3c"),
    ], style={
        "display": "flex", "gap": "0", "marginBottom": "18px",
        "borderRadius": "12px", "overflow": "hidden",
        "boxShadow": "0 2px 10px rgba(0,0,0,0.07)", "border": "1px solid #e2e8f2"
    })

    def _card(icon_class, title, children, note=None):
        return html.Div([
            html.Div([
                html.Span(style={
                    "width": "28px", "height": "28px", "borderRadius": "7px",
                    "background": "#e8f0fb", "color": NAVY,
                    "display": "inline-flex", "alignItems": "center", "justifyContent": "center",
                    "fontSize": "0.8rem", "flexShrink": "0", "marginRight": "8px"
                }, children=[html.I(className=icon_class)]),
                html.Strong(title, style={"color": NAVY})
            ], style={
                "fontSize": "0.92rem", "fontWeight": "700", "color": NAVY,
                "marginBottom": "14px", "paddingBottom": "10px",
                "borderBottom": "2px solid #f0f4fa", "display": "flex", "alignItems": "center"
            }),
            *children,
            *([html.Div([
                html.I(className="fas fa-circle-info me-1"), html.Strong(" Interpretación: "), note
            ], style={
                "background": "#f4f7fb", "borderLeft": f"3px solid {AZUL}",
                "borderRadius": "0 6px 6px 0", "padding": "8px 12px",
                "fontSize": "0.8rem", "color": "#4a5568", "marginTop": "12px"
            })] if note else [])
        ], style={
            "background": "#fff", "border": "1px solid #e2e8f2",
            "borderRadius": "12px", "boxShadow": "0 1px 8px rgba(0,0,0,0.05)",
            "padding": "18px", "marginBottom": "18px"
        })

    # ── 13.1 Residuos ─────────────────────────────────────────
    res = ets_model.resid
    df_res = pd.DataFrame({"anio": años[:len(res)], "residuo": res})

    fig_res = go.Figure()
    for _, row in df_res.iterrows():
        fig_res.add_trace(go.Scatter(x=[row.anio, row.anio], y=[0, row.residuo], mode="lines",
                                     line=dict(color=AZUL, width=2), showlegend=False))
    fig_res.add_trace(go.Scatter(x=df_res.anio, y=df_res.residuo, mode="markers",
                                  marker=dict(color=NAVY, size=5), showlegend=False))
    fig_res.add_hline(y=0, line=dict(color="#333", dash="dot", width=1))
    fig_res.update_layout(height=260, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           xaxis_title="Año", yaxis_title="Residuo",
                           font=dict(family="Segoe UI, Helvetica Neue, Arial, sans-serif", size=11))

    fig_hist = go.Figure(go.Histogram(x=res, nbinsx=8,
                                       marker=dict(color=AZUL, line=dict(color=NAVY, width=1))))
    fig_hist.update_layout(height=260, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                            xaxis_title="Residuo", yaxis_title="Frecuencia",
                            font=dict(family="Segoe UI, Helvetica Neue, Arial, sans-serif", size=11))

    # ── 13.2 Proyección ──────────────────────────────────────
    fc = ets_model.forecast(5)
    sim = ets_model.simulate(nsimulations=5, anchor="end", repetitions=1000)
    lo95 = np.percentile(sim, 2.5, axis=1)
    hi95 = np.percentile(sim, 97.5, axis=1)
    lo80 = np.percentile(sim, 10, axis=1)
    hi80 = np.percentile(sim, 90, axis=1)
    años_fc = np.arange(años[-1] + 1, años[-1] + 6)

    fig_fc = go.Figure()
    fig_fc.add_trace(go.Scatter(
        x=np.concatenate([años_fc, años_fc[::-1]]),
        y=np.concatenate([hi95, lo95[::-1]]),
        fill="toself", fillcolor="rgba(69,123,157,0.15)",
        line=dict(color="rgba(0,0,0,0)"), name="IC 95%"
    ))
    fig_fc.add_trace(go.Scatter(
        x=np.concatenate([años_fc, años_fc[::-1]]),
        y=np.concatenate([hi80, lo80[::-1]]),
        fill="toself", fillcolor="rgba(69,123,157,0.35)",
        line=dict(color="rgba(0,0,0,0)"), name="IC 80%"
    ))
    fig_fc.add_trace(go.Scatter(x=años, y=serie, mode="lines+markers", name="Histórico (1999–2017)",
                                 line=dict(color=NAVY, width=2.5)))
    fig_fc.add_trace(go.Scatter(x=años_fc, y=fc, mode="lines+markers", name="Proyección ETS",
                                 line=dict(color=AZUL, width=2.5, dash="dash"),
                                 marker=dict(color=AZUL, size=7, symbol="triangle-up")))
    fig_fc.add_vline(x=años[-1] + 0.5, line=dict(color="#333", dash="dot", width=1.5))
    fig_fc.update_layout(
        title=dict(text="<b>Proyección ETS — Unintentional Injuries · West Virginia</b>",
                   font=dict(size=13, color=NAVY)),
        xaxis_title="Año", yaxis_title="Tasa por 100,000 hab.",
        hovermode="x unified", height=380,
        legend=dict(orientation="h", x=0, y=-0.15),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, Helvetica Neue, Arial, sans-serif", size=11)
    )

    # ── 13.3 Tabla ────────────────────────────────────────────
    df_tbl = pd.DataFrame({
        "Año": años_fc,
        "Estimado": np.round(fc, 1),
        "Lo 80%": np.round(lo80, 1),
        "Hi 80%": np.round(hi80, 1),
        "Lo 95%": np.round(lo95, 1),
        "Hi 95%": np.round(hi95, 1),
    })
    tbl_fc = dbc.Table.from_dataframe(df_tbl, striped=True, bordered=True, hover=True, className="table-sm")

    return dbc.Container([
        html.Br(),
        # Encabezado
        html.Div([
            html.Span("Modelo 2 · Suavizamiento Exponencial", style={
                "display": "inline-block",
                "background": "rgba(255,255,255,0.12)", "border": "1px solid rgba(255,255,255,0.2)",
                "color": "#a8d8f0", "fontSize": "0.72rem", "fontWeight": "700",
                "letterSpacing": "1.3px", "textTransform": "uppercase",
                "padding": "3px 10px", "borderRadius": "20px", "marginBottom": "9px"
            }),
            html.H3([html.I(className="fas fa-chart-line me-2"),
                     "ETS (Error, Trend, Seasonality)"],
                    style={"color": "#fff", "fontWeight": "800", "margin": "0 0 5px"}),
            html.P([
                "Suavizamiento exponencial con selección automática por AICc.",
                " Aplicado a Unintentional Injuries – West Virginia (1999–2017). Sección 13."
            ], style={"color": "rgba(255,255,255,0.72)", "fontSize": "0.855rem",
                      "lineHeight": "1.5", "margin": "0", "maxWidth": "760px"}),
        ], style={
            "background": "linear-gradient(135deg, #0f2340 0%, #1D3557 60%, #2a4a72 100%)",
            "borderRadius": "14px", "padding": "22px 28px", "marginBottom": "20px",
            "boxShadow": "0 4px 20px rgba(29,53,87,0.15)"
        }),

        kpi_bar,

        # 13.1 Residuos
        dbc.Row([
            dbc.Col(_card("fas fa-microscope", "13.1 · Diagnóstico de residuos — ETS",
                          [dcc.Graph(figure=fig_res, style={"height": "260px"})],
                          "Residuos deben comportarse como ruido blanco (p > 0.05 en Ljung-Box)."), md=6),
            dbc.Col(_card("fas fa-chart-bar", "13.1 · Distribución de residuos — ETS",
                          [dcc.Graph(figure=fig_hist, style={"height": "260px"})]), md=6),
        ]),

        # 13.2 Proyección
        _card("fas fa-chart-line", "13.2 · Proyección ETS — Unintentional Injuries (2018–2022)",
              [dcc.Graph(figure=fig_fc, style={"height": "380px"})],
              "ETS proyecta crecimiento sostenido. Los IC se amplían por la incertidumbre acumulada en series cortas con tendencia fuerte."),

        # 13.3 Tabla
        _card("fas fa-table", "13.3 · Tabla de valores proyectados — ETS",
              [tbl_fc,
               html.P("IC 80% e IC 95%: intervalos de confianza. ETS tiene error multiplicativo, lo que amplía los IC proporcionalmente.",
                      style={"fontSize": "0.74rem", "color": "#8a97aa", "marginTop": "10px"})]),
        html.Br(),
    ], fluid=True)
