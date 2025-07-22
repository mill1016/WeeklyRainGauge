import streamlit as st
import requests
from datetime import date, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

API_KEY = "e1f10a1e78da46f5b10a1e78da96f525"
STATIONS = ["KMNMINNE101", "KMNEDINA46", "KMNMINNE53", "KMNMINNE824", "KMNSAINT469"]
BASE_URL = "https://api.weather.com/v2/pws/history/all"

def get_precip_for_day(station_id, date_str):
    params = {
        "stationId": station_id,
        "date": date_str,
        "format": "json",
        "units": "e",
        "apiKey": API_KEY
    }
    try:
        r = requests.get(BASE_URL, params=params)
        r.raise_for_status()
        data = r.json()
        observations = data.get("observations", [])
        if not observations:
            return 0.0
        precip_values = [
            obs["imperial"].get("precipTotal", 0.0)
            for obs in observations if "imperial" in obs
        ]
        return max(precip_values) if precip_values else 0.0
    except Exception as e:
        st.error(f"Error fetching data for {station_id} on {date_str}: {e}")
        return 0.0

st.set_page_config(page_title="Edina Precip Tracker", layout="wide")
#st.title("🌧️ Edina Precipitation Tracker")

# Loop through last 7 days
today = date.today()
daily_avg = []
for i in range(1, 8):
    d = today - timedelta(days=i)
    ds_api = d.strftime("%Y%m%d")
    ds_label = d.isoformat()
    station_precips = [get_precip_for_day(s, ds_api) for s in STATIONS]
    avg_precip = sum(station_precips) / len(station_precips)
    daily_avg.append((ds_label, avg_precip))

# Build DataFrame
df = pd.DataFrame(daily_avg, columns=["Date", "Avg Precip [in]"]).sort_values("Date")
df["Date"] = pd.to_datetime(df["Date"])
df["7-Day Cumulative"] = df["Avg Precip [in]"].rolling(7, min_periods=1).sum()

# Plotting
fig, ax1 = plt.subplots(figsize=(10, 6))
ax1.bar(df['Date'], df['Avg Precip [in]'], color='cornflowerblue', label='Daily Precipitation')
ax1.set_ylabel('Daily Precipitation [in]', color='black')
ax1.tick_params(axis='y', labelcolor='black')
ax1.set_xlabel('Date')
ax1.set_xticks(df['Date'])
ax1.set_xticklabels(df['Date'].dt.strftime('%a\n%m-%d'))

ax2 = ax1.twinx()
ax2.plot(df['Date'], df['7-Day Cumulative'], color='steelblue', label='7-Day Cumulative')
ax2.set_ylabel('7-Day Cumulative Total [in]', color='black')
ax2.tick_params(axis='y', labelcolor='black')

y_min = 0  # Assuming you always want to start at 0
y_max = max(df['Avg Precip [in]'].max(), df['7-Day Cumulative'].max())*1.1
# Set both axes to the same y-limits
ax1.set_ylim(y_min, y_max)
ax2.set_ylim(y_min, y_max)

fig.suptitle("Edina Precipitation - Last 7 Days")
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
plt.tight_layout()

st.pyplot(fig)

#st.dataframe(df.set_index("Date"))