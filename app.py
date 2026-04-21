import streamlit as st
import pandas as pd
import plotly.express as px
from scipy import stats
from sklearn.linear_model import LinearRegression
import numpy as np

# Page Config
st.set_page_config(
    page_title="Global Macro Dashboard",
    page_icon="🌍",
    layout="wide"
)

# Load Data
@st.cache_data
def load_data():
    df_raw = pd.read_csv('Data.csv')
    df_raw = df_raw.rename(columns={
        'Country Name': 'economy',
        'Country Code': 'country_code',
        'Series Name':  'series_name',
        'Series Code':  'series_code'
    })
    indicator_map = {
        'NY.GDP.MKTP.KD.ZG': 'GDP Growth (%)',
        'FP.CPI.TOTL.ZG':    'Inflation (%)',
        'SL.UEM.TOTL.ZS':    'Unemployment (%)'
    }
    df_raw = df_raw[df_raw['series_code'].isin(indicator_map.keys())].copy()
    df_raw['indicator'] = df_raw['series_code'].map(indicator_map)
    year_cols = [c for c in df_raw.columns if 'YR' in c]
    df_melt = df_raw.melt(
        id_vars=['economy', 'country_code', 'indicator'],
        value_vars=year_cols,
        var_name='year_raw',
        value_name='value'
    )
    df_melt['year'] = df_melt['year_raw'].str.extract(r'(\d{4})').astype(int)
    df_melt = df_melt[df_melt['year'].between(2000, 2025)]
    df_melt['value'] = pd.to_numeric(df_melt['value'], errors='coerce')
    data = df_melt.pivot_table(
        index=['economy', 'country_code', 'year'],
        columns='indicator',
        values='value'
    ).reset_index()
    data.columns.name = None
    for col in ['GDP Growth (%)', 'Inflation (%)', 'Unemployment (%)']:
        data[col] = data.groupby('economy')[col].transform(
            lambda x: x.fillna(x.mean())
        )
    return data

data = load_data()
indicators = ['GDP Growth (%)', 'Inflation (%)', 'Unemployment (%)']

# Sidebar
st.sidebar.title("🎛️ Dashboard Controls")
all_countries = sorted(data['economy'].unique())
selected_countries = st.sidebar.multiselect(
    "Select Countries",
    options=all_countries,
    default=all_countries
)
selected_years = st.sidebar.slider(
    "Select Year Range",
    min_value=2000, max_value=2025, value=(2000, 2025)
)
selected_indicator = st.sidebar.selectbox(
    "Select Indicator for Trend Chart",
    options=indicators, index=0
)
st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Data Source:** [World Bank WDI](https://databank.worldbank.org/source/world-development-indicators)  \n"
    "Accessed: April 2026"
)

# Filter Data
filtered = data[
    (data['economy'].isin(selected_countries)) &
    (data['year'].between(selected_years[0], selected_years[1]))
]

# ── IMPROVEMENT 1: About / Problem Statement ──────────────────────────────────
st.title("🌍 Global Macro Dashboard")
st.markdown("Explore **GDP Growth**, **Inflation**, and **Unemployment** trends across 7 major economies (2000–2025).")

with st.expander("ℹ️ About this dashboard — click to expand", expanded=False):
    st.markdown("""
**Analytical Problem**

How have GDP growth, inflation, and unemployment evolved across major economies since 2000,
and what can these macro indicators tell us about economic resilience — especially around the
2008 Global Financial Crisis and the 2020 COVID-19 pandemic?

**Target Audience**

Economics and finance students, policy researchers, and business analysts who need a quick
comparative view of macroeconomic performance across the G7 and emerging markets.

**Dataset**

World Bank World Development Indicators (WDI) — three series:
- `NY.GDP.MKTP.KD.ZG` — GDP growth (annual %)
- `FP.CPI.TOTL.ZG` — Inflation, consumer prices (annual %)
- `SL.UEM.TOTL.ZS` — Unemployment, total (% of total labour force)

Coverage: Brazil, China, Germany, India, Japan, United Kingdom, United States (2000–2025).
Missing values are filled with each country's own period average to preserve trend continuity.

**How to use**

Use the sidebar to filter countries and year range, then explore each tab:
📊 Overview → snapshot & rankings | 📈 Trend → time-series by indicator |
🔬 Advanced → Okun's Law & COVID shock | 🌐 Bubble → animated three-way view |
🧮 Calculator → compute change between any two years
    """)

