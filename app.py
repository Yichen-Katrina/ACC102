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
st.sidebar.title("Dashboard Controls")
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

# Header
st.title("Global Macro Dashboard")
st.markdown("Explore **GDP Growth**, **Inflation**, and **Unemployment** trends across 7 major economies (2000-2025).")

with st.expander("About this dashboard - click to expand", expanded=False):
    st.markdown("""
**Analytical Problem**

How have GDP growth, inflation, and unemployment evolved across major economies since 2000,
and what can these macro indicators tell us about economic resilience - especially around the
2008 Global Financial Crisis and the 2020 COVID-19 pandemic?

**Target Audience**

Economics and finance students, policy researchers, and business analysts who need a quick
comparative view of macroeconomic performance across the G7 and emerging markets.

**Dataset**

World Bank World Development Indicators (WDI) - three series:
- NY.GDP.MKTP.KD.ZG - GDP growth (annual %)
- FP.CPI.TOTL.ZG - Inflation, consumer prices (annual %)
- SL.UEM.TOTL.ZS - Unemployment, total (% of total labour force)

Coverage: Brazil, China, Germany, India, Japan, United Kingdom, United States (2000-2025).
Missing values are filled with each country's own period average to preserve trend continuity.

**How to use**

Use the sidebar to filter countries and year range, then explore each tab:
Overview -> snapshot & rankings | Trend -> time-series by indicator |
Advanced -> Okun's Law & COVID shock | Bubble -> animated three-way view |
Calculator -> compute change between any two years and compare against peers
    """)

st.info("Use the sidebar to filter countries and year range. Then explore the tabs below to dive into the data.")

c1, c2, c3 = st.columns(3)
c1.success("**Overview** - Latest snapshot of all economies")
c2.info("**Advanced Insights** - Okun's Law & COVID-19 analysis")
c3.warning("**Calculator** - Compute and compare changes over a custom period")

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "Trend Analysis",
    "Advanced Insights",
    "Bubble Chart",
    "Calculator"
])

