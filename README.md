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

## 3. Dashboard Features

| Tab | Description |
|---|---|
| 📊 Overview | Latest snapshot of all economies with metric cards, cross-country bar charts, and an auto-generated takeaway explaining what the numbers mean |
| 📈 Trend Analysis | Time-series line chart for any selected indicator; includes volatility ranking table (mean and std dev) and context-aware written insights per indicator |
| 🔬 Advanced Insights | Okun's Law scatter plot with OLS trendlines, Pearson r, p-value, slope, and R-squared; COVID-19 shock analysis comparing 2019 vs 2020 GDP change across all economies |
| 🌐 Bubble Chart | Animated three-way visualisation: X = GDP Growth, Y = Inflation, bubble size = Unemployment; includes reading guide and key moments to watch (2009, 2020) |
| 🧮 Calculator | Computes any country's change in any indicator over a custom period; peer benchmark panel ranks the selected country against all others over the same period |

## 4. Methods

- Data loading and reshaping using `pandas` (melt, pivot_table)
- Missing value imputation using each country's own historical mean to preserve relative levels
- Descriptive statistics (mean, std, min, max) by country, including volatility ranking
- Pearson correlation and pooled OLS linear regression (`scipy`, `scikit-learn`, `statsmodels`) to test whether Okun's Law holds across the dataset
- COVID-19 shock analysis comparing 2019 vs 2020 values across all economies
- Interactive trend visualisation using `plotly`
- Streamlit app with sidebar controls for country, year range, and indicator selection
- Peer comparison panel in the Calculator tab: benchmarks each country's change against the group average

## 5. Key Findings

- China recorded the highest average GDP growth (8.19%) across 2000–2025
- Brazil had the highest average inflation (6.28%) and unemployment (9.68%)
- Japan consistently maintained the lowest inflation rate (0.41%) globally
- All 7 economies experienced sharp GDP contractions in 2020 due to COVID-19
- Post-pandemic inflation surged across all countries in 2021–2022
- A Pearson correlation and OLS regression confirmed Okun's Law holds across most economies, with a negative relationship between GDP growth and unemployment. The COVID-19 shock analysis revealed asymmetric impacts: the UK experienced the sharpest contraction while China maintained positive growth, reflecting differences in economic structure and pandemic response.

## 6. Key Macro Events (2000–2025)

| Year | Event |
|---|---|
| 2001 | Dot-com bust and US recession |
| 2003 | China WTO integration accelerates export growth |
| 2008–2009 | Global Financial Crisis: GDP collapse across all economies |
| 2010–2011 | Post-GFC recovery; commodity price surge drives inflation |
| 2013 | Eurozone debt crisis spillover; Japan launches Abenomics |
| 2015–2016 | China slowdown; oil price crash; Brazil recession begins |
| 2018 | US-China trade war escalation |
| 2020 | COVID-19 pandemic: synchronised global GDP shock |
| 2021 | V-shaped recovery; global supply chain disruption |
| 2022–2023 | Post-pandemic inflation surge; aggressive central bank tightening |
| 2024–2025 | Disinflation; uneven labour market recovery across economies |

## 7. How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Or install manually:
```bash
pip install streamlit pandas plotly scipy scikit-learn statsmodels
streamlit run app.py
```

## 8. Product Link / Demo

🔗 **Live App:** https://acc102-macro-dashboard.streamlit.app

## 9. Limitations & Next Steps

- **Data completeness:** 2024–2025 data may be incomplete or based on preliminary estimates for some countries, as World Bank figures are typically published with a 1–2 year lag.
- **Missing value imputation:** Missing values were filled using each country's historical mean, which is a simplified approach that may smooth over structural breaks or crisis periods.
- **Unemployment coverage:** Unemployment data for India has limited historical coverage in earlier years, which may affect cross-country comparisons.
- **Pooled regression:** The OLS regression pools all countries without controlling for country-specific fixed effects (e.g. labour market institutions), which may bias the slope estimate.
- **Correlation vs causation:** The Okun's Law scatter analysis shows correlation between GDP growth and unemployment, but does not establish causation or control for other macroeconomic variables.
- **Country selection bias:** The seven economies were selected for diversity and data availability, but do not represent all global economic patterns, particularly smaller or developing economies.
- **Future improvements:** Could include additional indicators such as GDP per capita, trade balance, and government debt; a wider country selection; live data integration via the World Bank API; and more advanced modelling such as panel regression with fixed effects or time-series forecasting.
