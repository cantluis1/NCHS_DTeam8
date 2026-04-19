"""
data/loader.py
Carga y limpia el dataset NCHS una sola vez.
Todas las pestañas importan desde aquí para evitar lecturas duplicadas.
"""

import re
from pathlib import Path
from functools import lru_cache

import pandas as pd

DATA_PATH = Path(__file__).parent / "nchs_deaths.csv"

# Causas clasificadas como "Deaths of Despair"
DESPAIR_CAUSES = ["Suicide", "Unintentional injuries"]

# Abreviatura → nombre completo de estado (para mapas)
STATE_ABBREV = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI",
    "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI",
    "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX",
    "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
    "United States": "US",
}

PALETA = [
    "#c5b8f0", "#f7c5e0", "#b8e8c5", "#fde8b0",
    "#b8d8f0", "#f0b8b8", "#d4f0b8", "#f0d4b8",
    "#b8c5f0", "#f0b8d4", "#b8f0e8",
]

CAUSA_COLORES = {
    "Heart disease":           "#f0b8b8",
    "Cancer":                  "#c5b8f0",
    "Unintentional injuries":  "#fde8b0",
    "CLRD":                    "#b8d8f0",
    "Stroke":                  "#f7c5e0",
    "Alzheimer's disease":     "#d4f0b8",
    "Diabetes":                "#f0d4b8",
    "Influenza and pneumonia": "#b8f0e8",
    "Kidney disease":          "#b8c5f0",
    "Suicide":                 "#f0b8d4",
    "All causes":              "#e0e0e0",
}


def _parse_number(x):
    """Convierte '1.234' o '1,234' o '1234' a int/float limpio."""
    s = str(x).strip()
    # Puntos como separador de miles: '1.234' → '1234'
    s = re.sub(r'\.(?=\d{3}(\D|$))', '', s)
    s = s.replace(',', '.')
    return s


@lru_cache(maxsize=1)
def load_df() -> pd.DataFrame:
    """Lee, limpia y cachea el dataset completo."""
    df = pd.read_csv(DATA_PATH)

    # Limpiar Deaths
    df["Deaths"] = df["Deaths"].apply(_parse_number)
    df["Deaths"] = pd.to_numeric(df["Deaths"], errors="coerce").fillna(0).astype(int)

    # Limpiar Age-adjusted Death Rate
    df["Rate"] = df["Age-adjusted Death Rate"].apply(_parse_number)
    df["Rate"] = pd.to_numeric(df["Rate"], errors="coerce")

    # Year como int nativo de Python (no numpy.int64) — crítico para JSON serialization
    df["Year"] = df["Year"].astype(int)

    # Código de estado
    df["StateCode"] = df["State"].map(STATE_ABBREV)

    # Flag Deaths of Despair
    df["IsDespair"] = df["Cause Name"].isin(DESPAIR_CAUSES)

    return df


def get_national(df: pd.DataFrame) -> pd.DataFrame:
    """Filas donde State == 'United States'."""
    return df[df["State"] == "United States"].copy()


def get_states(df: pd.DataFrame) -> pd.DataFrame:
    """Filas de estados (excluye 'United States' agregado)."""
    return df[df["State"] != "United States"].copy()
