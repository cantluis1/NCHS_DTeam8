"""
tabs/marco_teorico.py  —  Marco Teórico e ICD-10  (sin emojis)
"""
import dash_bootstrap_components as dbc
from dash import html


def layout():
    header = html.Div([
        html.H2("Marco Teórico", className="fw-bold mb-1", style={"color": "#001f3f"}),
        html.P("Fundamentos conceptuales, clasificación ICD-10 y operacionalización de variables.",
               className="text-muted lead"),
        html.Hr(style={"borderColor": "#001f3f"}),
    ], className="mb-4")

    conceptos = dbc.Card([
        dbc.CardHeader(html.H5("Conceptos Clave", className="mb-0 fw-bold", style={"color": "white"})),
        dbc.CardBody(dbc.Row([
            dbc.Col(_concepto("1", "Tasa de mortalidad ajustada por año",
                "Mide la frecuencia de muertes en una población normalizada a la estructura "
                "etaria estándar de EE.UU. (año 2000). Expresada por cada 100,000 habitantes. "
                "Permite comparar estados y años sin el sesgo de pirámides poblacionales distintas.",
                "#5a4fcf"), md=4),
            dbc.Col(_concepto("2", "NCHS — National Center for Health Statistics",
                "Organismo federal bajo el CDC responsable de recopilar y analizar datos "
                "sobre la salud de la población estadounidense. El NVSS (National Vital "
                "Statistics System) es su fuente primaria para mortalidad.",
                "#c94f8a"), md=4),
            dbc.Col(_concepto("3", "Deaths of Despair",
                "Concepto acuñado por Anne Case y Angus Deaton (2015) para describir muertes "
                "por suicidio, sobredosis de drogas/alcohol e hígado alcohólico. Asociadas al "
                "deterioro socioeconómico de clases trabajadoras blancas en EE.UU.",
                "#2d7a4f"), md=4),
        ], className="g-3"))
    ], className="shadow-sm border-0 mb-4", style={"borderRadius": "12px"})

    icd_card = dbc.Card([
        dbc.CardHeader(html.H5("Clasificación ICD-10 de las Causas Analizadas",
                               className="mb-0 fw-bold", style={"color": "white"})),
        dbc.CardBody(dbc.Table([
            html.Thead(html.Tr([
                html.Th("Causa (dataset)"), html.Th("Nombre ICD-10 completo"),
                html.Th("Códigos ICD-10"), html.Th("Categoría"), html.Th("Color"),
            ]), style={"background": "#f5f3ff", "fontSize": "0.82rem"}),
            html.Tbody([
                _fila("Heart disease",           "Enfermedades del corazón",
                      "I00–I09, I11, I13, I20–I51", "Cardiovascular",      "#f0b8b8"),
                _fila("Cancer",                  "Tumores malignos",
                      "C00–C97",                    "Neoplasias",           "#c5b8f0"),
                _fila("Unintentional injuries",  "Accidentes (lesiones no intencionales)",
                      "V01–X59, Y85–Y86",           "Lesiones externas",    "#fde8b0"),
                _fila("CLRD",                    "Enf. crónicas de vías resp. inferiores",
                      "J40–J47",                    "Respiratoria",         "#b8d8f0"),
                _fila("Stroke",                  "Enfermedades cerebrovasculares",
                      "I60–I69",                    "Cardiovascular",       "#f7c5e0"),
                _fila("Alzheimer's disease",     "Enfermedad de Alzheimer",
                      "G30",                        "Neurológica",          "#d4f0b8"),
                _fila("Diabetes",                "Diabetes mellitus",
                      "E10–E14",                    "Metabólica",           "#f0d4b8"),
                _fila("Influenza and pneumonia", "Influenza y neumonía",
                      "J09–J18",                    "Infecciosa",           "#b8f0e8"),
                _fila("Kidney disease",          "Nefritis, síndrome nefrótico y nefrosis",
                      "N00–N07, N17–N19, N25–N27",  "Renal",                "#b8c5f0"),
                _fila("Suicide",                 "Lesiones autoinfligidas intencionalmente",
                      "U03, X60–X84, Y87.0",        "Salud mental",         "#f0b8d4"),
                _fila("All causes",              "Total de todas las causas de muerte",
                      "Todas",                      "Agregado",             "#e8e8e8"),
            ])
        ], striped=False, hover=True, responsive=True, bordered=True, className="small mb-0"))
    ], className="shadow-sm border-0 mb-4", style={"borderRadius": "12px"})

    op_vars = [
        ("Year",                    "Año de registro",        "Temporal",        "Año calendario",              "Cuantitativa discreta", "Razón (1999–2017)", "NVSS"),
        ("113 Cause Name",          "Descripción ICD-10",     "Clasificación",   "Texto ICD-10 completo",       "Cualitativa nominal",   "Nominal",           "ICD-10"),
        ("Cause Name",              "Causa abreviada",        "Clasificación",   "Etiqueta legible de la causa","Cualitativa nominal",   "Nominal",           "NCHS"),
        ("State",                   "Estado/Territorio",      "Geográfica",      "Nombre del estado o 'United States'","Cualitativa nominal","Nominal",       "FIPS"),
        ("Deaths",                  "Número de muertes",      "Resultado",       "Conteo absoluto de defunciones","Cuantitativa discreta","Razón (≥ 0)",     "Certificados de defunción"),
        ("Age-adjusted Death Rate", "Tasa ajustada por año",  "Resultado clave", "Muertes por 100,000 hab.",    "Cuantitativa continua", "Razón (≥ 0)",       "Cálculo NCHS"),
    ]

    tabla_op = dbc.Card([
        dbc.CardHeader(html.H5("Tabla de Operacionalización de Variables",
                               className="mb-0 fw-bold", style={"color": "white"})),
        dbc.CardBody(dbc.Table([
            html.Thead(html.Tr([
                html.Th("Variable"), html.Th("Concepto"), html.Th("Dimensión"),
                html.Th("Indicador"), html.Th("Tipo"), html.Th("Escala"), html.Th("Fuente"),
            ]), style={"background": "#f5f3ff", "fontSize": "0.82rem"}),
            html.Tbody([
                html.Tr([
                    html.Td(html.Code(v[0], style={"color": "#5a4fcf"})),
                    html.Td(v[1]), html.Td(v[2]), html.Td(v[3]),
                    html.Td(v[4]), html.Td(v[5]),
                    html.Td(v[6], className="text-muted"),
                ]) for v in op_vars
            ])
        ], striped=False, hover=True, responsive=True, bordered=True, className="small mb-0"))
    ], className="shadow-sm border-0 mb-4", style={"borderRadius": "12px"})

    return dbc.Container([html.Br(), header, conceptos, icd_card, tabla_op, html.Br()], fluid=True)


