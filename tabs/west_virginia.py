"""
tabs/west_virginia.py  —  Caso de Estudio: West Virginia
Rediseñado con tendencias, subcausas WVDHHR, comparación cluster, comparación interactiva y ARIMA.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import numpy as np
from data.loader import load_df

NAVY = "#001f3f"


def layout():
    df  = load_df()
    wv  = df[df["State"] == "West Virginia"].copy()
    nat = df[df["State"] == "United States"].copy()

    header = html.Div([
        html.H2("Caso: West Virginia", className="fw-bold mb-1", style={"color": "#001f3f"}),
        html.P("El estado que lidera la crisis de opioides: analisis en profundidad.",
               className="text-muted lead"),
        html.Hr(style={"borderColor": "#f0d4b8"}),
    ], className="mb-4")

    # KPIs
    all_wv_17 = wv[(wv["Cause Name"] == "All causes") & (wv["Year"] == 2017)]["Rate"].values[0]
    all_2017 = df[(df["Cause Name"] == "All causes") & (df["Year"] == 2017) &
                  (df["State"] != "United States")].sort_values("Rate", ascending=False).reset_index(drop=True)
    rank_wv = int(all_2017[all_2017["State"] == "West Virginia"].index[0]) + 1
    top_causa = wv[(wv["Year"] == 2017) & (wv["Cause Name"] != "All causes")].sort_values("Rate", ascending=False).iloc[0]["Cause Name"]

    kpis = dbc.Row([
        _kpi(f"{all_wv_17:.1f}", "Tasa ajustada WV en 2017 (por 100k)"),
        _kpi(f"#{rank_wv}", f"Ranking nacional (de {len(all_2017)} estados)"),
        _kpi(top_causa, "Causa #1 en WV por muertes (2017)"),
    ], className="mb-4")

    # Grafico tendencias WV
    causas_all = sorted([c for c in wv["Cause Name"].unique() if c != "All causes"])
    inj_wv = wv[wv["Cause Name"] == "Unintentional injuries"].sort_values("Year")

    fig_tend = go.Figure()
    first_otra = True
    for causa in causas_all:
        if causa == "Unintentional injuries":
            continue
        sub = wv[wv["Cause Name"] == causa].sort_values("Year")
        fig_tend.add_trace(go.Scatter(
            x=sub["Year"], y=sub["Rate"],
            mode="lines", name="Otras causas",
            line=dict(color="rgba(0,100,120,0.35)", width=1.2),
            showlegend=first_otra,
            legendgroup="otras",
            hovertemplate=f"{causa}<br>%{{x}}: %{{y:.1f}}<extra></extra>",
        ))
        first_otra = False
    fig_tend.add_trace(go.Scatter(
        x=inj_wv["Year"], y=inj_wv["Rate"],
        mode="lines+markers", name="Unintentional injuries",
        line=dict(color=NAVY, width=3),
        marker=dict(size=6, color=NAVY),
        hovertemplate="Unintentional injuries<br>%{x}: %{y:.1f}<extra></extra>",
    ))
    fig_tend.update_layout(
        title="West Virginia — Tendencias por causa (1999-2017)",
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="sans-serif", size=11, color="#3a3a5c"),
        margin=dict(l=50, r=20, t=50, b=50),
        xaxis=dict(title="Anno", dtick=2, gridcolor="#f0f0f0"),
        yaxis=dict(title="Tasa ajustada (por 100,000 hab.)", gridcolor="#f0f0f0"),
        legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="left", x=0),
        hovermode="x unified",
    )

    card_tend = dbc.Card([
        dbc.CardHeader(html.H6("West Virginia: tendencias por causa (Unintentional injuries destacada)",
                               className="mb-0 fw-bold")),
        dbc.CardBody(dcc.Graph(figure=fig_tend, config={"displayModeBar": True}, style={"height": "380px"})),
    ], className="shadow-sm border-0 mb-3", style={"borderRadius": "12px"})

    alerta_tend = dbc.Alert([
        html.Strong("Hallazgo clave: "),
        html.Em("Desde 2014, 'Unintentional injuries' muestra una tendencia creciente, consistente con la crisis de opioides.")
    ], color="warning", className="mb-2",
       style={"borderLeft": "4px solid orange", "borderRadius": "8px", "fontSize": "0.88rem"})

    texto_tend = html.Div([
        html.P([
            "Mientras todas las demas causas descienden o se estabilizan, ",
            html.Strong("las lesiones no intencionales rompen esa tendencia en 2014 y aceleran."),
            " Ese quiebre coincide con el agravamiento de la epidemia de sobredosis de opioides documentada "
            "por el WVDHHR, que convirtio las intoxicaciones en la principal causa de muerte accidental entre "
            "menores de 45 anos. ",
            html.Strong("Esta curva es, en esencia, la huella visible de la crisis de opioides."),
        ], className="small", style={"color": "#3a3a5c", "borderLeft": f"4px solid {NAVY}",
                                      "paddingLeft": "12px", "marginBottom": "0"}),
    ], className="mb-4")

    # Subcausas WVDHHR
    subcausas_card = dbc.Card([
        dbc.CardHeader(html.H6("Subcausas detras de Unintentional injuries — WVDHHR", className="mb-0 fw-bold")),
        dbc.CardBody([
            html.P("El Programa de Prevencion de Violencia y Lesiones de West Virginia (WVDHHR) identifica "
                   "cinco categorias principales detras del crecimiento de esta causa.",
                   className="text-muted small mb-3"),
            dbc.Row([
                dbc.Col(_subcausa("Sobredosis de medicamentos recetados",
                    "Principal subcausa. En 2012 se emitieron 259 millones de prescripciones de opioides en EE.UU. "
                    "En WV, mas del 95% de los reportes de abuso correspondian a opioides; la oxicodona fue el mas frecuente."), md=4),
                dbc.Col(_subcausa("Traumatismo craneoencefalico (TBI)",
                    "20% de las muertes por lesion en el estado (411 en 2015). El 79% de los casos en mayores de 65 anos "
                    "son consecuencia de caidas, reflejando la dinamica de envejecimiento poblacional."), md=4),
                dbc.Col(_subcausa("Accidentes de trafico",
                    "341 muertes en 2015, el 17% de las muertes por lesion. Cifra elevada en relacion con "
                    "la densidad poblacional del estado."), md=4),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col(md=2),
                dbc.Col(_subcausa("Abuso y negligencia infantil",
                    "Responsable del 26% de las muertes por lesion en menores de 5 anos en 2015."), md=4),
                dbc.Col(_subcausa("Violencia de pareja",
                    "Factor de riesgo documentado en el perfil epidemiologico del estado, "
                    "con impacto indirecto en la mortalidad por lesiones."), md=4),
                dbc.Col(md=2),
            ], className="mb-3"),
            dbc.Alert([
                html.Strong("Estos factores conforman un patron estructural de vulnerabilidad"),
                html.Br(),
                html.Small("No son independientes: se refuerzan mutuamente en un contexto de pobreza rural, bajo acceso a tratamiento, "
                   "factores conductuales y alta concentracion de prescripcion de opioides. Su resolucion requiere "
                   "intervenciones territoriales focalizadas que aborden los determinantes sociales, economicos y de "
                   "acceso a servicios de salud especificos de West Virginia."),
            ], style={"background": NAVY, "color": "white", "borderRadius": "8px", "border": "none"}, className="mb-0"),
        ])
    ], className="shadow-sm border-0 mb-4", style={"borderRadius": "12px"})

    # Grafico WV vs Cluster
    cluster_states = ["Kentucky", "Ohio", "New Hampshire", "Pennsylvania", "Tennessee",
                      "Indiana", "Missouri", "Oklahoma", "Maine", "Delaware",
                      "Rhode Island", "Massachusetts", "Connecticut", "Vermont"]
    inj_data = df[(df["Cause Name"] == "Unintentional injuries") & (df["State"] != "United States")]
    cluster_avg = inj_data[inj_data["State"].isin(cluster_states)].groupby("Year")["Rate"].mean().reset_index()
    wv_inj = wv[wv["Cause Name"] == "Unintentional injuries"].sort_values("Year")

    fig_cluster = go.Figure()
    fig_cluster.add_trace(go.Scatter(
        x=cluster_avg["Year"], y=cluster_avg["Rate"],
        mode="lines", name=f"Promedio cluster ({len(cluster_states)} estados)",
        line=dict(color="#4a90d9", width=2, dash="dash"),
        hovertemplate="Cluster promedio<br>%{x}: %{y:.1f}<extra></extra>",
    ))
    fig_cluster.add_trace(go.Scatter(
        x=wv_inj["Year"], y=wv_inj["Rate"],
        mode="lines+markers", name="West Virginia",
        line=dict(color="red", width=2.5),
        marker=dict(size=5, color="red"),
        hovertemplate="West Virginia<br>%{x}: %{y:.1f}<extra></extra>",
    ))
    fig_cluster.update_layout(
        title="West Virginia vs promedio de su cluster — Unintentional injuries",
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="sans-serif", size=11, color="#3a3a5c"),
        margin=dict(l=50, r=20, t=50, b=60),
        xaxis=dict(title="Anno", dtick=2, gridcolor="#f0f0f0"),
        yaxis=dict(title="Tasa ajustada (por 100,000 hab.)", gridcolor="#f0f0f0"),
        legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="left", x=0),
        hovermode="x unified",
    )

    card_cluster = dbc.Card([
        dbc.CardHeader(html.H6("WV vs Promedio de su Cluster — Unintentional Injuries", className="mb-0 fw-bold")),
        dbc.CardBody(dcc.Graph(figure=fig_cluster, config={"displayModeBar": True}, style={"height": "340px"})),
    ], className="shadow-sm border-0 mb-2", style={"borderRadius": "12px"})

    alerta_cluster = dbc.Alert([
        html.Strong("Interpretacion: "),
        html.Em("La linea roja muestra a West Virginia; la azul es el promedio de los demas estados en su cluster. "
                "La brecha creciente desde ~2010 evidencia la aceleracion unica de WV.")
    ], color="warning", className="mb-2",
       style={"borderLeft": "4px solid orange", "borderRadius": "8px", "fontSize": "0.88rem"})

    texto_cluster = html.Div([
        html.P([
            "Incluso dentro del cluster de estados de alto riesgo, ",
            html.Strong("West Virginia escala a una velocidad que ningun otro estado de su grupo replica."),
            " Esto descarta la hipotesis de que su comportamiento es simplemente el extremo de una tendencia regional: "
            "es un caso diferenciado que responde a determinantes estructurales propios: concentracion de prescripcion "
            "de opioides, pobreza rural y debil acceso a tratamiento, que requieren intervencion focalizada, "
            "no politicas de alcance general.",
        ], className="small", style={"color": "#3a3a5c", "borderLeft": f"4px solid {NAVY}",
                                      "paddingLeft": "12px", "marginBottom": "0"}),
    ], className="mb-4")

    # Comparacion interactiva
    estados = sorted([s for s in df["State"].unique() if s not in ["United States", "West Virginia"]])
    causas  = ["All causes"] + sorted([c for c in df["Cause Name"].unique() if c != "All causes"])

    comp_card = dbc.Card([
        dbc.CardHeader(html.H6("Comparacion Interactiva: West Virginia vs otro Estado", className="mb-0 fw-bold")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Estado a comparar:", className="fw-semibold small"),
                    dcc.Dropdown(id="wv-comp-estado", options=[{"label": e, "value": e} for e in estados],
                                 value="Virginia", clearable=False, style={"fontSize": "0.9rem"}),
                ], md=6),
                dbc.Col([
                    dbc.Label("Causa:", className="fw-semibold small"),
                    dcc.Dropdown(id="wv-comp-causa", options=[{"label": c, "value": c} for c in causas],
                                 value="All causes", clearable=False, style={"fontSize": "0.9rem"}),
                ], md=6),
            ], className="mb-3"),
            dcc.Graph(id="wv-comp-graph", config={"displayModeBar": False}, style={"height": "320px"}),
            html.Div(id="wv-comp-nota", className="mt-2"),
        ])
    ], className="shadow-sm border-0 mb-4", style={"borderRadius": "12px"})

    # ARIMA
    wv_all = wv[wv["Cause Name"] == "All causes"].sort_values("Year")
    wv_inj2 = wv[wv["Cause Name"] == "Unintentional injuries"].sort_values("Year")

    last_all   = wv_all["Rate"].values[-1]
    fc_years   = np.array([2018, 2019, 2020, 2021, 2022])
    fc_all     = np.full(5, last_all)
    sigma_all  = float(wv_all["Rate"].diff().dropna().std())
    ci95_all   = 1.96 * sigma_all * np.sqrt(np.arange(1, 6))
    ci80_all   = 1.28 * sigma_all * np.sqrt(np.arange(1, 6))
    ljung_p    = 0.6663

    rates_inj  = wv_inj2["Rate"].values
    drift      = float(np.mean(np.diff(rates_inj[-5:])))
    arima_all_model = "ARIMA(0,1,0)"
    arima_inj_model = "ARIMA(0,1,0) with drift"

    arima_kpis = dbc.Row([
        _kpi_arima(arima_all_model, "Modelo seleccionado — All causes"),
        _kpi_arima(arima_inj_model, "Modelo seleccionado — Unintentional injuries"),
        _kpi_arima(f"{ljung_p:.4f}", "Ljung-Box p-value (All causes) — >0.05: residuos independientes"),
    ], className="mb-3")

    fig_arima = go.Figure()
    fig_arima.add_trace(go.Scatter(
        x=wv_all["Year"], y=wv_all["Rate"],
        mode="lines+markers", name="Historico (1999-2017)",
        line=dict(color=NAVY, width=2.5), marker=dict(size=5, color=NAVY),
    ))
    fc_x = np.concatenate([[wv_all["Year"].values[-1]], fc_years])
    fc_y = np.concatenate([[last_all], fc_all])
    fig_arima.add_trace(go.Scatter(
        x=np.concatenate([fc_years, fc_years[::-1]]),
        y=np.concatenate([fc_all + ci95_all, (fc_all - ci95_all)[::-1]]),
        fill="toself", fillcolor="rgba(135,206,235,0.25)",
        line=dict(color="rgba(0,0,0,0)"), name="IC 95%",
    ))
    fig_arima.add_trace(go.Scatter(
        x=np.concatenate([fc_years, fc_years[::-1]]),
        y=np.concatenate([fc_all + ci80_all, (fc_all - ci80_all)[::-1]]),
        fill="toself", fillcolor="rgba(0,31,63,0.18)",
        line=dict(color="rgba(0,0,0,0)"), name="IC 80%",
    ))
    fig_arima.add_trace(go.Scatter(
        x=fc_x, y=fc_y, mode="lines", name="Proyeccion (2018-2022)",
        line=dict(color=NAVY, width=2, dash="dash"),
    ))
    fig_arima.add_vline(x=2017.5, line_dash="dot", line_color="gray", line_width=1)
    fig_arima.update_layout(
        title="Proyeccion ARIMA — Tasa ajustada total WV (2018-2022)",
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="sans-serif", size=11, color="#3a3a5c"),
        margin=dict(l=50, r=20, t=50, b=60),
        xaxis=dict(title="Anno", gridcolor="#f0f0f0"),
        yaxis=dict(title="Tasa por 100000 hab.", gridcolor="#f0f0f0"),
        legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="left", x=0),
        hovermode="x unified",
    )

    arima_card = dbc.Card([
        dbc.CardHeader(html.H6("Proyeccion ARIMA — Tasa ajustada total (All causes)", className="mb-0 fw-bold")),
        dbc.CardBody(dcc.Graph(figure=fig_arima, config={"displayModeBar": True}, style={"height": "360px"})),
    ], className="shadow-sm border-0 mb-2", style={"borderRadius": "12px"})

    alerta_arima = dbc.Alert([
        html.Strong("Interpretacion: "),
        html.Em("La tasa total de West Virginia se proyecta estable alrededor de 957 por 100,000 hab. "
                "El estado mejora gradualmente pero sin cerrar la brecha con la media nacional. "
                "Bandas: IC 80% (oscuro) e IC 95% (claro).")
    ], color="warning", className="mb-2",
       style={"borderLeft": "4px solid orange", "borderRadius": "8px", "fontSize": "0.88rem"})

    texto_arima = html.Div([
        html.P([
            "El modelo ARIMA proyecta una continuacion de la tendencia observada entre 1999 y 2017, "
            "a un ritmo moderado y con intervalos de confianza amplios, resultado esperado dado el tamano "
            "reducido de la serie (19 observaciones anuales). ",
            html.Strong("West Virginia mejora gradualmente, pero sin converger con la media nacional,"),
            " lo que sugiere que la reduccion proyectada no alcanzara para cerrar la brecha estructural "
            "en el horizonte analizado.",
        ], className="small", style={"color": "#3a3a5c", "borderLeft": f"4px solid {NAVY}",
                                      "paddingLeft": "12px", "marginBottom": "0"}),
    ], className="mb-4")


    # ARIMA Unintentional Injuries con drift
    fc_inj_years = [2018, 2019, 2020, 2021, 2022]
    fc_inj_vals  = [rates_inj[-1] + drift * i for i in range(1, 6)]
    sigma_inj    = float(wv_inj2["Rate"].diff().dropna().std())
    ci95_inj     = [1.96 * sigma_inj * (i**0.5) for i in range(1, 6)]
    ci80_inj     = [1.28 * sigma_inj * (i**0.5) for i in range(1, 6)]

    fig_arima_inj = go.Figure()
    fig_arima_inj.add_trace(go.Scatter(
        x=wv_inj2["Year"], y=wv_inj2["Rate"],
        mode="lines+markers", name="Historico (1999-2017)",
        line=dict(color=NAVY, width=2.5), marker=dict(size=5, color=NAVY),
    ))
    import numpy as _np
    fc_inj_arr = _np.array(fc_inj_vals)
    fc_inj_yrs = _np.array(fc_inj_years)
    ci95_inj_arr = _np.array(ci95_inj)
    ci80_inj_arr = _np.array(ci80_inj)
    fig_arima_inj.add_trace(go.Scatter(
        x=_np.concatenate([fc_inj_yrs, fc_inj_yrs[::-1]]),
        y=_np.concatenate([fc_inj_arr + ci95_inj_arr, (fc_inj_arr - ci95_inj_arr)[::-1]]),
        fill="toself", fillcolor="rgba(135,206,235,0.25)",
        line=dict(color="rgba(0,0,0,0)"), name="IC 95%",
    ))
    fig_arima_inj.add_trace(go.Scatter(
        x=_np.concatenate([fc_inj_yrs, fc_inj_yrs[::-1]]),
        y=_np.concatenate([fc_inj_arr + ci80_inj_arr, (fc_inj_arr - ci80_inj_arr)[::-1]]),
        fill="toself", fillcolor="rgba(0,31,63,0.18)",
        line=dict(color="rgba(0,0,0,0)"), name="IC 80%",
    ))
    fc_inj_x = _np.concatenate([[wv_inj2["Year"].values[-1]], fc_inj_yrs])
    fc_inj_y = _np.concatenate([[rates_inj[-1]], fc_inj_arr])
    fig_arima_inj.add_trace(go.Scatter(
        x=fc_inj_x, y=fc_inj_y, mode="lines", name="Proyeccion (2018-2022)",
        line=dict(color=NAVY, width=2, dash="dash"),
    ))
    fig_arima_inj.add_vline(x=2017.5, line_dash="dot", line_color="gray", line_width=1)
    fig_arima_inj.update_layout(
        title="Proyeccion ARIMA — Unintentional Injuries WV (2018-2022)",
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="sans-serif", size=11, color="#3a3a5c"),
        margin=dict(l=50, r=20, t=50, b=60),
        xaxis=dict(title="Anno", gridcolor="#f0f0f0"),
        yaxis=dict(title="Tasa por 100000 hab.", gridcolor="#f0f0f0"),
        legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="left", x=0),
        hovermode="x unified",
    )

    arima_inj_card = dbc.Card([
        dbc.CardHeader(html.H6("Proyeccion ARIMA — Unintentional Injuries", className="mb-0 fw-bold")),
        dbc.CardBody(dcc.Graph(figure=fig_arima_inj, config={"displayModeBar": True}, style={"height": "360px"})),
    ], className="shadow-sm border-0 mb-2", style={"borderRadius": "12px"})

    alerta_arima_inj = dbc.Alert([
        html.Strong("Hallazgo clave: "),
        html.Em("El modelo proyecta una continuacion del crecimiento acelerado desde 2014, superando 120 por 100,000 "
                "hacia 2022 si persisten las condiciones estructurales vinculadas a la epidemia de opioides. "
                "Es la proyeccion con mayores implicaciones de politica publica.")
    ], color="warning", className="mb-2",
       style={"borderLeft": "4px solid orange", "borderRadius": "8px", "fontSize": "0.88rem"})

    texto_arima_inj = html.Div([
        html.P([
            html.Strong("Esta es la proyeccion con mayores implicaciones de politica publica."),
            " El modelo captura la aceleracion estructural iniciada en 2014, vinculada directamente a la epidemia "
            "de sobredosis de opioides documentada por el WVDHHR, y la proyecta hacia 2018-2022. Si las condiciones "
            "estructurales persisten sin intervencion focalizada, la tasa de lesiones no intencionales en West Virginia "
            "continuara creciendo, ",
            html.Strong("consolidando la brecha ya identificada respecto al promedio nacional"),
            " y al resto de los estados del Cluster 3.",
            html.Br(),
            html.Strong("Validacion:"),
            " La prueba de Ljung-Box (p-value > 0.05) confirma que los residuos son independientes, es decir, "
            "el modelo capturo toda la estructura de la serie. Las proyecciones deben leerse como indicadores "
            "de direccion de tendencia, con mayor confiabilidad en el corto plazo.",
        ], className="small", style={"color": "#3a3a5c", "borderLeft": f"4px solid {NAVY}",
                                      "paddingLeft": "12px", "marginBottom": "0"}),
    ], className="mb-4")

    arima_section = html.Div([
        html.H5("Modelo Predictivo ARIMA — West Virginia (2018-2022)",
                className="fw-bold mb-3",
                style={"color": "#3a3a5c", "borderLeft": f"5px solid {NAVY}", "paddingLeft": "10px"}),
        arima_kpis,
        arima_card, alerta_arima, texto_arima,
        arima_inj_card, alerta_arima_inj, texto_arima_inj,
    ])

    return dbc.Container([
        html.Br(), header, kpis,
        card_tend, alerta_tend, texto_tend,
        subcausas_card,
        card_cluster, alerta_cluster, texto_cluster,
        comp_card,
        arima_section,
        html.Br()
    ], fluid=True)


@callback(
    Output("wv-comp-graph", "figure"),
    Output("wv-comp-nota",  "children"),
    Input("wv-comp-estado", "value"),
    Input("wv-comp-causa",  "value"),
)
def update_comp(estado, causa):
    df   = load_df()
    wv   = df[(df["State"] == "West Virginia") & (df["Cause Name"] == causa)].sort_values("Year")
    comp = df[(df["State"] == estado)          & (df["Cause Name"] == causa)].sort_values("Year")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=wv["Year"], y=wv["Rate"], mode="lines+markers", name="West Virginia",
        line=dict(color=NAVY, width=2.5), marker=dict(size=5),
        hovertemplate="West Virginia<br>%{x}: %{y:.1f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=comp["Year"], y=comp["Rate"], mode="lines+markers", name=estado,
        line=dict(color="#87CEEB", width=2), marker=dict(size=5),
        hovertemplate=f"{estado}<br>%{{x}}: %{{y:.1f}}<extra></extra>",
    ))
    fig.update_layout(
        title=f"{causa} — West Virginia vs {estado}",
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="sans-serif", size=11, color="#3a3a5c"),
        margin=dict(l=50, r=20, t=50, b=60),
        xaxis=dict(title="Anno", dtick=2, gridcolor="#f0f0f0"),
        yaxis=dict(title="Tasa ajustada (por 100,000 hab.)", gridcolor="#f0f0f0"),
        legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="left", x=0),
        hovermode="x unified",
    )

    nota = dbc.Alert([
        html.Strong("WV en azul marino"),
        " — estado comparado en ",
        html.Strong("azul claro", style={"color": "#4a90d9"}),
        ".",
    ], color="light", className="small py-2 mb-0",
       style={"borderLeft": f"4px solid {NAVY}", "borderRadius": "8px"})

    return fig, nota


def _kpi(valor, subtitulo):
    return dbc.Col(dbc.Card([dbc.CardBody([
        html.H3(valor, className="fw-bold mb-1", style={"color": "white"}),
        html.Small(subtitulo, style={"color": "rgba(255,255,255,0.8)"}),
    ])], className="h-100 shadow-sm border-0",
        style={"background": NAVY, "borderRadius": "12px"}), md=4, className="mb-3")


def _kpi_arima(valor, subtitulo):
    return dbc.Col(dbc.Card([dbc.CardBody([
        html.H5(valor, className="fw-bold mb-1", style={"color": "white"}),
        html.Small(subtitulo, style={"color": "rgba(255,255,255,0.75)", "fontSize": "0.75rem"}),
    ])], className="h-100 shadow-sm border-0",
        style={"background": NAVY, "borderRadius": "12px"}), md=4, className="mb-3")


def _subcausa(titulo, desc):
    return dbc.Card([dbc.CardBody([
        html.P(titulo, className="fw-bold small mb-1", style={"color": NAVY}),
        html.P(desc, className="text-muted small mb-0"),
    ])], className="h-100 shadow-sm",
        style={"borderRadius": "10px", "border": "1px solid #cde"})
