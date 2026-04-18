# 🌍 Global Macro Dashboard

An interactive data tool exploring GDP Growth, Inflation, and Unemployment trends across 7 major economies from 2000 to 2025.

**🔗 Live App: [https://acc102-macro-dashboard.streamlit.app](https://acc102-macro-dashboard.streamlit.app)**

---

## 1. Problem & User

How have key macroeconomic indicators evolved across major economies over the past two decades, and how did global shocks such as the 2008 financial crisis and the COVID-19 pandemic affect them differently? This dashboard is designed for students, researchers, and anyone interested in comparing macroeconomic performance across countries.

## 2. Data

- **Source:** World Bank World Development Indicators
- **URL:** https://databank.worldbank.org/source/world-development-indicators
- **Accessed:** April 2026
- **Indicators:**
  - `NY.GDP.MKTP.KD.ZG` — GDP Growth (annual %)
  - `FP.CPI.TOTL.ZG` — Inflation, consumer prices (annual %)
  - `SL.UEM.TOTL.ZS` — Unemployment, total (% of total labour force)
- **Countries:** China, United States, United Kingdom, Germany, Japan, India, Brazil
- **Period:** 2000–2025

## 3. Methods

- Data loading and reshaping using `pandas` (melt, pivot_table)
- Missing value imputation using country-level historical mean
- Descriptive statistics (mean, std, min, max) by country
- Interactive trend visualisation using `plotly`
- Streamlit app with sidebar controls for country, year range, and indicator selection

## 4. Key Findings

- China recorded the highest average GDP growth (8.19%) across 2000–2025
- Brazil had the highest average inflation (6.28%) and unemployment (9.68%)
- Japan consistently maintained the lowest inflation rate (0.41%) globally
- All 7 economies experienced sharp GDP contractions in 2020 due to COVID-19
- Post-pandemic inflation surged across all countries in 2021–2022
- A correlation analysis confirmed Okun's Law holds across most economies, 
with a negative relationship between GDP growth and unemployment. 
The COVID-19 shock analysis revealed asymmetric impacts — the UK experienced 
the sharpest contraction while China maintained positive growth, 
reflecting differences in economic structure and pandemic response.

## 5. How to Run

```bash
pip install streamlit pandas plotly
streamlit run app.py
```

## 6. Product Link / Demo

🔗 **Live App:** https://acc102-macro-dashboard.streamlit.app

## 7. Limitations & Next Steps

- 2024–2025 data may be incomplete or estimated for some countries
- Unemployment data for India is limited in coverage
- Future improvements could include GDP per capita, trade balance, and more countries
