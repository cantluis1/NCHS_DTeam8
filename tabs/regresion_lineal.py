"""
tabs/regresion_lineal.py — Sección 14: Regresión Lineal con Tendencia Temporal
Traduce tab_regresion.R → Dash / Python
Benchmark OLS · West Virginia · Unintentional Injuries (1999–2017)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.stattools import acf
import warnings
warnings.filterwarnings("ignore")

from data.loader import load_df

NAVY = "#1D3557"
AZUL = "#457B9D"


def _get_serie_acc():
    df = load_df()
    dff = df[(df["State"] == "West Virginia") & (df["Cause Name"] == "Unintentional injuries")].sort_values("Year")
    serie = dff["Rate"].dropna().values
    años  = dff["Year"].values[:len(serie)]
    return serie, años


def layout():
    serie, años = _get_serie_acc()
    n = len(serie)
    t = np.arange(n)

    # Modelo OLS
    lm = LinearRegression().fit(t.reshape(-1, 1), serie)
    y_pred = lm.predict(t.reshape(-1, 1))
    resid  = serie - y_pred

    r2    = 1 - np.sum(resid**2) / np.sum((serie - np.mean(serie))**2)
    rmse  = np.sqrt(np.mean(resid**2))
    beta1 = lm.coef_[0]

    lb = acorr_ljungbox(resid, lags=[4], return_df=True)
    pval = float(lb["lb_pvalue"].iloc[0])

    def _kpi_chip(label, value_el):
        return html.Div([
            html.P(label, style={"fontSize": "0.72rem", "fontWeight": "700",
                                  "letterSpacing": "0.8px", "textTransform": "uppercase",
                                  "color": "#8a97aa", "margin": "0 0 4px"}),
            value_el
        ], style={"flex": "1", "background": "#fff", "borderRight": "1px solid #e2e8f2",
                  "padding": "14px 12px", "textAlign": "center"})

    kpi_bar = html.Div([
        _kpi_chip("R²", html.P(f"{r2*100:.1f}%", style={
            "fontSize": "1.2rem", "fontWeight": "800", "color": "#1A3A5C", "margin": "2px 0"
        })),
        _kpi_chip("β₁ (pendiente/año)", html.P(f"+{beta1:.3f} pts/año", style={
            "fontSize": "1.2rem", "fontWeight": "800", "color": AZUL, "margin": "2px 0"
        })),
        _kpi_chip("RMSE (muestra)", html.P(f"{rmse:.2f}", style={
            "fontSize": "1.2rem", "fontWeight": "800", "color": "#1A3A5C", "margin": "2px 0"
        })),
        _kpi_chip("Ljung-Box p-valor", html.Div([
            html.P("✅ Ruido blanco" if pval > 0.05 else "⚠️ Autocorrelación", style={
                "fontSize": "1.1rem", "fontWeight": "800",
                "color": "#1e8449" if pval > 0.05 else "#e74c3c", "margin": "2px 0"
            }),
            html.P(f"p = {pval:.4f}", style={"fontSize": "0.78rem", "color": "#888", "margin": "0"})
        ])),
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

    # ── 14.1 ACF Residuos ─────────────────────────────────────
    max_lag = min(8, n - 2)
    acf_vals = acf(resid, nlags=max_lag, fft=True)
    lags     = np.arange(max_lag + 1)
    ic_band  = 1.96 / np.sqrt(n)

    fig_acf = go.Figure()
    for lag, val in zip(lags, acf_vals):
        fig_acf.add_trace(go.Scatter(x=[lag, lag], y=[0, val], mode="lines",
                                      line=dict(color=NAVY, width=3), showlegend=False))
        fig_acf.add_trace(go.Scatter(x=[lag], y=[val], mode="markers",
                                      marker=dict(color=NAVY, size=6), showlegend=False))
    fig_acf.add_hline(y=ic_band,  line=dict(color=AZUL, dash="dash", width=1.2), annotation_text="IC 95%")
    fig_acf.add_hline(y=-ic_band, line=dict(color=AZUL, dash="dash", width=1.2))
    fig_acf.update_layout(height=260, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           xaxis_title="Rezago", yaxis_title="Autocorrelación",
                           yaxis=dict(range=[-1.1, 1.1]),
                           font=dict(family="Segoe UI, Helvetica Neue, Arial, sans-serif", size=11))

    fig_hist = go.Figure(go.Histogram(x=resid, nbinsx=8,
                                       marker=dict(color=AZUL, line=dict(color=NAVY, width=1))))
    fig_hist.update_layout(height=260, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                            xaxis_title="Residuo", yaxis_title="Frecuencia",
                            font=dict(family="Segoe UI, Helvetica Neue, Arial, sans-serif", size=11))

    # ── 14.2 Proyección ──────────────────────────────────────
    h = 5
    t_fut  = np.arange(n, n + h).reshape(-1, 1)
    pred   = lm.predict(t_fut)
    años_fc = np.arange(años[-1] + 1, años[-1] + h + 1)

    # IC manual (OLS)
    mse = np.mean(resid**2)
    se  = np.sqrt(mse)
    t_vals = np.arange(n, n + h)
    mean_t = np.mean(t)
    ss_t   = np.sum((t - mean_t)**2)
    se_pred = se * np.sqrt(1 + 1/n + (t_vals - mean_t)**2 / ss_t)
    z80 = 1.282; z95 = 1.960
    lo80 = pred - z80 * se_pred; hi80 = pred + z80 * se_pred
    lo95 = pred - z95 * se_pred; hi95 = pred + z95 * se_pred

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
    fig_fc.add_trace(go.Scatter(x=años_fc, y=pred, mode="lines+markers", name="Proyección OLS",
                                 line=dict(color=AZUL, width=2.5, dash="dash"),
                                 marker=dict(color=AZUL, size=7, symbol="triangle-up")))
    fig_fc.add_vline(x=años[-1] + 0.5, line=dict(color="#333", dash="dot", width=1.5))
    fig_fc.update_layout(
        title=dict(text="<b>Proyección Regresión Lineal — Unintentional Injuries · West Virginia</b>",
                   font=dict(size=13, color=NAVY)),
        xaxis_title="Año", yaxis_title="Tasa por 100,000 hab.",
        hovermode="x unified", height=380,
        legend=dict(orientation="h", x=0, y=-0.15),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, Helvetica Neue, Arial, sans-serif", size=11)
    )

    # ── 14.3 Tabla ────────────────────────────────────────────
    df_tbl = pd.DataFrame({
        "Año":     años_fc,
        "Estimado": np.round(pred, 1),
        "Lo 80%":   np.round(lo80, 1),
        "Hi 80%":   np.round(hi80, 1),
        "Lo 95%":   np.round(lo95, 1),
        "Hi 95%":   np.round(hi95, 1),
    })
    tbl_fc = dbc.Table.from_dataframe(df_tbl, striped=True, bordered=True, hover=True, className="table-sm")

    return dbc.Container([
        html.Br(),
        # Encabezado
        html.Div([
            html.Span("Modelo 3 · Benchmark OLS", style={
                "display": "inline-block",
                "background": "rgba(255,255,255,0.12)", "border": "1px solid rgba(255,255,255,0.2)",
                "color": "#a8d8f0", "fontSize": "0.72rem", "fontWeight": "700",
                "letterSpacing": "1.3px", "textTransform": "uppercase",
                "padding": "3px 10px", "borderRadius": "20px", "marginBottom": "9px"
            }),
            html.H3([html.I(className="fas fa-chart-line me-2"),
                     "Regresión Lineal con Tendencia Temporal"],
                    style={"color": "#fff", "fontWeight": "800", "margin": "0 0 5px"}),
            html.P([
                "Benchmark OLS: ŷₜ = β₀ + β₁·t + εₜ. "
                "Aplicado a Unintentional Injuries – West Virginia (1999–2017). Sección 14."
            ], style={"color": "rgba(255,255,255,0.72)", "fontSize": "0.855rem",
                      "lineHeight": "1.5", "margin": "0", "maxWidth": "760px"}),
        ], style={
            "background": "linear-gradient(135deg, #0f2340 0%, #1D3557 60%, #2a4a72 100%)",
            "borderRadius": "14px", "padding": "22px 28px", "marginBottom": "20px",
            "boxShadow": "0 4px 20px rgba(29,53,87,0.15)"
        }),

        kpi_bar,

        # 14.1 Residuos
        dbc.Row([
            dbc.Col(_card("fas fa-microscope", "14.1 · ACF de residuos — Regresión Lineal",
                          [dcc.Graph(figure=fig_acf, style={"height": "260px"})],
                          "Barras que superen las bandas de confianza (±1.96/√n) indican autocorrelación residual."), md=6),
            dbc.Col(_card("fas fa-chart-bar", "14.1 · Distribución de residuos — OLS",
                          [dcc.Graph(figure=fig_hist, style={"height": "260px"})]), md=6),
        ]),

        # 14.2 Proyección
        _card("fas fa-chart-line",
              "14.2 · Proyección Regresión Lineal — Unintentional Injuries (2018–2022)",
              [dcc.Graph(figure=fig_fc, style={"height": "380px"})],
              "Las proyecciones convergen con ETS porque ambos modelos capturan la misma tendencia lineal. "
              "Sin embargo, los IC subestiman la incertidumbre real al no incorporar dependencia temporal."),

        # 14.3 Tabla
        _card("fas fa-table", "14.3 · Tabla de valores proyectados — Regresión Lineal",
              [tbl_fc,
               html.P("Intervalos de predicción OLS al 80% y 95%. Válidos solo bajo supuesto de errores independientes (no cumplido para series I(1)).",
                      style={"fontSize": "0.74rem", "color": "#8a97aa", "marginTop": "10px"})]),
        html.Br(),
    ], fluid=True)