st.info("👈 Use the sidebar to filter countries and year range. Then explore the tabs below to dive into the data.")

c1, c2, c3 = st.columns(3)
c1.success("📊 **Overview** — Latest snapshot of all economies")
c2.info("🔬 **Advanced Insights** — Okun's Law & COVID-19 analysis")
c3.warning("🧮 **Calculator** — Compute changes over a custom period")

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "📈 Trend Analysis",
    "🔬 Advanced Insights",
    "🌐 Bubble Chart",
    "🧮 Calculator"
])

# Tab 1: Overview
with tab1:
    latest_year = filtered['year'].max()
    latest = filtered[filtered['year'] == latest_year]

    st.subheader(f"Snapshot — {latest_year}")
    flag_map = {
        'Brazil': '🇧🇷', 'China': '🇨🇳', 'Germany': '🇩🇪',
        'India': '🇮🇳', 'Japan': '🇯🇵',
        'United Kingdom': '🇬🇧', 'United States': '🇺🇸'
    }
    cols = st.columns(len(selected_countries))
    for i, country in enumerate(selected_countries):
        row = latest[latest['economy'] == country]
        if not row.empty:
            gdp = row['GDP Growth (%)'].values[0]
            inf = row['Inflation (%)'].values[0]
            une = row['Unemployment (%)'].values[0]
            flag = flag_map.get(country, '')
            with cols[i]:
                st.metric(label=f"{flag} {country}", value=f"{gdp:.1f}%", delta="GDP Growth")
                st.caption(f"Inflation: {inf:.1f}% | Unemp: {une:.1f}%")

    st.markdown("---")
    st.subheader(f"Country Comparison — {latest_year}")
    col1, col2, col3 = st.columns(3)
    for col, ind in zip([col1, col2, col3], indicators):
        fig_bar = px.bar(
            latest[latest['economy'].isin(selected_countries)].sort_values(ind, ascending=False),
            x='economy', y=ind, color='economy',
            labels={'economy': 'Country'},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_bar.update_layout(showlegend=False, height=300)
        col.plotly_chart(fig_bar, width='stretch')

    st.markdown("---")
    st.subheader("Summary Statistics (Selected Period)")
    summary = filtered.groupby('economy')[indicators].mean().round(2).reset_index()
    summary.columns = ['Country', 'Avg GDP Growth (%)', 'Avg Inflation (%)', 'Avg Unemployment (%)']
    st.dataframe(summary, use_container_width=True, hide_index=True)

    # ── IMPROVEMENT 2: CSV Download ───────────────────────────────────────────
    st.markdown("---")
    st.subheader("📥 Export Data")
    st.caption("Download the filtered dataset as a CSV file for further analysis.")
    csv_export = filtered[['economy', 'year'] + indicators].sort_values(['economy', 'year'])
    csv_bytes = csv_export.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download filtered data as CSV",
        data=csv_bytes,
        file_name=f"global_macro_{selected_years[0]}_{selected_years[1]}.csv",
        mime="text/csv"
    )

