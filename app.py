import streamlit as st
import pandas as pd
import plotly.express as px

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
    indicators = ['GDP Growth (%)', 'Inflation (%)', 'Unemployment (%)']
    for col in indicators:
        data[col] = data.groupby('economy')[col].transform(
            lambda x: x.fillna(x.mean())
        )
    return data

data = load_data()
indicators = ['GDP Growth (%)', 'Inflation (%)', 'Unemployment (%)']

# Sidebar 
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/8/87/Globe_icon_2.svg", width=60)
st.sidebar.title("Dashboard Controls")

all_countries = sorted(data['economy'].unique())
selected_countries = st.sidebar.multiselect(
    "Select Countries",
    options=all_countries,
    default=all_countries
)

year_min, year_max = int(data['year'].min()), int(data['year'].max())
selected_years = st.sidebar.slider(
    "Select Year Range",
    min_value=year_min,
    max_value=year_max,
    value=(2000, 2025)
)

selected_indicator = st.sidebar.selectbox(
    "Select Indicator for Trend Chart",
    options=indicators,
    index=0
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
st.title("🌍 Global Macro Dashboard")
st.markdown("Explore GDP Growth, Inflation, and Unemployment trends across 7 major economies (2000–2025).")
st.markdown("---")

# Metric Cards 
latest_year = filtered['year'].max()
latest = filtered[filtered['year'] == latest_year]

st.subheader(f"Snapshot — {latest_year}")
cols = st.columns(len(selected_countries))
for i, country in enumerate(selected_countries):
    row = latest[latest['economy'] == country]
    if not row.empty:
        gdp = row['GDP Growth (%)'].values[0]
        inf = row['Inflation (%)'].values[0]
        une = row['Unemployment (%)'].values[0]
        with cols[i]:
            st.metric(label=f"🏳️ {country}", value=f"{gdp:.1f}%", delta="GDP Growth")
            st.caption(f"Inflation: {inf:.1f}% | Unemployment: {une:.1f}%")

st.markdown("---")

# Trend Chart 
st.subheader(f"{selected_indicator} Trend — {selected_years[0]} to {selected_years[1]}")
fig_line = px.line(
    filtered,
    x='year', y=selected_indicator,
    color='economy',
    markers=True,
    labels={'year': 'Year', 'economy': 'Country'},
    color_discrete_sequence=px.colors.qualitative.Set2
)
fig_line.update_layout(hovermode='x unified', height=420)
st.plotly_chart(fig_line, width='stretch')

# Bar Chart
st.subheader(f"Country Comparison — {latest_year}")
col1, col2, col3 = st.columns(3)

for col, ind in zip([col1, col2, col3], indicators):
    fig_bar = px.bar(
        latest[latest['economy'].isin(selected_countries)].sort_values(ind, ascending=False),
        x='economy', y=ind,
        color='economy',
        labels={'economy': 'Country'},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_bar.update_layout(showlegend=False, height=300)
    col.plotly_chart(fig_bar, width='stretch')

# Summary Table 
st.markdown("---")
st.subheader("Summary Statistics (Selected Period)")
summary = filtered.groupby('economy')[indicators].mean().round(2).reset_index()
summary.columns = ['Country', 'Avg GDP Growth (%)', 'Avg Inflation (%)', 'Avg Unemployment (%)']
st.dataframe(summary, width='stretch', hide_index=True)

# Key Insights 
st.markdown("---")
st.subheader("Key Insights")
avg = filtered.groupby('economy')[indicators].mean().round(2)
if not avg.empty:
    for ind in indicators:
        top    = avg[ind].idxmax()
        bottom = avg[ind].idxmin()
        st.markdown(f"**{ind}:** Highest average → `{top}` ({avg.loc[top, ind]}%) | Lowest → `{bottom}` ({avg.loc[bottom, ind]}%)")