# TAB 1 - Overview
with tab1:
    latest_year = filtered['year'].max()
    latest = filtered[filtered['year'] == latest_year]

    st.subheader(f"Snapshot - {latest_year}")
    flag_map = {
        'Brazil': 'BR', 'China': 'CN', 'Germany': 'DE',
        'India': 'IN', 'Japan': 'JP',
        'United Kingdom': 'GB', 'United States': 'US'
    }
    cols = st.columns(len(selected_countries))
    for i, country in enumerate(selected_countries):
        row = latest[latest['economy'] == country]
        if not row.empty:
            gdp = row['GDP Growth (%)'].values[0]
            inf = row['Inflation (%)'].values[0]
            une = row['Unemployment (%)'].values[0]
            with cols[i]:
                st.metric(label=country, value=f"{gdp:.1f}%", delta="GDP Growth")
                st.caption(f"Inflation: {inf:.1f}% | Unemp: {une:.1f}%")

    st.markdown("---")
    st.subheader(f"Country Comparison - {latest_year}")
    col1, col2, col3 = st.columns(3)
    for col, ind in zip([col1, col2, col3], indicators):
        sorted_latest = latest[latest['economy'].isin(selected_countries)].sort_values(ind, ascending=False)
        fig_bar = px.bar(
            sorted_latest, x='economy', y=ind, color='economy',
            labels={'economy': 'Country'},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_bar.update_layout(showlegend=False, height=300)
        col.plotly_chart(fig_bar, width='stretch')

    # FIX 1: auto-generated takeaway after bar charts
    if not latest.empty:
        grp_avg = latest[indicators].mean()
        top_gdp     = latest.loc[latest['GDP Growth (%)'].idxmax(), 'economy']
        top_gdp_val = latest['GDP Growth (%)'].max()
        low_une     = latest.loc[latest['Unemployment (%)'].idxmin(), 'economy']
        low_une_val = latest['Unemployment (%)'].min()
        high_inf    = latest.loc[latest['Inflation (%)'].idxmax(), 'economy']
        high_inf_val= latest['Inflation (%)'].max()

        st.info(f"""
**What to take away from the {latest_year} snapshot**

- **Fastest-growing economy:** {top_gdp} at {top_gdp_val:.1f}% GDP growth (group average: {grp_avg['GDP Growth (%)']:.1f}%).
- **Tightest labour market:** {low_une} has the lowest unemployment ({low_une_val:.1f}%), suggesting strong job creation or structural full employment.
- **Highest inflation pressure:** {high_inf} leads on inflation ({high_inf_val:.1f}%), which may signal demand overheating or supply-side constraints.

Use the Trend Analysis tab to see how these positions changed over time, or the Calculator tab to measure each country's improvement since {selected_years[0]}.
        """)

    st.markdown("---")
    st.subheader("Summary Statistics (Selected Period)")
    summary = filtered.groupby('economy')[indicators].mean().round(2).reset_index()
    summary.columns = ['Country', 'Avg GDP Growth (%)', 'Avg Inflation (%)', 'Avg Unemployment (%)']
    st.dataframe(summary, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Export Data")
    st.caption("Download the filtered dataset as a CSV file for further analysis.")
    csv_export = filtered[['economy', 'year'] + indicators].sort_values(['economy', 'year'])
    csv_bytes = csv_export.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download filtered data as CSV",
        data=csv_bytes,
        file_name=f"global_macro_{selected_years[0]}_{selected_years[1]}.csv",
        mime="text/csv"
    )

# TAB 2 - Trend Analysis
with tab2:
    st.subheader(f"{selected_indicator} Trend - {selected_years[0]} to {selected_years[1]}")
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
    vol = filtered.groupby('economy')[indicators].std().round(2)

    if not avg.empty:
        ind = selected_indicator
        top     = avg[ind].idxmax()
        bottom  = avg[ind].idxmin()
        top_val = avg.loc[top, ind]
        bot_val = avg.loc[bottom, ind]
        grp_avg = avg[ind].mean()
        most_volatile = vol[ind].idxmax()
        most_stable   = vol[ind].idxmin()

        # FIX 2: context-aware interpretation per indicator
        if ind == 'GDP Growth (%)':
            high_label = "fastest-growing"
            low_label  = "slowest-growing"
            high_note  = "This may reflect rapid industrialisation, strong exports, or favourable demographic trends."
            low_note   = "Persistently low growth can indicate structural headwinds such as an ageing population or weak domestic demand."
            vol_note   = "High volatility in GDP growth suggests greater exposure to external shocks or commodity cycles."
            stab_note  = "Low volatility points to a diversified and resilient economic structure."
        elif ind == 'Inflation (%)':
            high_label = "highest-inflation"
            low_label  = "lowest-inflation"
            high_note  = "Persistently high inflation erodes purchasing power and may prompt central bank tightening."
            low_note   = "Very low or negative inflation may signal weak demand or deflationary pressure, common in mature economies."
            vol_note   = "Volatile inflation makes long-term planning difficult for businesses and households."
            stab_note  = "Stable, low inflation is typically associated with credible monetary policy frameworks."
        else:
            high_label = "highest-unemployment"
            low_label  = "lowest-unemployment"
            high_note  = "Structural unemployment may reflect skills mismatches, rigid labour regulations, or weak investment."
            low_note   = "Near-full employment boosts consumer spending but may also create wage-push inflation."
            vol_note   = "Large swings in unemployment suggest vulnerability to cyclical downturns."
            stab_note  = "A stable unemployment rate indicates a resilient labour market that absorbs shocks without large layoffs."

        st.info(f"""
**{ind} - {selected_years[0]} to {selected_years[1]}**

- **{high_label.capitalize()} economy:** {top} averaged {top_val}% over the period ({round(top_val - grp_avg, 2):+.1f} pp vs group average of {grp_avg:.1f}%). {high_note}
- **{low_label.capitalize()} economy:** {bottom} averaged {bot_val}% ({round(bot_val - grp_avg, 2):+.1f} pp vs group average). {low_note}
- **Most volatile:** {most_volatile} (std dev = {vol.loc[most_volatile, ind]}%) - {vol_note}
- **Most stable:** {most_stable} (std dev = {vol.loc[most_stable, ind]}%) - {stab_note}
        """)

        # Ranking table
        rank_df = avg[[ind]].copy()
        rank_df.columns = [f'Avg {ind}']
        rank_df[f'Std Dev {ind}'] = vol[ind]
        rank_df['Rank (avg)'] = rank_df[f'Avg {ind}'].rank(ascending=(ind != 'GDP Growth (%)')).astype(int)
        rank_df = rank_df.sort_values('Rank (avg)').reset_index()
        rank_df.columns = ['Country', f'Avg {ind}', f'Std Dev {ind}', 'Rank']
        st.dataframe(rank_df, use_container_width=True, hide_index=True)

# TAB 3 - Advanced Insights
with tab3:
    adv_tab1, adv_tab2 = st.tabs(["Okun's Law", "COVID-19 Impact"])

    with adv_tab1:
        st.markdown("**GDP Growth vs Unemployment - Does Okun's Law Hold?**")
        okun_data = filtered[['GDP Growth (%)', 'Unemployment (%)']].dropna()

        fig_scatter = px.scatter(
            filtered, x='GDP Growth (%)', y='Unemployment (%)',
            color='economy', trendline='ols',
            title="GDP Growth vs Unemployment (OLS trendline per country)",
            labels={'economy': 'Country'},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_scatter, width='stretch')

        if len(okun_data) >= 3:
            r, p_value = stats.pearsonr(okun_data['GDP Growth (%)'], okun_data['Unemployment (%)'])
            X = okun_data[['GDP Growth (%)']].values
            y = okun_data['Unemployment (%)'].values
            model     = LinearRegression().fit(X, y)
            slope     = round(model.coef_[0], 3)
            r_squared = round(model.score(X, y), 3)

            mc1, mc2, mc3, mc4 = st.columns(4)
            mc1.metric("Pearson r", f"{r:.3f}", help="Strength and direction of linear correlation. Negative = Okun's Law holds.")
            mc2.metric("p-value", f"{p_value:.4f}", help="Statistical significance. p < 0.05 means significant.")
            mc3.metric("OLS Slope (beta)", f"{slope}", help="For each 1 pp rise in GDP growth, unemployment changes by this amount (pp).")
            mc4.metric("R-squared", f"{r_squared}", help="Proportion of unemployment variation explained by GDP growth.")

            direction    = "negative" if r < 0 else "positive"
            significance = "statistically significant (p < 0.05)" if p_value < 0.05 else "not statistically significant at the 5% level"

            st.info(f"""
**Statistical Interpretation**

The Pearson correlation coefficient is r = {r:.3f}, indicating a {direction} relationship
between GDP growth and unemployment. This result is {significance}.

The OLS slope of {slope} means a 1 pp increase in GDP growth is associated with a
{abs(slope)} pp {"decrease" if slope < 0 else "increase"} in unemployment -
{"consistent with Okun's Law." if slope < 0 else "a non-standard pattern worth investigating."}

R-squared = {r_squared}: GDP growth explains {int(r_squared * 100)}% of unemployment variation here;
the rest is driven by structural factors like labour market rigidities and policy responses.
            """)
        else:
            st.warning("Not enough data points. Please select more countries or a wider year range.")

    with adv_tab2:
        st.markdown("**COVID-19 Shock - Change from 2019 to 2020**")
        pre  = data[data['year'] == 2019].set_index('economy')
        post = data[data['year'] == 2020].set_index('economy')
        shock = pd.DataFrame({
            'GDP Drop (pp)': (post['GDP Growth (%)'] - pre['GDP Growth (%)']).round(2),
            'Unemployment Rise (pp)': (post['Unemployment (%)'] - pre['Unemployment (%)']).round(2)
        }).reset_index()
        fig_shock = px.bar(
            shock, x='economy', y='GDP Drop (pp)',
            title='GDP Growth Change due to COVID-19 (2019 to 2020)',
            labels={'economy': 'Country'},
            color='GDP Drop (pp)',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig_shock, width='stretch')

        if not shock.empty:
            worst    = shock.loc[shock['GDP Drop (pp)'].idxmin(), 'economy']
            best     = shock.loc[shock['GDP Drop (pp)'].idxmax(), 'economy']
            avg_drop = shock['GDP Drop (pp)'].mean()
            st.info(f"""
**Key Findings**

- Hardest-hit economy: **{worst}** - the largest GDP growth decline from 2019 to 2020.
- **{best}** showed the smallest contraction or continued growth, reflecting greater resilience.
- Average GDP growth change across all economies: {avg_drop:.2f} pp - illustrating the synchronised nature of the shock.
- Variation in outcomes reflects differences in fiscal stimulus, industrial structure, and containment effectiveness.
            """)

# TAB 4 - Bubble Chart
with tab4:
    st.subheader("Economic Evolution - Animated Bubble Chart")

    # FIX 3: reading guide before the chart
    st.markdown("""
**How to read this chart**

| Dimension | What it shows | What to look for |
|---|---|---|
| X-axis | GDP Growth (%) | Moving right = growing faster |
| Y-axis | Inflation (%) | Moving up = more price pressure |
| Bubble size | Unemployment rate | Larger = more unemployment |
| Animation | Year (2000 to 2025) | Press Play to watch trajectories unfold |

**Key moments to watch:**
- **2009** - Global Financial Crisis: most bubbles shift sharply left (GDP collapse)
- **2020** - COVID-19: another leftward shock, with recovery visible by 2021
- **China** consistently stays right (high growth) with shrinking bubbles (falling unemployment)
- **Brazil** shows high inflation with volatile growth - a classic emerging-market pattern
    """)

    fig_bubble = px.scatter(
        data[data['economy'].isin(selected_countries)],
        x='GDP Growth (%)', y='Inflation (%)',
        size='Unemployment (%)', color='economy',
        animation_frame='year', animation_group='economy',
        hover_name='economy', size_max=50,
        range_x=[-15, 20], range_y=[-2, 20],
        title='GDP Growth vs Inflation vs Unemployment (2000-2025)',
        labels={'economy': 'Country'},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_bubble.update_layout(height=550)
    st.plotly_chart(fig_bubble, width='stretch')

# TAB 5 - Calculator
with tab5:
    st.subheader("Growth Rate Calculator")
    st.caption("Select a country, indicator, and time period - then see how it compares against all peers over the same period.")

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
                title=f"{calc_indicator} - {calc_country} ({calc_years[0]}-{calc_years[1]})",
                markers=True,
                color_discrete_sequence=['#1D9E75']
            )
            fig_calc.update_layout(height=350)
            st.plotly_chart(fig_calc, width='stretch')

            # FIX 4: peer benchmark panel
            st.markdown("---")
            st.subheader("Peer Comparison - same indicator, same period")
            st.caption(f"How does {calc_country}'s change in {calc_indicator} compare to other economies over {calc_years[0]}-{calc_years[1]}?")

            peer_rows = []
            for country in sorted(data['economy'].unique()):
                c_data = data[
                    (data['economy'] == country) &
                    (data['year'].between(calc_years[0], calc_years[1]))
                ]
                if c_data.empty:
                    continue
                sv = c_data[c_data['year'] == calc_years[0]][calc_indicator].values
                ev = c_data[c_data['year'] == calc_years[1]][calc_indicator].values
                av = c_data[calc_indicator].mean()
                if len(sv) > 0 and len(ev) > 0:
                    peer_rows.append({
                        'Country': country,
                        f'Start ({calc_years[0]}) %': round(sv[0], 2),
                        f'End ({calc_years[1]}) %': round(ev[0], 2),
                        'Change (pp)': round(ev[0] - sv[0], 2),
                        'Period Avg (%)': round(av, 2),
                    })

            if peer_rows:
                peer_df = pd.DataFrame(peer_rows)
                group_avg_change = peer_df['Change (pp)'].mean()

                # Horizontal bar chart
                peer_df_sorted = peer_df.sort_values('Change (pp)', ascending=True)
                bar_colors = [
                    '#1D9E75' if c == calc_country else '#B4B2A9'
                    for c in peer_df_sorted['Country']
                ]
                fig_peer = px.bar(
                    peer_df_sorted,
                    x='Change (pp)', y='Country',
                    orientation='h',
                    title=f"Change in {calc_indicator} ({calc_years[0]}-{calc_years[1]}) - all economies",
                )
                fig_peer.update_traces(marker_color=bar_colors)
                fig_peer.update_layout(showlegend=False, height=320)
                fig_peer.add_vline(
                    x=group_avg_change, line_dash="dash", line_color="gray",
                    annotation_text=f"Group avg: {group_avg_change:.2f} pp",
                    annotation_position="top right"
                )
                st.plotly_chart(fig_peer, width='stretch')

                st.dataframe(peer_df.set_index('Country'), use_container_width=True)

                # Verdict
                higher_is_better = calc_indicator == 'GDP Growth (%)'
                beat_count = sum(
                    1 for _, r in peer_df.iterrows()
                    if r['Country'] != calc_country and (
                        (change > r['Change (pp)']) if higher_is_better
                        else (change < r['Change (pp)'])
                    )
                )
                total_peers = len(peer_df) - 1
                vs_group    = round(change - group_avg_change, 2)
                vs_label    = "above" if vs_group > 0 else "below"
                direction_word = "increased" if change > 0 else "decreased"

                st.info(f"""
**Verdict for {calc_country}**

{calc_country}'s {calc_indicator} **{direction_word} by {abs(change):.2f} pp** from {calc_years[0]} to {calc_years[1]},
vs a group average change of **{group_avg_change:.2f} pp** -
that is **{abs(vs_group):.2f} pp {vs_label} the group average**.

Among the {total_peers} peer economies, {calc_country} performed {"better" if higher_is_better else "with more improvement"} than **{beat_count}** of them on this measure.
                """)
