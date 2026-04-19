"""
tabs/metodologia.py  —  Metodología del análisis
"""
import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.graph_objects as go
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from data.loader import load_df


def layout():
    df = load_df()

    header = html.Div([
        html.H2(" Metodología", className="fw-bold mb-1", style={"color": "#001f3f"}),
        html.P("Descripción del dataset, proceso de limpieza y decisiones analíticas.",
               className="text-muted lead"),
        html.Hr(style={"borderColor": "#f7c5e0"}),
    ], className="mb-4")

    # KPIs del dataset
    n_filas   = len(df)
    n_estados = df[df["State"] != "United States"]["State"].nunique()
    n_causas  = df[df["Cause Name"] != "All causes"]["Cause Name"].nunique()
    anos      = f"{df['Year'].min()}–{df['Year'].max()}"

    kpis = dbc.Row([
        _kpi("", "Registros totales",    f"{n_filas:,}",   "#001f3f"),
        _kpi("", "Rango temporal",        anos,             "#001f3f"),
        _kpi("", "Estados + D.C.",        str(n_estados),  "#001f3f"),
        _kpi("", "Causas de muerte",      str(n_causas),   "#001f3f"),
    ], className="mb-4")

    fuente = dbc.Card([
        dbc.CardHeader(html.H5(" Fuente y Acceso al Dataset",
                               className="mb-0 fw-bold", style={"color": "white"})),
        dbc.CardBody(dbc.Row([
            dbc.Col([
                html.H6("NCHS — data.cdc.gov", className="fw-semibold", style={"color": "#5a4fcf"}),
                html.P([
                    "Dataset público disponible en ",
                    html.A("data.cdc.gov/NCHS/bi63-dtpu",
                           href="https://data.cdc.gov/National-Center-for-Health-Statistics/NCHS-Leading-Causes-of-Death-United-States/bi63-dtpu",
                           target="_blank"),
                    ". Publicado bajo dominio público; no requiere licencia especial para uso académico o investigativo."
                ], className="text-muted small"),
                html.H6("Proceso de Limpieza", className="fw-semibold mt-3", style={"color": "#5a4fcf"}),
                html.Ul([
                    html.Li("Separadores de miles con punto (ej. '1.234') convertidos a enteros."),
                    html.Li("Separador decimal con coma ('3,6') convertido a punto flotante."),
                    html.Li("Casos con tasa nula imputados como NaN (supresión por privacidad en conteos < 20)."),
                    html.Li("Variable 'StateCode' derivada para mapas coropléticos."),
                ], className="text-muted small"),
            ], md=6),
            dbc.Col([
                html.H6("Decisiones Analíticas", className="fw-semibold", style={"color": "#5a4fcf"}),
                dbc.Table([html.Tbody([
                    html.Tr([html.Td("Métrica principal"),   html.Td(html.Strong("Age-adjusted Death Rate"))]),
                    html.Tr([html.Td("Métrica secundaria"),  html.Td(html.Strong("Deaths (valor absoluto)"))]),
                    html.Tr([html.Td("Nivel nacional"),      html.Td(html.Strong("State = 'United States'"))]),
                    html.Tr([html.Td("Nivel estatal"),       html.Td(html.Strong("State ≠ 'United States'"))]),
                    html.Tr([html.Td("Deaths of Despair"),   html.Td(html.Strong("Suicide + Unintentional injuries"))]),
                    html.Tr([html.Td("Caso de estudio"),     html.Td(html.Strong("West Virginia (mayor tasa nacional)"))]),
                    html.Tr([html.Td("Tipo de análisis"),    html.Td(html.Strong("Descriptivo / exploratorio"))]),
                    html.Tr([html.Td("Software"),            html.Td(html.Strong("Python · Dash · Plotly · Pandas"))]),
                ])], size="sm", className="small")
            ], md=6),
        ]))
    ], className="shadow-sm border-0 mb-4", style={"borderRadius": "12px"})

    # Distribución de muertes totales nacionales por causa (barh)
    nat = df[(df["State"] == "United States") & (df["Cause Name"] != "All causes")]
    causa_total = nat.groupby("Cause Name")["Deaths"].sum().sort_values()

    fig_bar = go.Figure(go.Bar(
        x=causa_total.values,
        y=causa_total.index,
        orientation="h",
        marker_color="#001f3f",  # azul cielo uniforme
        text=[f"{v:,.0f}" for v in causa_total.values],
        textposition="inside",
        insidetextanchor="end",
        textfont=dict(color="white", size=11),
    ))
    fig_bar.update_layout(
        title="Total de Muertes 1999–2017 por Causa (nivel nacional)",
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="sans-serif", size=11, color="#3a3a5c"),
        margin=dict(l=180, r=120, t=50, b=40),
        height=420,
        xaxis=dict(title="Total muertes acumuladas", fixedrange=True),
        yaxis=dict(fixedrange=True),
        dragmode=False,
    )

    grafico = dbc.Card([
        dbc.CardHeader(html.H6("Total de Muertes 1999–2017 por Causa (nivel nacional)", className="mb-0 fw-bold")),
        dbc.CardBody(dcc.Graph(figure=fig_bar, config={"displayModeBar": False, "staticPlot": True}), className="p-2"),
    ], className="shadow-sm border-0 mb-4", style={"borderRadius": "12px"}
    )

    return dbc.Container([html.Br(), header, kpis, fuente, grafico, html.Br()], fluid=True)


def _kpi(icon, titulo, valor, bg):
    return dbc.Col(dbc.Card([dbc.CardBody([
        html.Div(icon, className="fs-2 mb-1"),
        html.H6(titulo, className="small", style={"color": "white"}),
        html.H4(valor, className="fw-bold mb-0", style={"color": "white"}),
    ], className="text-center")], className="h-100 shadow-sm border-0",
        style={"background": bg, "borderRadius": "12px"}), md=3, className="mb-3")