def _concepto(num, titulo, desc, color):
    return dbc.Card([
        dbc.CardHeader(
            html.Div([
                html.Span(num, style={
                    "width": "28px", "height": "28px", "background": color,
                    "color": "white", "fontSize": "0.85rem", "fontWeight": "700",
                    "borderRadius": "50%", "display": "inline-flex",
                    "alignItems": "center", "justifyContent": "center",
                    "flexShrink": "0", "marginRight": "10px"
                }),
                html.Strong(titulo, style={"color": "white", "fontSize": "0.9rem"}),
            ], style={"display": "flex", "alignItems": "center"}),
            style={"background": "#001f3f", "borderRadius": "8px 8px 0 0"}
        ),
        dbc.CardBody(
            html.P(desc, className="small mb-0", style={"color": "#2c3e50", "lineHeight": "1.65"}),
            style={"background": "white", "borderRadius": "0 0 8px 8px",
                   "border": "1px solid #dee2e6", "borderTop": "none"}
        ),
    ], className="h-100 shadow-sm border-0",
       style={"borderRadius": "8px", "overflow": "hidden"})


def _fila(causa, nombre, codigos, categoria, color):
    return html.Tr([
        html.Td(html.Span(causa, className="fw-semibold",
                          style={"borderLeft": f"4px solid {color}", "paddingLeft": "6px"})),
        html.Td(nombre), html.Td(html.Code(codigos, style={"fontSize": "0.75rem"})),
        html.Td(categoria), html.Td(html.Span("●", style={"color": color, "fontSize": "1.2rem"})),
    ])
