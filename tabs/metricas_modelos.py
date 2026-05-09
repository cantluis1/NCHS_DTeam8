"""
tabs/metricas_modelos.py — Métricas de Modelos (ARIMA Diagnóstico Completo)
Secciones 11 y 15. Sin emojis. Todo pre-computado en layout().
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.stats.diagnostic import acorr_ljungbox
from sklearn.linear_model import LinearRegression
from data.loader import load_df

NAVY = "#1D3557"
AZUL = "#457B9D"
ROJO = "#E63946"


def _get_series():
    df = load_df()
    df_acc = df[(df["State"] == "West Virginia") & (df["Cause Name"] == "Unintentional injuries")].sort_values("Year")
    df_tot = df[(df["State"] == "West Virginia") & (df["Cause Name"] == "All causes")].sort_values("Year")
    return df_acc["Rate"].dropna().values, df_tot["Rate"].dropna().values


def _card(title, children, note=None):
    return html.Div([
        html.Div(html.Strong(title, style={"color": NAVY}),
                 style={"fontSize": "0.92rem", "fontWeight": "700", "marginBottom": "14px",
                        "paddingBottom": "10px", "borderBottom": "2px solid #f0f4fa"}),
        *children,
        *([html.Div([html.Strong("Interpretación: "), note],
                    style={"background": "#f4f7fb", "borderLeft": f"3px solid {AZUL}",
                           "borderRadius": "0 6px 6px 0", "padding": "8px 12px",
                           "fontSize": "0.8rem", "color": "#4a5568", "marginTop": "12px"})] if note else [])
    ], style={
        "background": "#fff", "border": "1px solid #e2e8f2",
        "borderTop": f"3px solid {NAVY}",
        "borderRadius": "10px", "boxShadow": "0 1px 8px rgba(0,0,0,0.05)",
        "padding": "18px", "marginBottom": "18px"
    })


def _note(text):
    return html.P(text, style={"fontSize": "0.85rem", "color": "#555", "marginBottom": "14px"})


def layout():
    serie_acc, serie_tot = _get_series()
    n = len(serie_acc)

    # trend="t" es el drift correcto para ARIMA(0,1,0) en statsmodels
    arima_acc  = ARIMA(serie_acc, order=(0, 1, 0), trend="t").fit()
    arima_tot  = ARIMA(serie_tot, order=(0, 1, 0), trend="t").fit()
    ets_acc    = ExponentialSmoothing(serie_acc, trend="mul",  seasonal=None, initialization_method="estimated").fit()
    holt_acc   = ExponentialSmoothing(serie_acc, trend="add",  seasonal=None, initialization_method="estimated").fit()
    holtd_acc  = ExponentialSmoothing(serie_acc, trend="add",  seasonal=None, damped_trend=True,
                                      initialization_method="estimated").fit()

    def aicc(fit_obj, k):
        return fit_obj.aic + (2 * k * (k + 1)) / max(1, n - k - 1)

    # 11.2 ADF
    adf_tot = adfuller(serie_tot, autolag="AIC")
    adf_acc = adfuller(serie_acc, autolag="AIC")
    df_adf = pd.DataFrame({
        "Serie": ["WV – All causes", "WV – Unintentional injuries"],
        "Estadístico ADF": [round(adf_tot[0], 4), round(adf_acc[0], 4)],
        "Valor-p": [round(adf_tot[1], 4), round(adf_acc[1], 4)],
        "Resultado": ["Estacionaria" if adf_tot[1] < 0.05 else "No estacionaria",
                      "Estacionaria" if adf_acc[1] < 0.05 else "No estacionaria"],
    })

    # 11.3 ACF / PACF
    ml_acf  = min(12, n - 2)         # ACF: hasta 12 lags
    ml_pacf = min(12, n // 2 - 1)    # PACF: límite statsmodels < n/2
    ic      = 1.96 / np.sqrt(n)
    lags_acf  = np.arange(ml_acf + 1)
    lags_pacf = np.arange(ml_pacf + 1)

    fig_acf = make_subplots(rows=2, cols=2,
                            subplot_titles=["ACF – WV All causes", "PACF – WV All causes",
                                            "ACF – WV Unintentional Injuries", "PACF – WV Unintentional Injuries"])
    pairs = [
        (acf(serie_tot, nlags=ml_acf,  fft=True), lags_acf,  NAVY, 1, 1),
        (pacf(serie_tot, nlags=ml_pacf),           lags_pacf, NAVY, 1, 2),
        (acf(serie_acc, nlags=ml_acf,  fft=True), lags_acf,  ROJO, 2, 1),
        (pacf(serie_acc, nlags=ml_pacf),           lags_pacf, ROJO, 2, 2),
    ]
    for vals, lags_v, color, r, c in pairs:
        for lag, val in zip(lags_v, vals):
            fig_acf.add_trace(go.Scatter(x=[lag, lag], y=[0, val], mode="lines",
                                         line=dict(color=color, width=2.5), showlegend=False), row=r, col=c)
            fig_acf.add_trace(go.Scatter(x=[lag], y=[val], mode="markers",
                                         marker=dict(color=color, size=5), showlegend=False), row=r, col=c)
        fig_acf.add_hline(y= ic, line=dict(color="blue", dash="dash", width=1.2), row=r, col=c)
        fig_acf.add_hline(y=-ic, line=dict(color="blue", dash="dash", width=1.2), row=r, col=c)
        fig_acf.add_hline(y= 0,  line=dict(color="#aaa", width=0.8),              row=r, col=c)
    fig_acf.update_layout(height=460, plot_bgcolor="#FAFAFA", paper_bgcolor="rgba(0,0,0,0)",
                          showlegend=False, font=dict(family="Segoe UI, Helvetica Neue, Arial, sans-serif", size=11))
    fig_acf.update_xaxes(title_text="Lag", showgrid=False)
    fig_acf.update_yaxes(title_text="ACF",  row=1, col=1)
    fig_acf.update_yaxes(title_text="Partial ACF", row=1, col=2)
    fig_acf.update_yaxes(title_text="ACF",  row=2, col=1)
    fig_acf.update_yaxes(title_text="Partial ACF", row=2, col=2)

    # 11.4 Selección
    df_mod = pd.DataFrame({
        "Serie":   ["WV – All causes", "WV – Unintentional injuries"],
        "Modelo":  ["ARIMA(0,1,0) with drift"] * 2,
        "AIC":     [round(arima_tot.aic, 2), round(arima_acc.aic, 2)],
        "Sigma²":  [round(float(np.var(arima_tot.resid)), 4), round(float(np.var(arima_acc.resid)), 4)],
    })
    summary_tot = (f"Modelo   : ARIMA(0,1,0) with drift\n"
                   f"AIC      : {arima_tot.aic:.2f}\n"
                   f"BIC      : {arima_tot.bic:.2f}\n"
                   f"Sigma²   : {float(np.var(arima_tot.resid)):.4f}\n"
                   f"Drift    : {float(arima_tot.params[0]):.4f}")
    summary_acc_str = (f"Modelo   : ARIMA(0,1,0) with drift\n"
                       f"AIC      : {arima_acc.aic:.2f}\n"
                       f"BIC      : {arima_acc.bic:.2f}\n"
                       f"Sigma²   : {float(np.var(arima_acc.resid)):.4f}\n"
                       f"Drift    : {float(arima_acc.params[0]):.4f}")

    # 11.5 Residuos — estilo checkresiduals(): 3 paneles por modelo
    def _checkres_fig(res, años_r, color, title):
        ml_r  = min(12, len(res) - 2)          # R default: floor(10*log10(n)), ~12 for n=18
        ic_r  = 1.96 / np.sqrt(len(res))       # confianza al 95% (idéntico a R)
        lags_r = np.arange(1, ml_r + 1)        # R omite lag 0 en checkresiduals ACF
        acf_r  = acf(res, nlags=ml_r, fft=True)[1:]   # skip lag 0 (always 1.0)
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=["Residuos en el tiempo", "ACF de residuos", "Distribución"],
            column_widths=[0.45, 0.30, 0.25],
        )
        # Panel 1: residuos
        for t, rv in zip(años_r, res):
            fig.add_trace(go.Scatter(x=[t, t], y=[0, rv], mode="lines",
                                     line=dict(color=color, width=2), showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=años_r, y=res, mode="markers",
                                  marker=dict(color=color, size=4), showlegend=False), row=1, col=1)
        fig.add_hline(y=0, line=dict(color="#333", dash="dot", width=1), row=1, col=1)
        # Panel 2: ACF (lag 0 omitido, como R checkresiduals)
        for lag, val in zip(lags_r, acf_r):
            fig.add_trace(go.Scatter(x=[lag, lag], y=[0, val], mode="lines",
                                     line=dict(color=color, width=2.5), showlegend=False), row=1, col=2)
            fig.add_trace(go.Scatter(x=[lag], y=[val], mode="markers",
                                     marker=dict(color=color, size=5), showlegend=False), row=1, col=2)
        fig.add_hline(y= ic_r, line=dict(color="blue", dash="dash", width=1.2), row=1, col=2)
        fig.add_hline(y=-ic_r, line=dict(color="blue", dash="dash", width=1.2), row=1, col=2)
        fig.add_hline(y=0,     line=dict(color="#aaa", width=0.8), row=1, col=2)
        # Panel 3: histograma
        fig.add_trace(go.Histogram(x=res, nbinsx=7,
                                   marker=dict(color=color, opacity=0.75,
                                   line=dict(color="white", width=0.5)), showlegend=False), row=1, col=3)
        fig.update_layout(
            title=dict(text=f"<b>{title}</b>", font=dict(size=12, color=color), x=0),
            height=260, plot_bgcolor="#FAFAFA", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=50, b=30, l=30, r=10),
            font=dict(family="Segoe UI, Helvetica Neue, Arial, sans-serif", size=10),
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="#eee")
        return fig

    # ARIMA(0,1,0) residual[0] = valor inicial (sin predicción) → se omite igual que R checkresiduals()
    res_tot_plot = np.array(arima_tot.resid)[1:]
    res_acc_plot = np.array(arima_acc.resid)[1:]
    años_tot_r   = np.arange(2000, 2000 + len(res_tot_plot))
    años_acc_r   = np.arange(2000, 2000 + len(res_acc_plot))
    fig_res_tot  = _checkres_fig(res_tot_plot, años_tot_r, NAVY, "Residuos – WV All causes")
    fig_res_acc  = _checkres_fig(res_acc_plot, años_acc_r, ROJO, "Residuos – WV Unintentional Injuries")

    # 15.1 AIC/AICc/BIC
    k_a, k_e, k_h, k_hd = 1, 3, 3, 4
    df_aic = pd.DataFrame({
        "Modelo":     ["ARIMA(0,1,0) with drift", "ETS (Holt multiplicativo)",
                       "Holt lineal ETS(A,A,N)", "Holt amortiguado ETS(A,Ad,N)"],
        "Parámetros": [k_a, k_e, k_h, k_hd],
        "AIC":  [round(arima_acc.aic, 2), round(ets_acc.aic, 2),
                 round(holt_acc.aic, 2),  round(holtd_acc.aic, 2)],
        "AICc": [round(aicc(arima_acc, k_a), 2), round(aicc(ets_acc, k_e), 2),
                 round(aicc(holt_acc, k_h), 2),  round(aicc(holtd_acc, k_hd), 2)],
        "BIC":  [round(arima_acc.bic, 2), round(ets_acc.bic, 2),
                 round(holt_acc.bic, 2),  round(holtd_acc.bic, 2)],
    })
    mejor_aicc_val = df_aic["AICc"].min()
    mejor_mod      = df_aic.loc[df_aic["AICc"].idxmin(), "Modelo"]
    box_mejor = html.Div([
        html.Strong(f"Modelo con menor AICc: {mejor_mod}"), html.Br(),
        f"AICc = {mejor_aicc_val:.2f} — el valor más bajo entre todos los modelos evaluados. "
        "Diferencias > 7 puntos constituyen evidencia fuerte (Burnham & Anderson, 2002)."
    ], style={"background": "#D1FAE5", "border": "1px solid #6EE7B7",
              "borderRadius": "6px", "padding": "12px 16px", "fontSize": "0.85rem"})

    # 15.2 Ljung-Box
    t_hist = np.arange(n)
    lm_obj = LinearRegression().fit(t_hist.reshape(-1, 1), serie_acc)
    res_lm = serie_acc - lm_obj.predict(t_hist.reshape(-1, 1))

    def _lb(res):
        r = acorr_ljungbox(res, lags=[4], return_df=True)
        return float(r["lb_stat"].iloc[0]), float(r["lb_pvalue"].iloc[0])

    lbs = [_lb(arima_acc.resid), _lb(ets_acc.resid),
           _lb(holt_acc.resid),  _lb(holtd_acc.resid), _lb(res_lm)]
    df_lb = pd.DataFrame({
        "Modelo":    ["ARIMA(0,1,0)+drift", "ETS", "Holt lineal", "Holt amortiguado", "Regresión lineal"],
        "Q*":        [round(r[0], 4) for r in lbs],
        "df":        [4] * 5,
        "p-value":   [round(r[1], 4) for r in lbs],
        "Resultado": ["Ruido blanco" if r[1] > 0.05 else "Autocorrelación" for r in lbs],
    })

    # 15.3 tsCV — 6 modelos igual que en Shiny
    def _tscv(serie, h, fn):
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

    def fn_arima(tr, h):
        return list(ARIMA(tr, order=(0, 1, 0), trend="t").fit().get_forecast(h).predicted_mean)

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
        # Random walk with drift: drift = mean of first differences
        diff_mean = float(np.mean(np.diff(tr)))
        last_val  = float(tr[-1])
        return [last_val + diff_mean * step for step in range(1, h + 1)]

    def fn_lm(tr, h):
        return list(LinearRegression()
                    .fit(np.arange(len(tr)).reshape(-1, 1), tr)
                    .predict(np.arange(len(tr), len(tr) + h).reshape(-1, 1)))

    r1a  = _tscv(serie_acc, 1, fn_arima); r3a  = _tscv(serie_acc, 3, fn_arima)
    r1e  = _tscv(serie_acc, 1, fn_ets);   r3e  = _tscv(serie_acc, 3, fn_ets)
    r1h  = _tscv(serie_acc, 1, fn_holt);  r3h  = _tscv(serie_acc, 3, fn_holt)
    r1hd = _tscv(serie_acc, 1, fn_holtd); r3hd = _tscv(serie_acc, 3, fn_holtd)
    r1n  = _tscv(serie_acc, 1, fn_naive); r3n  = _tscv(serie_acc, 3, fn_naive)
    r1l  = _tscv(serie_acc, 1, fn_lm);    r3l  = _tscv(serie_acc, 3, fn_lm)

    df_cv = pd.DataFrame({
        "Modelo":   ["ARIMA(0,1,0) with drift", "ETS", "Holt lineal",
                     "Holt amortiguado", "Naive with drift", "Regresión Lineal"],
        "RMSE h=1": [r1a[0],  r1e[0],  r1h[0],  r1hd[0],  r1n[0],  r1l[0]],
        "MAE h=1":  [r1a[1],  r1e[1],  r1h[1],  r1hd[1],  r1n[1],  r1l[1]],
        "RMSE h=3": [r3a[0],  r3e[0],  r3h[0],  r3hd[0],  r3n[0],  r3l[0]],
        "MAE h=3":  [r3a[1],  r3e[1],  r3h[1],  r3hd[1],  r3n[1],  r3l[1]],
    })

    # ── Encabezado ─────────────────────────────────────────────────────────
    header = html.Div([
        html.Span("Modelo 1 · Serie Temporal", style={
            "display": "inline-block", "background": "rgba(255,255,255,0.12)",
            "border": "1px solid rgba(255,255,255,0.2)", "color": "#a8d8f0",
            "fontSize": "0.72rem", "fontWeight": "700", "letterSpacing": "1.2px",
            "textTransform": "uppercase", "padding": "3px 10px",
            "borderRadius": "20px", "marginBottom": "10px"
        }),
        html.H3("ARIMA: Métricas y Diagnóstico",
                style={"color": "#fff", "fontWeight": "800", "margin": "0 0 6px"}),
        html.P("Diagnóstico completo del modelo ARIMA aplicado a West Virginia (1999–2017). "
               "Incluye prueba ADF, identificación del orden, selección automática, "
               "diagnóstico de residuos y comparación de criterios de información.",
               style={"color": "rgba(255,255,255,0.72)", "fontSize": "0.875rem",
                      "lineHeight": "1.55", "margin": "0", "maxWidth": "720px"}),
    ], style={"background": "linear-gradient(135deg, #0f2340 0%, #1D3557 60%, #2a4a72 100%)",
              "borderRadius": "14px", "padding": "22px 28px", "marginBottom": "22px",
              "boxShadow": "0 4px 20px rgba(29,53,87,0.18)"})

    tabs = dbc.Tabs([
        dbc.Tab(label="Estacionariedad (ADF)", tab_id="adf", children=[
            html.Br(),
            _card("11.2 – Prueba Dickey-Fuller Aumentada (ADF)", [
                _note("La hipótesis nula establece raíz unitaria (serie no estacionaria). "
                      "Un valor-p < 0.05 permite rechazarla."),
                dbc.Table.from_dataframe(df_adf, striped=True, bordered=True, hover=True, className="table-sm"),
            ])
        ]),
        dbc.Tab(label="ACF / PACF", tab_id="acf", children=[
            html.Br(),
            _card("11.3 – ACF y PACF – Identificación visual del orden", [
                _note("Un corte abrupto en PACF tras lag 1 sugiere AR(1); un corte en ACF sugiere MA(1)."),
                dcc.Graph(figure=fig_acf, config={"displayModeBar": False}),
            ])
        ]),
        dbc.Tab(label="Selección del Modelo", tab_id="seleccion", children=[
            html.Br(),
            _card("11.4 – Selección automática", [
                _note("Búsqueda minimizando AIC. Se muestran el modelo seleccionado y sus parámetros."),
                dbc.Table.from_dataframe(df_mod, striped=True, bordered=True, hover=True, className="table-sm"),
                html.Br(),
                html.H6("Resumen – WV All causes", style={"color": AZUL, "fontWeight": "700"}),
                html.Pre(summary_tot, style={"background": "#f4f7fb", "borderRadius": "6px",
                                             "padding": "12px", "fontSize": "0.82rem"}),
                html.H6("Resumen – WV Unintentional Injuries",
                        style={"color": ROJO, "fontWeight": "700", "marginTop": "12px"}),
                html.Pre(summary_acc_str, style={"background": "#f4f7fb", "borderRadius": "6px",
                                                 "padding": "12px", "fontSize": "0.82rem"}),
            ])
        ]),
        dbc.Tab(label="Diagnóstico de Residuos", tab_id="residuos", children=[
            html.Br(),
            _card("11.5 – Diagnóstico de residuos", [
                _note("Los residuos deben comportarse como ruido blanco: sin patrones, "
                      "sin autocorrelación y p-value de Ljung-Box > 0.05."),
                dcc.Graph(figure=fig_res_tot, config={"displayModeBar": False}),
                html.Div(style={"height": "10px"}),
                dcc.Graph(figure=fig_res_acc, config={"displayModeBar": False}),
            ])
        ]),
        dbc.Tab(label="AIC / AICc / BIC", tab_id="aic", children=[
            html.Br(),
            _card("15.1 – Criterios de información (modelos paramétricos)", [
                _note("El AICc es la métrica preferida cuando n < 40. "
                      "Diferencias > 7 puntos en AICc constituyen evidencia fuerte."),
                dbc.Table.from_dataframe(df_aic, striped=True, bordered=True, hover=True, className="table-sm"),
                html.Br(),
                box_mejor,
            ])
        ]),
        dbc.Tab(label="Ljung-Box", tab_id="ljung", children=[
            html.Br(),
            _card("15.2 – Diagnóstico comparativo de residuos (Ljung-Box, lag=4)", [
                _note("Un p-value > 0.05 es condición necesaria de validez."),
                dbc.Table.from_dataframe(df_lb, striped=True, bordered=True, hover=True, className="table-sm"),
            ])
        ]),
        dbc.Tab(label="tsCV", tab_id="tscv", children=[
            html.Br(),
            _card("15.3 – Validación cruzada de series de tiempo (tsCV)", [
                _note("Evaluación del error de predicción fuera de muestra. "
                      "Se reportan RMSE y MAE para horizontes h=1 y h=3."),
                dbc.Table.from_dataframe(df_cv, striped=True, bordered=True, hover=True, className="table-sm"),
            ])
        ]),
    ], active_tab="adf",
       style={"background": "#fff", "borderRadius": "14px",
              "boxShadow": "0 2px 16px rgba(0,0,0,0.07)", "padding": "0 4px"})

    return dbc.Container([html.Br(), header, tabs, html.Br()], fluid=True)
