import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import linregress

# Title
st.title("🌍 COVID-19 Vaccination Tracker")

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv('country_vaccinations.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

# Sidebar - Country selection
countries = df['country'].dropna().unique().tolist()
selected_countries = st.sidebar.multiselect("Select Countries", countries, default=['United States', 'India', 'United Kingdom'])

# Sidebar - Metric selection
metrics = ['total_vaccinations', 'people_vaccinated_per_hundred', 'daily_vaccinations']
selected_metric = st.sidebar.selectbox("Select Metric to Display", metrics)

# Filtered Data
filtered_df = df[df['country'].isin(selected_countries)]

# Line Chart
st.subheader(f"{selected_metric.replace('_', ' ').title()} Over Time")
fig, ax = plt.subplots(figsize=(10, 5))
for country in selected_countries:
    country_df = filtered_df[filtered_df['country'] == country]
    ax.plot(country_df['date'], country_df[selected_metric], label=country)

ax.set_xlabel("Date")
ax.set_ylabel(selected_metric.replace('_', ' ').title())
ax.legend()
st.pyplot(fig)

# Latest Total Vaccinations
st.subheader("💉 Latest Total Vaccinations")
latest = filtered_df[filtered_df['date'] == filtered_df['date'].max()]
latest = latest[['country', 'total_vaccinations']].dropna()
st.bar_chart(latest.set_index('country'))

# Summary Statistics
st.subheader("📊 Summary Statistics")
summary = filtered_df.groupby('country')[selected_metric].describe()[['mean', 'std', 'min', '50%', 'max']]
st.dataframe(summary.rename(columns={'50%': 'median'}).style.format("{:.2f}"))

# Correlation Matrix (Optional)
if st.checkbox("Show Correlation Matrix"):
    corr_df = filtered_df[['total_vaccinations', 'people_vaccinated_per_hundred', 'daily_vaccinations']].dropna()
    st.write("Correlation Matrix:")
    st.dataframe(corr_df.corr().style.background_gradient(cmap='coolwarm'))

# Trend Analysis (Simple Linear Regression)
st.subheader("📉 Trend Analysis")
trend_country = st.selectbox("Select Country for Trend", selected_countries)
country_data = filtered_df[filtered_df['country'] == trend_country].dropna(subset=[selected_metric])
country_data['ordinal_date'] = country_data['date'].map(pd.Timestamp.toordinal)

# Linear regression
slope, intercept, r_value, p_value, std_err = linregress(country_data['ordinal_date'], country_data[selected_metric])

st.write(f"📈 **Trend Line Slope** for {selected_metric.replace('_', ' ')} in {trend_country}: {slope:.2f}")
st.write(f"📊 **R-squared**: {r_value**2:.3f} | **P-value**: {p_value:.4f}")

# Plot trend
fig2, ax2 = plt.subplots(figsize=(8, 4))
ax2.plot(country_data['date'], country_data[selected_metric], label='Actual')
ax2.plot(country_data['date'], intercept + slope * country_data['ordinal_date'], label='Trend', linestyle='--')
ax2.set_title(f"Trend of {selected_metric.replace('_', ' ')} in {trend_country}")
ax2.legend()
st.pyplot(fig2)