# Tab 2: Trend Analysis
with tab2:
    st.subheader(f"{selected_indicator} Trend — {selected_years[0]} to {selected_years[1]}")
    fig_line = px.line(
        filtered, x='year', y=selected_indicator, color='economy',
        markers=True,
        labels={'year': 'Year', 'economy': 'Country'},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_line.update_layout(hovermode='x unified', height=420)
    st.plotly_chart(fig_line, width='stretch')

    st.markdown("---")
    st.subheader("Key Insights")
    avg = filtered.groupby('economy')[indicators].mean().round(2)
    if not avg.empty:
        for ind in indicators:
            top = avg[ind].idxmax()
            bottom = avg[ind].idxmin()
            st.markdown(f"**{ind}:** Highest → `{top}` ({avg.loc[top, ind]}%) | Lowest → `{bottom}` ({avg.loc[bottom, ind]}%)")

# Tab 3: Advanced Insights
with tab3:
    adv_tab1, adv_tab2 = st.tabs(["Okun's Law", "COVID-19 Impact"])

    # ── IMPROVEMENT 3: Pearson r + Linear Regression in Okun's Law tab ────────
    with adv_tab1:
        st.markdown("**GDP Growth vs Unemployment — Does Okun's Law Hold?**")

        okun_data = filtered[['GDP Growth (%)', 'Unemployment (%)']].dropna()

        fig_scatter = px.scatter(
            filtered, x='GDP Growth (%)', y='Unemployment (%)',
            color='economy', trendline='ols',
            title="GDP Growth vs Unemployment (OLS trendline per country)",
            labels={'economy': 'Country'},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_scatter, width='stretch')

        # Pearson correlation
        if len(okun_data) >= 3:
            r, p_value = stats.pearsonr(okun_data['GDP Growth (%)'], okun_data['Unemployment (%)'])

            # Linear regression (sklearn)
            X = okun_data[['GDP Growth (%)']].values
            y = okun_data['Unemployment (%)'].values
            model = LinearRegression().fit(X, y)
            slope     = round(model.coef_[0], 3)
            intercept = round(model.intercept_, 3)
            r_squared = round(model.score(X, y), 3)

            # Display stats in metric cards
            mc1, mc2, mc3, mc4 = st.columns(4)
            mc1.metric("Pearson r", f"{r:.3f}", help="Strength and direction of linear correlation. Negative = Okun's Law holds.")
            mc2.metric("p-value", f"{p_value:.4f}", help="Statistical significance. p < 0.05 means the correlation is significant.")
            mc3.metric("OLS Slope (β)", f"{slope}", help="For each 1 pp rise in GDP growth, unemployment changes by this amount (pp).")
            mc4.metric("R²", f"{r_squared}", help="Proportion of unemployment variation explained by GDP growth.")

            # Written interpretation
            direction = "negative" if r < 0 else "positive"
            significance = "statistically significant (p < 0.05)" if p_value < 0.05 else "not statistically significant at the 5% level"

            st.info(f"""
**Statistical Interpretation**

The Pearson correlation coefficient is **r = {r:.3f}**, indicating a **{direction} relationship**
between GDP growth and unemployment across the selected countries and period.
This result is **{significance}**.

The OLS regression yields a slope of **β = {slope}**, meaning that on average, a 1 percentage
point increase in GDP growth is associated with a **{abs(slope)} pp {'decrease' if slope < 0 else 'increase'}**
in the unemployment rate — broadly consistent with {'Okun\'s Law' if slope < 0 else 'a non-standard pattern'}.

The R² of **{r_squared}** suggests that GDP growth alone explains approximately
**{int(r_squared * 100)}%** of the variation in unemployment in this dataset,
with the remainder driven by structural factors such as labour market rigidities,
demographic trends, and policy responses.
            """)
        else:
            st.warning("Not enough data points to compute statistics. Please select more countries or a wider year range.")

    with adv_tab2:
        st.markdown("**COVID-19 Shock — Change from 2019 to 2020**")
        pre  = data[data['year'] == 2019].set_index('economy')
        post = data[data['year'] == 2020].set_index('economy')
        shock = pd.DataFrame({
            'GDP Drop (pp)': (post['GDP Growth (%)'] - pre['GDP Growth (%)']).round(2),
            'Unemployment Rise (pp)': (post['Unemployment (%)'] - pre['Unemployment (%)']).round(2)
        }).reset_index()
        fig_shock = px.bar(
            shock, x='economy', y='GDP Drop (pp)',
            title='GDP Growth Change due to COVID-19 (2019 → 2020)',
            labels={'economy': 'Country'},
            color='GDP Drop (pp)',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig_shock, width='stretch')
        st.caption("The UK experienced the sharpest contraction, while China was the only economy to maintain positive growth in 2020.")

        # Additional interpretation
        if not shock.empty:
            worst = shock.loc[shock['GDP Drop (pp)'].idxmin(), 'economy']
            best  = shock.loc[shock['GDP Drop (pp)'].idxmax(), 'economy']
            avg_drop = shock['GDP Drop (pp)'].mean()
            st.info(f"""
**Key Findings**

- The hardest-hit economy was **{worst}**, experiencing the largest GDP growth decline from 2019 to 2020.
- **{best}** showed the smallest contraction (or continued growth), reflecting stronger economic resilience or earlier containment.
- Across all 7 economies, the average GDP growth change was **{avg_drop:.2f} pp**, illustrating the synchronised nature of the COVID-19 shock.
- The variation in outcomes reflects differences in fiscal stimulus, industrial structure, and containment policy effectiveness.
            """)

# Tab 4: Bubble Chart
with tab4:
    st.subheader("🌐 Economic Evolution — Animated Bubble Chart")
    st.caption("Each bubble represents a country. Size = Unemployment rate. X = GDP Growth. Y = Inflation. Press ▶ to animate.")
    fig_bubble = px.scatter(
        data[data['economy'].isin(selected_countries)],
        x='GDP Growth (%)', y='Inflation (%)',
        size='Unemployment (%)', color='economy',
        animation_frame='year', animation_group='economy',
        hover_name='economy', size_max=50,
        range_x=[-15, 20], range_y=[-2, 20],
        title='GDP Growth vs Inflation vs Unemployment (2000–2025)',
        labels={'economy': 'Country'},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_bubble.update_layout(height=550)
    st.plotly_chart(fig_bubble, width='stretch')

# Tab 5: Calculator
with tab5:
    st.subheader("🧮 Growth Rate Calculator")
    st.caption("Select a country, indicator, and time period to calculate the cumulative change.")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        calc_country = st.selectbox("Country", options=sorted(data['economy'].unique()))
    with col_b:
        calc_indicator = st.selectbox("Indicator", options=indicators)
    with col_c:
        calc_years = st.slider("Year Range", min_value=2000, max_value=2025, value=(2000, 2025))

    calc_data = data[
        (data['economy'] == calc_country) &
        (data['year'].between(calc_years[0], calc_years[1]))
    ]

    if not calc_data.empty:
        start_val = calc_data[calc_data['year'] == calc_years[0]][calc_indicator].values
        end_val   = calc_data[calc_data['year'] == calc_years[1]][calc_indicator].values

        if len(start_val) > 0 and len(end_val) > 0:
            start_val = round(start_val[0], 2)
            end_val   = round(end_val[0], 2)
            change    = round(end_val - start_val, 2)
            avg_val   = round(calc_data[calc_indicator].mean(), 2)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric(f"Value in {calc_years[0]}", f"{start_val}%")
            m2.metric(f"Value in {calc_years[1]}", f"{end_val}%")
            m3.metric("Change (pp)", f"{change:+.2f}")
            m4.metric("Period Average", f"{avg_val}%")

            fig_calc = px.line(
                calc_data, x='year', y=calc_indicator,
                title=f"{calc_indicator} — {calc_country} ({calc_years[0]}–{calc_years[1]})",
                markers=True,
                color_discrete_sequence=['#1D9E75']
            )
            fig_calc.update_layout(height=350)
            st.plotly_chart(fig_calc, width='stretch')
