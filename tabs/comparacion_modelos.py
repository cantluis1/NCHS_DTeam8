"""
tabs/comparacion_modelos.py — Secciones 15–16: Comparación y Selección Final
Replica tab_comparacion.R → Dash / Python
West Virginia · Unintentional Injuries (1999–2017)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore")

from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.stats.diagnostic import acorr_ljungbox
from sklearn.linear_model import LinearRegression
from data.loader import load_df

NAVY  = "#1D3557"
AZUL  = "#457B9D"
ROJO  = "#E63946"
VERDE = "#1e8449"


# ── Helpers ────────────────────────────────────────────────────────────────
def _get_serie():
    df = load_df()
    dff = df[(df["State"] == "West Virginia") &
             (df["Cause Name"] == "Unintentional injuries")].sort_values("Year")
    serie = dff["Rate"].dropna().values
    años  = dff["Year"].values[:len(serie)]
    return serie, años


def _aicc(fit_obj, k, n):
    return fit_obj.aic + (2 * k * (k + 1)) / max(1, n - k - 1)


def _lb(res):
    r = acorr_ljungbox(res, lags=[4], return_df=True)
    return float(r["lb_stat"].iloc[0]), float(r["lb_pvalue"].iloc[0])


def _tscv(serie, h, fn):
    n = len(serie)
    rmse_l, mae_l = [], []
    for i in range(max(10, n // 2), n):
        train, actual = serie[:i], serie[i:i+h]
        if len(actual) < h:
            continue
        try:
            pred = np.array(fn(train, h))[:h]
            e = actual[:h] - pred
            rmse_l.append(float(np.sqrt(np.mean(e**2))))
            mae_l.append(float(np.mean(np.abs(e))))
        except Exception:
            pass
    return (round(float(np.mean(rmse_l)), 3) if rmse_l else float("nan"),
            round(float(np.mean(mae_l)),  3) if mae_l  else float("nan"))


def _section_header(icon_cls, titulo):
    return html.Div([
        html.I(className=f"{icon_cls} me-2"),
        html.Strong(titulo)
    ], style={
        "background": NAVY, "color": "#fff", "borderRadius": "8px 8px 0 0",
        "padding": "12px 18px", "fontSize": "0.92rem", "fontWeight": "700"
    })


def _note(text, color=AZUL):
    return html.P(text, style={
        "fontSize": "0.81rem", "color": "#666",
        "marginBottom": "10px", "lineHeight": "1.55"
    })


def _dt_table(df, bold_col0=False):
    """Dark-header sortable table matching Shiny DataTable style."""
    thead = html.Thead(html.Tr([
        html.Th(col, style={
            "background": "#2c3e50", "color": "#fff",
            "padding": "10px 14px", "fontSize": "0.82rem",
            "fontWeight": "600", "borderRight": "1px solid #3d5166",
            "whiteSpace": "nowrap"
        }) for col in df.columns
    ]))
    rows = []
    for i, row in df.iterrows():
        cells = []
        for j, (col, val) in enumerate(row.items()):
            is_bold = bold_col0 and j == 0
            # Highlight best row (first data row = winner)
            bg = "#e8f4fd" if i == 0 else ("#fff" if i % 2 == 0 else "#f9fafc")
            cells.append(html.Td(val, style={
                "padding": "9px 14px", "fontSize": "0.83rem",
                "fontWeight": "700" if is_bold else "400",
                "background": bg,
                "color": NAVY if (is_bold and i == 0) else "#333",
                "borderBottom": "1px solid #eef0f3"
            }))
        rows.append(html.Tr(cells))
    return html.Table([thead, html.Tbody(rows)], style={
        "width": "100%", "borderCollapse": "collapse",
        "borderRadius": "0 0 8px 8px", "overflow": "hidden"
    })


def _card_section(icon_cls, titulo, children):
    return html.Div([
        _section_header(icon_cls, titulo),
        html.Div(children, style={
            "background": "#fff", "border": "1px solid #e2e8f2",
            "borderTop": "none", "borderRadius": "0 0 8px 8px",
            "padding": "16px 18px"
        })
    ], style={"marginBottom": "20px",
              "boxShadow": "0 2px 12px rgba(0,0,0,0.06)", "borderRadius": "8px"})


def _criteria_card(num, titulo, texto, color):
    return html.Div([
        html.P(num, style={
            "margin": "0 0 4px", "fontSize": "0.68rem", "fontWeight": "700",
            "textTransform": "uppercase", "letterSpacing": "0.9px", "color": color
        }),
        html.P(titulo, style={
            "margin": "0 0 8px", "fontSize": "0.88rem",
            "fontWeight": "700", "color": NAVY
        }),
        html.P(texto, style={
            "margin": "0", "fontSize": "0.83rem",
            "lineHeight": "1.6", "color": "#333"
        })
    ], style={
        "background": "#fff", "borderRadius": "8px",
        "padding": "16px 18px", "boxShadow": "0 1px 4px rgba(0,0,0,0.06)",
        "borderTop": f"3px solid {color}"
    })


def layout():
    serie, años = _get_serie()
    n = len(serie)

    # ── Fit models ─────────────────────────────────────────────────────────
    arima    = ARIMA(serie, order=(0, 1, 0), trend="t").fit()
    ets      = ExponentialSmoothing(serie, trend="mul", seasonal=None,
                                    initialization_method="estimated").fit()
    holt     = ExponentialSmoothing(serie, trend="add", seasonal=None,
                                    initialization_method="estimated").fit()
    holtd    = ExponentialSmoothing(serie, trend="add", seasonal=None,
                                    damped_trend=True,
                                    initialization_method="estimated").fit()
    t_hist   = np.arange(n)
    lm       = LinearRegression().fit(t_hist.reshape(-1, 1), serie)
    res_lm   = serie - lm.predict(t_hist.reshape(-1, 1))

    # ARIMA drift & AICc
    drift_b  = float(arima.params[0])
    aicc_a   = _aicc(arima, 1, n)
    aicc_e   = _aicc(ets,   4, n)
    aicc_h   = _aicc(holt,  4, n)
    aicc_hd  = _aicc(holtd, 5, n)

    # ── KPI banner ─────────────────────────────────────────────────────────
    def _chip(label, value):
        return html.Div([
            html.P(label, style={
                "margin": "0 0 2px", "fontSize": "0.62rem", "fontWeight": "700",
                "letterSpacing": "1px", "textTransform": "uppercase",
                "color": "rgba(255,255,255,0.55)"
            }),
            html.P(value, style={
                "margin": "0", "fontSize": "1.15rem",
                "fontWeight": "800", "color": "#fff"
            })
        ], style={
            "background": "rgba(255,255,255,0.10)",
            "borderRadius": "8px", "padding": "10px 18px",
            "border": "1px solid rgba(255,255,255,0.15)"
        })

    banner = html.Div([
        html.Div([
            html.Span("COMPARACIÓN DE MODELOS Y SELECCIÓN FINAL — SECCIONES 15–16", style={
                "display": "inline-block", "background": "rgba(255,255,255,0.12)",
                "border": "1px solid rgba(255,255,255,0.2)", "color": "#a8d8f0",
                "fontSize": "0.68rem", "fontWeight": "700", "letterSpacing": "1.2px",
                "textTransform": "uppercase", "padding": "3px 10px",
                "borderRadius": "20px", "marginBottom": "10px"
            }),
            html.H3([
                html.I(className="fas fa-scale-balanced me-2"),
                "ARIMA(0,1,0) with drift"
            ], style={"color": "#fff", "fontWeight": "800", "margin": "0 0 5px",
                      "fontSize": "1.3rem"}),
            html.P("Evaluación sistemática de ARIMA, ETS, Holt, Holt amortiguado, "
                   "Naive y Regresión Lineal mediante criterios de información, "
                   "diagnóstico de residuos y validación cruzada.",
                   style={"color": "rgba(255,255,255,0.72)", "fontSize": "0.83rem",
                          "lineHeight": "1.5", "margin": "0", "maxWidth": "600px"}),
        ], style={"flex": "1"}),
        html.Div([
            _chip("AICc",       f"{aicc_a:.2f}"),
            _chip("BIC",        f"{arima.bic:.2f}"),
            _chip("Ljung-Box p", f"{_lb(arima.resid[1:])[1]:.3f}"),
            _chip("Drift β",    f"+{drift_b:.3f} pts/año"),
        ], style={"display": "flex", "gap": "10px", "flexWrap": "wrap",
                  "alignItems": "center"}),
    ], style={
        "display": "flex", "gap": "24px", "alignItems": "center",
        "flexWrap": "wrap",
        "background": "linear-gradient(135deg, #0f2340 0%, #1D3557 60%, #2a4a72 100%)",
        "borderRadius": "14px", "padding": "22px 28px", "marginBottom": "22px",
        "boxShadow": "0 4px 20px rgba(29,53,87,0.18)"
    })

    # ── 15.1 AIC / AICc / BIC table ────────────────────────────────────────
    df_aic = pd.DataFrame({
        "Modelo":     ["ARIMA(0,1,0) with drift",
                       f"ETS – ETS(M,A,N)",
                       "Holt lineal – ETS(A,A,N)",
                       "Holt amortiguado – ETS(A,Ad,N)"],
        "Parámetros": [1, 4, 4, 5],
        "AIC":  [round(arima.aic, 2), round(ets.aic, 2),
                 round(holt.aic, 2),  round(holtd.aic, 2)],
        "AICc": [round(aicc_a, 2), round(aicc_e, 2),
                 round(aicc_h, 2), round(aicc_hd, 2)],
        "BIC":  [round(arima.bic, 2), round(ets.bic, 2),
                 round(holt.bic, 2),  round(holtd.bic, 2)],
    })

    # ── 15.2 Ljung-Box ─────────────────────────────────────────────────────
    lbs_data = [
        ("ARIMA(0,1,0) with drift", _lb(arima.resid[1:])),
        ("ETS – ETS(M,A,N)",        _lb(ets.resid)),
        ("Holt lineal",             _lb(holt.resid)),
        ("Holt amortiguado",        _lb(holtd.resid)),
        ("Regresión lineal",        _lb(res_lm)),
    ]

    def _lb_row(nombre, lb_result):
        q, p = lb_result
        ok = p > 0.05
        return {
            "Modelo":      nombre,
            "Q*":          round(q, 3),
            "p-valor":     round(p, 4),
            "Diagnóstico": "✅ Ruido blanco" if ok else "❌ Autocorrelación"
        }

    df_lb = pd.DataFrame([_lb_row(n, lb) for n, lb in lbs_data])

    # Color rows for Ljung-Box
    def _lb_table(df):
        thead = html.Thead(html.Tr([
            html.Th(col, style={
                "background": "#2c3e50", "color": "#fff",
                "padding": "10px 14px", "fontSize": "0.82rem",
                "fontWeight": "600", "borderRight": "1px solid #3d5166"
            }) for col in df.columns
        ]))
        rows = []
        for i, row in df.iterrows():
            ok = "Ruido blanco" in str(row["Diagnóstico"])
            bg_row = "#f0faf4" if ok else "#fef0f0"
            cells = []
            for j, (col, val) in enumerate(row.items()):
                color_val = VERDE if (col == "Diagnóstico" and ok) else ("#c0392b" if col == "Diagnóstico" else "#333")
                cells.append(html.Td(val, style={
                    "padding": "9px 14px", "fontSize": "0.83rem",
                    "background": bg_row, "color": color_val,
                    "fontWeight": "700" if col == "Diagnóstico" else "400",
                    "borderBottom": "1px solid #eef0f3"
                }))
            rows.append(html.Tr(cells))
        return html.Table([thead, html.Tbody(rows)],
                          style={"width": "100%", "borderCollapse": "collapse"})

    # ── 15.3 tsCV ──────────────────────────────────────────────────────────
    def fn_arima(tr, h):
        return list(ARIMA(tr, order=(0,1,0), trend="t").fit().get_forecast(h).predicted_mean)
    def fn_ets(tr, h):
        return list(ExponentialSmoothing(tr, trend="mul", seasonal=None,
                                         initialization_method="estimated").fit().forecast(h))
    def fn_holt(tr, h):
        return list(ExponentialSmoothing(tr, trend="add", seasonal=None,
                                         initialization_method="estimated").fit().forecast(h))
    def fn_holtd(tr, h):
        return list(ExponentialSmoothing(tr, trend="add", seasonal=None, damped_trend=True,
                                         initialization_method="estimated").fit().forecast(h))
    def fn_naive(tr, h):
        d = float(np.mean(np.diff(tr)))
        return [float(tr[-1]) + d * s for s in range(1, h+1)]
    def fn_lm(tr, h):
        m = LinearRegression().fit(np.arange(len(tr)).reshape(-1,1), tr)
        return list(m.predict(np.arange(len(tr), len(tr)+h).reshape(-1,1)))

    modelos_cv = [
        ("ARIMA(0,1,0) with drift", fn_arima),
        ("ETS – ETS(M,A,N)",        fn_ets),
        ("Holt lineal",             fn_holt),
        ("Holt amortiguado",        fn_holtd),
        ("Naive with drift",        fn_naive),
        ("Regresión lineal",        fn_lm),
    ]
    cv_rows = []
    for nombre, fn in modelos_cv:
        r1 = _tscv(serie, 1, fn)
        r3 = _tscv(serie, 3, fn)
        cv_rows.append({
            "Modelo":    nombre,
            "RMSE h=1":  r1[0],
            "MAE h=1":   r1[1],
            "RMSE h=3":  r3[0],
            "MAE h=3":   r3[1],
        })
    df_cv = pd.DataFrame(cv_rows)

    # Bold best RMSE h=1 row
    best_rmse1_idx = df_cv["RMSE h=1"].idxmin()

    def _cv_table(df, best_idx):
        thead = html.Thead(html.Tr([
            html.Th(col, style={
                "background": "#2c3e50", "color": "#fff",
                "padding": "10px 14px", "fontSize": "0.82rem",
                "fontWeight": "600", "borderRight": "1px solid #3d5166"
            }) for col in df.columns
        ]))
        rows = []
        for i, row in df.iterrows():
            is_best = (i == best_idx)
            cells = []
            for j, (col, val) in enumerate(row.items()):
                bg = "#e8f4fd" if is_best else ("#fff" if i % 2 == 0 else "#f9fafc")
                cells.append(html.Td(val, style={
                    "padding": "9px 14px", "fontSize": "0.83rem",
                    "fontWeight": "700" if is_best else "400",
                    "background": bg, "color": NAVY if is_best else "#333",
                    "borderBottom": "1px solid #eef0f3"
                }))
            rows.append(html.Tr(cells))
        return html.Table([thead, html.Tbody(rows)],
                          style={"width": "100%", "borderCollapse": "collapse"})

    # ── 15.4 Gráfico comparativo ────────────────────────────────────────────
    h_fc = 5
    años_fc = np.arange(años[-1] + 1, años[-1] + h_fc + 1)
    colores_fc = {
        "ARIMA(0,1,0) drift": NAVY,
        "ETS":                 "#2196F3",
        "Holt lineal":         "#4CAF50",
        "Holt amortiguado":   "#FF9800",
        "Naive drift":         "#9B2226",
        "Reg. lineal":         "#9C27B0",
    }

    fig_comp = go.Figure()
    fig_comp.add_trace(go.Scatter(
        x=años, y=serie, mode="lines+markers", name="Histórico",
        line=dict(color="black", width=2.5),
        marker=dict(color="black", size=5)
    ))

    preds = {
        "ARIMA(0,1,0) drift": list(arima.get_forecast(h_fc).predicted_mean),
        "ETS":                 list(ets.forecast(h_fc)),
        "Holt lineal":         list(holt.forecast(h_fc)),
        "Holt amortiguado":   list(holtd.forecast(h_fc)),
        "Naive drift":         fn_naive(serie, h_fc),
        "Reg. lineal":         fn_lm(serie, h_fc),
    }
    for label, pred in preds.items():
        fig_comp.add_trace(go.Scatter(
            x=años_fc, y=pred, mode="lines+markers", name=label,
            line=dict(color=colores_fc[label], width=2, dash="dash"),
            marker=dict(size=5)
        ))

    fig_comp.add_vline(x=años[-1] + 0.5,
                       line=dict(color="#aaa", dash="dot", width=1.5))
    fig_comp.update_layout(
        title=dict(text="<b>Comparación de proyecciones — Unintentional Injuries · West Virginia</b>",
                   font=dict(size=12, color=NAVY), x=0.01),
        xaxis_title="Año", yaxis_title="Tasa ajustada por 100,000 hab.",
        hovermode="x unified", height=400,
        legend=dict(orientation="h", x=0, y=-0.2, font=dict(size=10)),
        plot_bgcolor="#fff", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, Helvetica Neue, Arial, sans-serif", size=11),
    )
    fig_comp.update_xaxes(showgrid=True, gridcolor="#f0f0f0")
    fig_comp.update_yaxes(showgrid=True, gridcolor="#f0f0f0")

    nota_fc = html.Div([
        html.I(className="fas fa-circle-info me-1"),
        html.Strong(" Interpretación: "),
        "Línea negra: serie histórica 1999–2017. Líneas discontinuas: proyecciones 2018–2022 de cada modelo. "
        "ARIMA(0,1,0) with drift y ETS convergen; Holt amortiguado proyecta crecimiento decelerado."
    ], style={
        "background": "#fff8e1", "border": "1px solid #ffe082",
        "borderLeft": "4px solid #f9a825",
        "borderRadius": "6px", "padding": "10px 14px",
        "fontSize": "0.8rem", "color": "#5d4037", "marginTop": "12px"
    })

    # ── Nota tsCV ──────────────────────────────────────────────────────────
    nota_cv = html.Div([
        html.I(className="fas fa-circle-info me-1"),
        html.Strong(" Nota: "),
        "La Regresión Lineal obtiene el menor RMSE en tsCV, pero sus IC son inválidos para series I(1) "
        "(no estacionaria). Entre los modelos válidos, las diferencias de RMSE son marginales (< 0.4 pts)."
    ], style={
        "background": "#fff", "border": "1px solid #90caf9",
        "borderLeft": "4px solid #1565c0",
        "borderRadius": "6px", "padding": "10px 14px",
        "fontSize": "0.8rem", "color": "#1565c0", "marginTop": "12px"
    })

    # ── Sección 16 — Justificación ─────────────────────────────────────────
    delta_e  = round(aicc_e  - aicc_a, 2)
    delta_h  = round(aicc_h  - aicc_a, 2)
    delta_hd = round(aicc_hd - aicc_a, 2)
    lb_a_p   = round(_lb(arima.resid[1:])[1], 3)

    sec16_header = html.Div([
        html.Span("SECCIÓN 16 · MODELO PREDICTIVO ÓPTIMO", style={
            "display": "inline-block",
            "background": "rgba(255,255,255,0.12)", "border": "1px solid rgba(255,255,255,0.2)",
            "color": "#a8d8f0", "fontSize": "0.68rem", "fontWeight": "700",
            "letterSpacing": "1.2px", "textTransform": "uppercase",
            "padding": "3px 10px", "borderRadius": "20px", "marginBottom": "10px"
        }),
        html.H3([
            html.I(className="fas fa-scale-balanced me-2"),
            "ARIMA(0,1,0) with drift — Selección y Justificación"
        ], style={"color": "#fff", "fontWeight": "800", "margin": "0 0 5px"}),
        html.P("Comparación por AICc, diagnóstico de residuos y validez estadística. "
               "Aplicado a Unintentional Injuries – West Virginia (1999–2017). Sección 16.",
               style={"color": "rgba(255,255,255,0.72)", "fontSize": "0.83rem",
                      "margin": "0", "maxWidth": "680px"}),
    ], style={
        "background": "linear-gradient(135deg, #0f2340 0%, #1D3557 60%, #2a4a72 100%)",
        "borderRadius": "14px", "padding": "20px 26px", "marginBottom": "18px",
        "boxShadow": "0 4px 20px rgba(29,53,87,0.15)"
    })

    criterios_grid = html.Div([
        dbc.Row([
            dbc.Col(_criteria_card(
                "① Criterio de selección — AICc",
                "① Criterio de selección — AICc",
                f"Con n = {n} observaciones, el AICc penaliza la complejidad ajustada por tamaño muestral. "
                f"El ARIMA obtuvo el valor más bajo con un único parámetro, logrando el mejor equilibrio "
                f"entre ajuste y parsimonia.",
                VERDE
            ), md=6, className="mb-3"),
            dbc.Col(_criteria_card(
                "② Comparación con modelos rivales",
                "② Comparación con modelos rivales",
                f"ETS(M,A,N): ΔAICc = {delta_e:.2f} — evidencia fuerte en contra (Burnham & Anderson, 2002). "
                f"Holt lineal: ΔAICc = {delta_h:.2f}. Holt amortiguado: ΔAICc = {delta_hd:.2f}. "
                f"Ninguno supera al ARIMA en parsimonia.",
                AZUL
            ), md=6, className="mb-3"),
        ]),
        dbc.Row([
            dbc.Col(_criteria_card(
                "③ Validez estadística — Residuos",
                "③ Validez estadística — Residuos",
                f"Ljung-Box: Q* = {_lb(arima.resid[1:])[0]:.3f}, p = {lb_a_p:.3f} — sin autocorrelación significativa. "
                f"La diferenciación I(1) elimina la raíz unitaria (ADF confirmado). "
                f"El drift β = {drift_b:.2f} pts/año captura el crecimiento desde 2014 (sección 9.1.1).",
                "#1565c0"
            ), md=6, className="mb-3"),
            dbc.Col(_criteria_card(
                "④ Exclusión — Regresión Lineal",
                "④ Exclusión — Regresión Lineal",
                "Descartada por razones metodológicas: serie no estacionaria (ADF: p = 0.511). "
                "OLS sobre series I(1) produce intervalos de predicción inválidos "
                "(Granger & Newbold, 1974), no por rendimiento sino por supuesto violado.",
                ROJO
            ), md=6, className="mb-3"),
        ]),
    ])

    conclusion = html.Div([
        html.I(className="fas fa-circle-info me-1"),
        "El modelo sugiere que la tasa de Unintentional Injuries en West Virginia continuará aumentando hacia 2022, "
        "profundizando la brecha con el promedio nacional (sección 9.3) y reforzando la necesidad de "
        "intervención prioritaria en salud pública."
    ], style={
        "background": "#e3f2fd", "border": "1px solid #90caf9",
        "borderLeft": "4px solid #1565c0",
        "borderRadius": "6px", "padding": "12px 16px",
        "fontSize": "0.83rem", "color": "#1565c0",
        "lineHeight": "1.6"
    })

    return dbc.Container([
        html.Br(),
        banner,

        # 15.1
        _card_section("fas fa-trophy", "15.1 · Criterios de información — AIC / AICc / BIC", [
            _note("Menor AICc = mejor modelo. Con n = 19, AICc es el criterio apropiado (corrige "
                  "sobreparametrización en muestras pequeñas). Diferencias > 7 pts constituyen evidencia "
                  "fuerte contra el modelo mayor (Burnham & Anderson, 2002)."),
            _dt_table(df_aic, bold_col0=True),
        ]),

        # 15.2
        _card_section("fas fa-circle-check",
                      "15.2 · Diagnóstico comparativo de residuos — Ljung-Box", [
            _note("H₀: residuos independientes. p > 0.05 → ruido blanco (condición necesaria de validez)."),
            _lb_table(df_lb),
        ]),

        # 15.3
        _card_section("fas fa-rotate",
                      "15.3 · Validación cruzada de series de tiempo (tsCV)", [
            _note("Error de predicción fuera de muestra con ventanas de entrenamiento expandidas. "
                  "Horizontes h = 1 (precisión inmediata) y h = 3 (proyección a mediano plazo)."),
            _cv_table(df_cv, best_rmse1_idx),
            nota_cv,
        ]),

        # 15.4
        _card_section("fas fa-chart-line",
                      "15.4 · Gráfico comparativo de proyecciones — Unintentional Injuries", [
            dcc.Graph(figure=fig_comp, config={"displayModeBar": True}),
            nota_fc,
        ]),

        # Sección 16
        html.Br(),
        sec16_header,
        criterios_grid,
        conclusion,
        html.Br(),
    ], fluid=True)
