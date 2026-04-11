# NCHS Dashboard · Leading Causes of Death in the United States

Interactive dashboard for the exploratory analysis of mortality data in the United States (1999–2017), built with Python, Dash and Plotly. The data comes from the **National Center for Health Statistics (NCHS)**, the statistical branch of the CDC.

---

## Business Context

Understanding long-term mortality trends is essential for public health policy, academic research and evidence-based decision making. This dashboard allows users to explore how the leading causes of death in the U.S. have evolved over nearly two decades, identify geographic disparities between states, and analyze the phenomenon known as **Deaths of Despair** — the sustained rise in deaths by suicide and unintentional injuries (opioid crisis).

The tool is designed both as an analytical instrument and as a presentation resource, providing interactive visualizations that transform raw data into clear narratives.

---

## Run the App

All the files required to run the application locally are inside the `nchs_dashboard` folder. The dashboard was developed with Python using the library Dash (make sure you have Python installed on your computer).

**1. (Optional)** We recommend using a virtual environment to prevent conflicts with other libraries:

```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

**2.** Install the requirements (located inside the `nchs_dashboard` folder):

```bash
pip install -r requirements.txt
```

**3.** Start the application (inside the `nchs_dashboard` folder):

```bash
python app.py
```

**4.** Access the dashboard locally on your browser:

```
http://localhost:8080/
```

---

## Dashboard Structure

| Tab | Content |
|-----|---------|
| **Introducción** | Overview, key metrics and dashboard navigation |
| **Marco Teórico** | Conceptual foundations and ICD-10 classification |
| **Metodología** | Dataset description, cleaning process and analytical decisions |
| **Evolución de Tasas** | Interactive time series by cause and state (1999–2017) |
| **Ranking por Año** | Animated bar chart ranking the top 10 causes with a year slider |
| **Deaths of Despair** | Deep dive into suicide and unintentional injuries (opioid crisis) |
| **Análisis Geográfico** | Choropleth map of mortality rates across U.S. states |
| **Caso: West Virginia** | In-depth case study of the state hardest hit by the opioid crisis |
| **Limitaciones** | Methodological scope, caveats and interpretation warnings |
| **Conclusiones** | Key findings, public policy implications and final reflection |

---

## Data

- **Source:** National Center for Health Statistics (NCHS) / Centers for Disease Control and Prevention (CDC)
- **Period:** 1999–2017
- **Coverage:** 50 states + District of Columbia + national total
- **Causes:** 10 leading causes of death + All causes (ICD-10 classification)
- **Metric:** Age-adjusted mortality rate per 100,000 inhabitants (standardized to the U.S. 2000 population)

---

## Tech Stack

- **Python** — core language
- **Dash** — web application framework
- **Plotly** — interactive visualizations
- **Dash Bootstrap Components** — layout and UI components
- **Pandas** — data processing

---

## Team

This project was developed as an academic data analysis exercise using publicly available NCHS/CDC data.
