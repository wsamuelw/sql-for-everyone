#!/usr/bin/env python3
"""
Netatmo Sensor Deep Dive Analysis
10 comprehensive analyses on NZ warehouse office sensor data (2025, 30-min intervals)
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

OUTPUT_FILE = "deep_dive_results.txt"
results = []

def out(text=""):
    """Print and collect output."""
    print(text)
    results.append(text)

# ============================================================
# LOAD & PREPARE
# ============================================================
df = pd.read_excel("Netatmo 2025.xlsx")

# Parse timestamps
df['dt'] = pd.to_datetime(df['Timezone'], format='%Y/%m/%d %H:%M:%S')
df['date'] = df['dt'].dt.date
df['hour'] = df['dt'].dt.hour
df['month'] = df['dt'].dt.month
df['month_name'] = df['dt'].dt.strftime('%B')
df['weekday'] = df['dt'].dt.dayofweek  # 0=Mon, 6=Sun
df['is_weekday'] = df['weekday'] < 5
df['week'] = df['dt'].dt.isocalendar().week.astype(int)
df['year_week'] = df['dt'].dt.strftime('%G-W%V')

# Column shortcuts
col_temp = 'Temperature °C (studio desk)'
col_hum = 'Humidity % (studio desk)'
col_co2 = 'CO2 ppm (studio desk)'
col_noise = 'Noise dB (studio desk)'
col_press = 'Pressure Pa (studio desk)'
col_temp_k = 'Temperature °C (kitchen island)'
col_hum_k = 'Humidity % (kitchen island)'
col_temp_u = 'Temperature °C (upstairs)'
col_hum_u = 'Humidity % (upstairs)'
col_co2_u = 'CO2 ppm (upstairs)'

out("=" * 70)
out("NETATMO SENSOR DEEP DIVE ANALYSIS — NZ Warehouse Office, 2025")
out("=" * 70)
out(f"Dataset: {len(df)} readings, {df['date'].nunique()} days, "
    f"{df['date'].min()} to {df['date'].max()}")
out(f"Interval: 30 minutes | Null values: {df.isnull().sum().sum()}")
out("")

# ============================================================
# DEEP DIVE 1: OCCUPANCY INFERENCE
# ============================================================
out("=" * 70)
out("DEEP DIVE 1: OCCUPANCY INFERENCE")
out("=" * 70)

# Occupancy score: 0 = neither, 1 = one signal, 2 = both
# Use noise > 48 dB (human activity) and CO2 > 490 ppm (elevated above outdoor ~420)
noise_high = (df[col_noise] > 48).astype(int)
co2_high = (df[col_co2] > 490).astype(int)
df['occ_score'] = noise_high + co2_high

# Daily occupancy summary
daily_occ = df.groupby('date').agg(
    occupied_hours=('occ_score', lambda x: (x > 0).sum() * 0.5),
    fully_occupied_hours=('occ_score', lambda x: (x == 2).sum() * 0.5),
    noise_only_hours=('occ_score', lambda x: ((x == 1) & (df.loc[x.index, col_noise] > 48)).sum() * 0.5),
    avg_score=('occ_score', 'mean'),
    reading_count=('occ_score', 'count')
).reset_index()

out("\nDaily Occupancy Summary:")
out(f"  Average occupied hours/day:  {daily_occ['occupied_hours'].mean():.1f} hrs")
out(f"  Average fully-occupied/day:  {daily_occ['fully_occupied_hours'].mean():.1f} hrs")
out(f"  Median occupied hours/day:   {daily_occ['occupied_hours'].median():.1f} hrs")

# Weekday vs weekend
weekday_dates = set(df[df['is_weekday']]['date'].unique())
weekend_dates = set(df[~df['is_weekday']]['date'].unique())

wd_hours = daily_occ[daily_occ['date'].isin(weekday_dates)]['occupied_hours']
we_hours = daily_occ[daily_occ['date'].isin(weekend_dates)]['occupied_hours']
wd_fully = daily_occ[daily_occ['date'].isin(weekday_dates)]['fully_occupied_hours']
we_fully = daily_occ[daily_occ['date'].isin(weekend_dates)]['fully_occupied_hours']

out(f"\nWeekday vs Weekend:")
out(f"  Weekday avg occupied hrs:    {wd_hours.mean():.1f} hrs (n={len(wd_hours)} days)")
out(f"  Weekend avg occupied hrs:    {we_hours.mean():.1f} hrs (n={len(we_hours)} days)")
out(f"  Weekday avg fully-occupied:  {wd_fully.mean():.1f} hrs")
out(f"  Weekend avg fully-occupied:  {we_fully.mean():.1f} hrs")

# Hourly occupancy pattern (weekday only, using noise as primary proxy)
wd_df = df[df['is_weekday']]
hourly_noise_pct = wd_df.groupby('hour')[col_noise].apply(lambda x: (x > 48).mean())
hourly_co2_mean = wd_df.groupby('hour')[col_co2].mean()
hourly_occ_score = wd_df.groupby('hour')['occ_score'].mean()

# Find arrival: first hour where noise% > 20% (threshold for meaningful activity)
noise_threshold = 0.20
active_hours = hourly_noise_pct[hourly_noise_pct > noise_threshold].index
if len(active_hours) > 0:
    # Filter to reasonable arrival window (5am-11am)
    morning_hours = [h for h in active_hours if 5 <= h <= 11]
    arrival_hour = morning_hours[0] if morning_hours else active_hours[0]
    # Find departure: last hour where noise% > 20% (in evening window)
    evening_hours = [h for h in active_hours if h >= 15]
    departure_hour = evening_hours[-1] + 1 if evening_hours else active_hours[-1] + 1
    out(f"\nTypical arrival time (weekday):  {int(arrival_hour):02d}:00")
    out(f"Typical departure time (weekday): {int(departure_hour):02d}:00")

# Lunch break detection: dip in noise between 10-14
midday_noise = hourly_noise_pct.loc[10:14]
if len(midday_noise) > 0:
    lunch_hour = midday_noise.idxmin()
    out(f"Lunch break dip detected at:    {int(lunch_hour):02d}:00 (noise%={midday_noise.min():.0%})")

# Monthly occupancy
monthly_occ2 = df.groupby('month').apply(
    lambda g: (g['occ_score'] > 0).sum() * 0.5 / g['date'].nunique()
).reset_index()
monthly_occ2.columns = ['month', 'avg_occupied_hrs_per_day']
month_names = df.drop_duplicates('month')[['month', 'month_name']].set_index('month')['month_name']
monthly_occ2['month_name'] = monthly_occ2['month'].map(month_names)

busiest_month = monthly_occ2.loc[monthly_occ2['avg_occupied_hrs_per_day'].idxmax()]
quietest_month = monthly_occ2.loc[monthly_occ2['avg_occupied_hrs_per_day'].idxmin()]

out(f"\nBusiest month:  {busiest_month['month_name']} ({busiest_month['avg_occupied_hrs_per_day']:.1f} hrs/day)")
out(f"Quietest month: {quietest_month['month_name']} ({quietest_month['avg_occupied_hrs_per_day']:.1f} hrs/day)")

out("\nHourly occupancy pattern (weekdays):")
out("  Hour   Noise%   CO2(avg)  Score")
for h in range(5, 23):
    n_pct = hourly_noise_pct.get(h, 0)
    c_avg = hourly_co2_mean.get(h, 0)
    s = hourly_occ_score.get(h, 0)
    bar = "#" * int(s * 20)
    out(f"  {h:02d}:00  {n_pct:>6.0%}  {c_avg:>7.0f}   {s:.2f}  {bar}")

out("\nKey Findings:")
out(f"  - Weekdays: {wd_hours.mean():.1f} occupied hrs/day, {wd_fully.mean():.1f} fully-occupied (noise+CO2)")
out(f"  - Weekends: {we_hours.mean():.1f} occupied hrs/day, {we_fully.mean():.1f} fully-occupied")
out(f"  - Typical office hours: ~{int(arrival_hour):02d}:00-{int(departure_hour):02d}:00 with lunch dip at {int(lunch_hour):02d}:00")
out(f"  - {busiest_month['month_name']} busiest ({busiest_month['avg_occupied_hrs_per_day']:.1f} hrs/day), "
    f"{quietest_month['month_name']} quietest ({quietest_month['avg_occupied_hrs_per_day']:.1f} hrs/day)")
out("")

# ============================================================
# DEEP DIVE 2: BUILDING THERMAL RESPONSE TIME
# ============================================================
out("=" * 70)
out("DEEP DIVE 2: BUILDING THERMAL RESPONSE TIME")
out("=" * 70)

def calc_slope(group, start_h, end_h):
    """Calculate temp slope in C/hr for a given hour window."""
    mask = (group['hour'] >= start_h) & (group['hour'] < end_h)
    subset = group[mask]
    if len(subset) < 4:
        return np.nan
    hours = (subset['dt'] - subset['dt'].iloc[0]).dt.total_seconds() / 3600
    temps = subset[col_temp].values
    if np.std(temps) < 0.05:
        return 0.0
    coeffs = np.polyfit(hours, temps, 1)
    return coeffs[0]

# Heating rate: 6am-2pm
daily_heating = df.groupby('date').apply(lambda g: pd.Series({
    'heating_rate': calc_slope(g, 6, 14),
    'month': g['month'].iloc[0],
    'month_name': g['month_name'].iloc[0]
})).reset_index()

# Cooling rate: overnight (18:00-06:00 wrapping midnight)
def calc_cooling_rate(group):
    night = group[(group['hour'] >= 18) | (group['hour'] < 6)]
    if len(night) < 6:
        return np.nan
    hours = (night['dt'] - night['dt'].iloc[0]).dt.total_seconds() / 3600
    temps = night[col_temp].values
    if np.std(temps) < 0.05:
        return 0.0
    coeffs = np.polyfit(hours, temps, 1)
    return coeffs[0]

daily_heating['cooling_rate'] = df.groupby('date').apply(calc_cooling_rate).reset_index(level=0, drop=True)

monthly_thermal = daily_heating.groupby(['month', 'month_name']).agg(
    heating_rate=('heating_rate', 'mean'),
    cooling_rate=('cooling_rate', 'mean')
).reset_index()

out("\nMonthly Heating/Cooling Rates (C/hr):")
out(f"  {'Month':<12} {'Heating Rate':>14} {'Cooling Rate':>14}")
out(f"  {'-'*12} {'-'*14} {'-'*14}")
for _, row in monthly_thermal.iterrows():
    out(f"  {row['month_name']:<12} {row['heating_rate']:>+14.3f} {row['cooling_rate']:>+14.3f}")

# Winter (NZ: Jun-Aug) vs Summer (Dec-Feb)
nz_winter = monthly_thermal[monthly_thermal['month'].isin([6, 7, 8])]
nz_summer = monthly_thermal[monthly_thermal['month'].isin([12, 1, 2])]

out(f"\nWinter (Jun-Aug) avg heating rate: {nz_winter['heating_rate'].mean():+.3f} C/hr")
out(f"Summer (Dec-Feb) avg heating rate: {nz_summer['heating_rate'].mean():+.3f} C/hr")
out(f"Winter avg cooling rate:            {nz_winter['cooling_rate'].mean():+.3f} C/hr")
out(f"Summer avg cooling rate:            {nz_summer['cooling_rate'].mean():+.3f} C/hr")

# Post-departure temperature decay
post_depart = df[(df['hour'] >= 17) & (df['hour'] <= 23) & df['is_weekday']].copy()
daily_temp_decay = post_depart.groupby('date').apply(
    lambda g: g[col_temp].iloc[-1] - g[col_temp].iloc[0] if len(g) >= 4 else np.nan
).dropna()

avg_temp_drop = daily_temp_decay.mean()
drop_rate = abs(avg_temp_drop / 6)  # C/hr over 6 hours

out(f"\nPost-departure temp change (17:00-23:00): {avg_temp_drop:+.2f} C (avg)")
out(f"Average temp drop rate: {drop_rate:.3f} C/hr")

# Half-life of temp decay
# Using exponential decay model: T(t) = T_ambient + (T_peak - T_ambient) * e^(-t/tau)
# half-life = tau * ln(2)
# From the data, peak-to-ambient drop rate gives us tau
# If temp drops by X over 6 hours from peak, and ambient is the overnight min
wd_hourly_temp = df[df['is_weekday']].groupby('hour')[col_temp].mean()
peak_temp = wd_hourly_temp.loc[17]  # approx peak at 5pm
ambient_temp = wd_hourly_temp.loc[5]  # approx ambient at 5am
if peak_temp > ambient_temp:
    decay_fraction = avg_temp_drop / (ambient_temp - peak_temp)  # fraction of total decay
    # -6/tau = ln(1 + decay_fraction)
    tau = -6 / np.log(1 + decay_fraction) if decay_fraction > -1 else np.nan
    half_life = np.log(2) * abs(tau) if not np.isnan(tau) else np.nan
else:
    half_life = np.nan

if not np.isnan(half_life):
    out(f"Temperature half-life (post-occupancy): {half_life:.1f} hours")

insulation_rating = "GOOD" if abs(nz_winter['cooling_rate'].mean()) < 0.3 else "POOR" if abs(nz_winter['cooling_rate'].mean()) > 0.5 else "MODERATE"
out(f"\nInsulation assessment: {insulation_rating} (winter cooling rate: {abs(nz_winter['cooling_rate'].mean()):.3f} C/hr)")

out("\nKey Findings:")
out(f"  - Building heats at {nz_winter['heating_rate'].mean():+.3f} C/hr in winter, {nz_summer['heating_rate'].mean():+.3f} C/hr in summer")
out(f"  - Cooling rate in winter: {abs(nz_winter['cooling_rate'].mean()):.3f} C/hr | summer: {abs(nz_summer['cooling_rate'].mean()):.3f} C/hr")
out(f"  - Insulation is {insulation_rating} — {'minimal heat loss overnight' if insulation_rating == 'GOOD' else 'significant heat loss overnight'}")
out(f"  - Post-departure temp drops {abs(avg_temp_drop):.1f}C over ~6 hours ({drop_rate:.3f} C/hr)")
if not np.isnan(half_life):
    out(f"  - Temperature half-life after occupancy ends: ~{half_life:.0f} hours")
out("")

# ============================================================
# DEEP DIVE 3: CO2 ACCUMULATION RATE
# ============================================================
out("=" * 70)
out("DEEP DIVE 3: CO2 ACCUMULATION RATE")
out("=" * 70)

def calc_co2_slope(group, start_h, end_h):
    mask = (group['hour'] >= start_h) & (group['hour'] < end_h)
    subset = group[mask]
    if len(subset) < 4:
        return np.nan
    hours = (subset['dt'] - subset['dt'].iloc[0]).dt.total_seconds() / 3600
    co2 = subset[col_co2].values
    coeffs = np.polyfit(hours, co2, 1)
    return coeffs[0]

daily_co2 = df.groupby('date').apply(lambda g: pd.Series({
    'co2_rising_slope': calc_co2_slope(g, 7, 14),
    'month': g['month'].iloc[0],
    'month_name': g['month_name'].iloc[0],
    'is_weekday': g['is_weekday'].iloc[0]
})).reset_index()

daily_co2['co2_falling_slope'] = df.groupby('date').apply(
    lambda g: calc_co2_slope(g, 18, 30)
).reset_index(level=0, drop=True)

# Estimate occupancy using correct formula:
# N = (dCO2/dt * V) / (q * (Ci - Co))
# V = 200 m3 = 200,000 L
# q = 0.0048 m3/min = 0.288 m3/hr per person (net CO2 exhaled minus inhaled)
# Ci - Co = net indoor CO2 above outdoor (~420 ppm)
# Simplified: N = (dCO2/dt [ppm/hr] * 200,000 [L]) / (0.288 [m3/hr] * 1e6)
VOLUME = 200_000  # litres
Q_PERSON_M3HR = 0.288  # m3/hr net CO2 per person
OUTDOOR_CO2 = 420  # ppm

daily_co2['est_occupancy'] = (
    daily_co2['co2_rising_slope'] * VOLUME / (Q_PERSON_M3HR * 1_000_000)
)
daily_co2['est_occupancy'] = daily_co2['est_occupancy'].clip(lower=0)

out("\nCO2 Accumulation Rates by Month:")
out(f"  {'Month':<12} {'Rising (ppm/hr)':>16} {'Falling (ppm/hr)':>17} {'Est. People':>12}")
out(f"  {'-'*12} {'-'*16} {'-'*17} {'-'*12}")
monthly_co2 = daily_co2.groupby(['month', 'month_name']).agg(
    rising=('co2_rising_slope', 'mean'),
    falling=('co2_falling_slope', 'mean'),
    occ=('est_occupancy', 'mean')
).reset_index()
for _, row in monthly_co2.iterrows():
    out(f"  {row['month_name']:<12} {row['rising']:>+16.1f} {row['falling']:>+17.1f} {row['occ']:>12.1f}")

# Seasonal comparison
wd_co2 = daily_co2[daily_co2['is_weekday']]
out(f"\nWeekday avg rising slope:   {wd_co2['co2_rising_slope'].mean():+.1f} ppm/hr")
out(f"Weekday avg falling slope:  {wd_co2['co2_falling_slope'].mean():+.1f} ppm/hr")
out(f"Weekday avg est. occupants: {wd_co2['est_occupancy'].mean():.1f}")

winter_co2 = daily_co2[daily_co2['month'].isin([6, 7, 8])]
summer_co2 = daily_co2[daily_co2['month'].isin([12, 1, 2])]
out(f"\nWinter rising slope:  {winter_co2['co2_rising_slope'].mean():+.1f} ppm/hr (est {winter_co2['est_occupancy'].mean():.1f} people)")
out(f"Summer rising slope:  {summer_co2['co2_rising_slope'].mean():+.1f} ppm/hr (est {summer_co2['est_occupancy'].mean():.1f} people)")

# Also look at peak hourly CO2 as a simpler occupancy indicator
peak_hourly_co2 = wd_df.groupby('hour')[col_co2].mean()
peak_occupancy_hour = peak_hourly_co2.idxmax()
out(f"\nPeak CO2 hour: {peak_occupancy_hour:02d}:00 (avg {peak_hourly_co2.max():.0f} ppm)")

out("\nKey Findings:")
out(f"  - Weekday CO2 rises at {wd_co2['co2_rising_slope'].mean():+.1f} ppm/hr (7am-2pm)")
out(f"  - CO2 falls at {wd_co2['co2_falling_slope'].mean():+.1f} ppm/hr overnight (natural ventilation)")
out(f"  - Estimated average {wd_co2['est_occupancy'].mean():.1f} people during occupied hours")
out(f"  - Peak CO2 at {peak_occupancy_hour:02d}:00 ({peak_hourly_co2.max():.0f} ppm avg) — {'winter' if winter_co2['co2_rising_slope'].mean() > summer_co2['co2_rising_slope'].mean() else 'summer'} has higher accumulation (windows closed)")
out("")

# ============================================================
# DEEP DIVE 4: PRESSURE AS WEATHER PROXY
# ============================================================
out("=" * 70)
out("DEEP DIVE 4: PRESSURE AS WEATHER PROXY")
out("=" * 70)

# Pressure in hPa (the column values ~1004 are hPa)
df['dp_dt'] = df[col_press].diff() / 0.5  # Change per hour (30-min interval)

# Rapid pressure drops
df['rapid_drop'] = df['dp_dt'] < -2  # < -2 hPa/hr

monthly_press = df.groupby(['month', 'month_name']).agg(
    mean_pressure=(col_press, 'mean'),
    max_drop_rate=('dp_dt', 'min'),
    rapid_drop_pct=('rapid_drop', 'mean')
).reset_index()

out("\nMonthly Pressure Summary:")
out(f"  {'Month':<12} {'Mean (hPa)':>12} {'Max Drop Rate':>14} {'Rapid Drop %':>14}")
out(f"  {'-'*12} {'-'*12} {'-'*14} {'-'*14}")
for _, row in monthly_press.iterrows():
    out(f"  {row['month_name']:<12} {row['mean_pressure']:>12.1f} {row['max_drop_rate']:>+14.2f} {row['rapid_drop_pct']:>13.1%}")

# Correlate pressure drops with subsequent indoor conditions (6-12hr lag)
df['press_change_6hr'] = df[col_press].diff(12)
df['press_change_12hr'] = df[col_press].diff(24)

# Correlation between pressure change and subsequent temp/humidity change
temp_change_6hr = df[col_temp].diff(12)
hum_change_6hr = df[col_hum].diff(12)

valid_mask = df['press_change_6hr'].notna() & temp_change_6hr.notna() & hum_change_6hr.notna()
corr_press_temp = df.loc[valid_mask, 'press_change_6hr'].corr(temp_change_6hr[valid_mask])
corr_press_hum = df.loc[valid_mask, 'press_change_6hr'].corr(hum_change_6hr[valid_mask])

out(f"\nPressure-indoor correlations (6hr lag):")
out(f"  dPressure vs dTemperature: {corr_press_temp:+.3f}")
out(f"  dPressure vs dHumidity:    {corr_press_hum:+.3f}")

# Storm analysis: find major pressure drops and subsequent indoor changes
storm_events = df[df['press_change_6hr'] < -4].copy()  # >4 hPa drop in 6hrs
if len(storm_events) > 0:
    out(f"\nSignificant storm events (>4 hPa drop in 6hrs): {len(storm_events)}")
    # For each storm event, look at indoor changes 6-12hr later
    temp_responses = []
    hum_responses = []
    for idx in storm_events.index:
        future_idx = idx + 24  # 12 hours ahead
        if future_idx in df.index:
            temp_change = df.loc[future_idx, col_temp] - df.loc[idx, col_temp]
            hum_change = df.loc[future_idx, col_hum] - df.loc[idx, col_hum]
            temp_responses.append(temp_change)
            hum_responses.append(hum_change)
    if temp_responses:
        out(f"  Avg temp change 12hr after storm: {np.mean(temp_responses):+.2f} C")
        out(f"  Avg humidity change 12hr after:   {np.mean(hum_responses):+.1f}%")

out(f"\nRapid pressure drop events (< -2 hPa/hr): {df['rapid_drop'].sum()} instances")
out(f"Percentage of time with rapid drops: {df['rapid_drop'].mean():.1%}")

out("\nKey Findings:")
out(f"  - {df['rapid_drop'].sum()} rapid pressure drop events detected (< -2 hPa/hr)")
out(f"  - Most common in {monthly_press.loc[monthly_press['rapid_drop_pct'].idxmax(), 'month_name']} ({monthly_press['rapid_drop_pct'].max():.1%} of readings)")
out(f"  - Pressure-temp correlation (6hr lag): {corr_press_temp:+.3f} — {'weak' if abs(corr_press_temp) < 0.2 else 'moderate' if abs(corr_press_temp) < 0.4 else 'strong'}")
out(f"  - Pressure-humidity correlation (6hr lag): {corr_press_hum:+.3f}")
out("")

# ============================================================
# DEEP DIVE 5: CROSS-ROOM PREDICTABILITY
# ============================================================
out("=" * 70)
out("DEEP DIVE 5: CROSS-ROOM PREDICTABILITY")
out("=" * 70)

def cross_corr(x, y, lag):
    """Cross-correlation at a given lag (in 30-min steps)."""
    if lag > 0:
        x_vals = x.iloc[lag:].values
        y_vals = y.iloc[:-lag].values
    elif lag < 0:
        x_vals = x.iloc[:lag].values
        y_vals = y.iloc[-lag:].values
    else:
        x_vals = x.values
        y_vals = y.values

    min_len = min(len(x_vals), len(y_vals))
    if min_len < 10:
        return np.nan
    x_vals = x_vals[:min_len]
    y_vals = y_vals[:min_len]
    mask = ~(np.isnan(x_vals) | np.isnan(y_vals))
    if mask.sum() < 10:
        return np.nan
    return np.corrcoef(x_vals[mask], y_vals[mask])[0, 1]

lags = [0, 1, 2, 3, 4, 5, 6]  # 0=same time, 1=30min, etc

# Studio vs Upstairs
out("\nStudio vs Upstairs Temperature Cross-Correlation:")
out(f"  {'Lag':>8} {'Minutes':>8} {'Correlation':>12}")
out(f"  {'-'*8} {'-'*8} {'-'*12}")
st_u_corrs = {}
for lag in lags:
    c = cross_corr(df[col_temp], df[col_temp_u], lag)
    st_u_corrs[lag] = c
    out(f"  {lag:>8} {lag*30:>8} {c:>12.4f}")

best_lag_st_u = max(st_u_corrs, key=lambda k: st_u_corrs[k] if not np.isnan(st_u_corrs[k]) else -1)

# Studio vs Kitchen
out("\nStudio vs Kitchen Island Temperature Cross-Correlation:")
st_k_corrs = {}
for lag in lags:
    c = cross_corr(df[col_temp], df[col_temp_k], lag)
    st_k_corrs[lag] = c
    out(f"  {lag:>8} {lag*30:>8} {c:>12.4f}")

best_lag_st_k = max(st_k_corrs, key=lambda k: st_k_corrs[k] if not np.isnan(st_k_corrs[k]) else -1)

# R-squared for linear model
def r_squared(x, y):
    mask = ~(np.isnan(x) | np.isnan(y))
    if mask.sum() < 10:
        return np.nan
    x_m, y_m = x[mask], y[mask]
    coeffs = np.polyfit(x_m, y_m, 1)
    predicted = np.polyval(coeffs, x_m)
    ss_res = np.sum((y_m - predicted) ** 2)
    ss_tot = np.sum((y_m - np.mean(y_m)) ** 2)
    return 1 - ss_res / ss_tot if ss_tot > 0 else np.nan

# Compute R2 at best lag
if best_lag_st_u > 0:
    x_u = df[col_temp].iloc[best_lag_st_u:].values
    y_u = df[col_temp_u].iloc[:-best_lag_st_u].values
else:
    x_u = df[col_temp].values
    y_u = df[col_temp_u].values
min_u = min(len(x_u), len(y_u))
r2_st_u = r_squared(x_u[:min_u], y_u[:min_u])

if best_lag_st_k > 0:
    x_k = df[col_temp].iloc[best_lag_st_k:].values
    y_k = df[col_temp_k].iloc[:-best_lag_st_k].values
else:
    x_k = df[col_temp].values
    y_k = df[col_temp_k].values
min_k = min(len(x_k), len(y_k))
r2_st_k = r_squared(x_k[:min_k], y_k[:min_k])

# Also compute R2 at lag=0 for baseline comparison
r2_st_u_0 = r_squared(df[col_temp].values, df[col_temp_u].values)
r2_st_k_0 = r_squared(df[col_temp].values, df[col_temp_k].values)

out(f"\nBest prediction models:")
out(f"  Upstairs = f(Studio, lag={best_lag_st_u*30}min): R² = {r2_st_u:.4f} (lag-0 baseline: {r2_st_u_0:.4f})")
out(f"  Kitchen  = f(Studio, lag={best_lag_st_k*30}min): R² = {r2_st_k:.4f} (lag-0 baseline: {r2_st_k_0:.4f})")

thermal_lag = best_lag_st_u * 30
out(f"\nThermal lag between floors: {thermal_lag} minutes")

# Diurnal amplitude comparison
studio_range = df.groupby('date')[col_temp].agg(lambda x: x.max() - x.mean())
upstairs_range = df.groupby('date')[col_temp_u].agg(lambda x: x.max() - x.mean())
kitchen_range = df.groupby('date')[col_temp_k].agg(lambda x: x.max() - x.mean())

out(f"\nDaily temperature amplitude (max - mean):")
out(f"  Studio:     {studio_range.mean():.2f} C avg")
out(f"  Kitchen:    {kitchen_range.mean():.2f} C avg")
out(f"  Upstairs:   {upstairs_range.mean():.2f} C avg")

out("\nKey Findings:")
out(f"  - Studio-Upstairs peak correlation at lag {best_lag_st_u*30}min (R²={r2_st_u:.4f})")
out(f"  - Studio-Kitchen peak correlation at lag {best_lag_st_k*30}min (R²={r2_st_k:.4f})")
out(f"  - {'Upstairs follows studio with a ' + str(thermal_lag) + 'min thermal lag' if thermal_lag > 0 else 'No significant thermal lag between floors — they respond simultaneously'}")
out(f"  - Kitchen tracks studio closely (R²={r2_st_k:.3f}), {'smaller' if kitchen_range.mean() < studio_range.mean() else 'larger'} temp swings than studio")
out("")

# ============================================================
# DEEP DIVE 6: ANOMALY DETECTION
# ============================================================
out("=" * 70)
out("DEEP DIVE 6: ANOMALY DETECTION")
out("=" * 70)

metrics = {
    'Temperature (C)': col_temp,
    'Humidity (%)': col_hum,
    'CO2 (ppm)': col_co2,
    'Noise (dB)': col_noise,
    'Pressure (hPa)': col_press
}

df['anomaly_score'] = 0.0

for name, col in metrics.items():
    expected = df.groupby(['hour', 'month'])[col].transform('mean')
    std = df.groupby(['hour', 'month'])[col].transform('std')
    std = std.replace(0, np.nan)
    df[f'z_{name}'] = (df[col] - expected) / std
    df[f'z_{name}'] = df[f'z_{name}'].fillna(0)
    df['anomaly_score'] = df[['anomaly_score', f'z_{name}']].abs().max(axis=1)

# Daily anomaly aggregation
daily_anomaly = df.groupby('date').agg(
    max_z=('anomaly_score', 'max'),
    mean_z=('anomaly_score', 'mean'),
    temp_anomaly=('z_Temperature (C)', lambda x: x.abs().max()),
    hum_anomaly=('z_Humidity (%)', lambda x: x.abs().max()),
    co2_anomaly=('z_CO2 (ppm)', lambda x: x.abs().max()),
    noise_anomaly=('z_Noise (dB)', lambda x: x.abs().max()),
    press_anomaly=('z_Pressure (hPa)', lambda x: x.abs().max())
).reset_index()

def worst_metric(row):
    scores = {
        'Temperature': row['temp_anomaly'],
        'Humidity': row['hum_anomaly'],
        'CO2': row['co2_anomaly'],
        'Noise': row['noise_anomaly'],
        'Pressure': row['press_anomaly']
    }
    return max(scores, key=scores.get)

daily_anomaly['worst_metric'] = daily_anomaly.apply(worst_metric, axis=1)

top20 = daily_anomaly.nlargest(20, 'max_z')

out("\nTop 20 Most Anomalous Days:")
out(f"  {'Date':<12} {'Score':>7} {'Worst Metric':<14} {'Temp z':>7} {'Hum z':>7} {'CO2 z':>7} {'Noise z':>7} {'Press z':>7}")
out(f"  {'-'*12} {'-'*7} {'-'*14} {'-'*7} {'-'*7} {'-'*7} {'-'*7} {'-'*7}")
for _, row in top20.iterrows():
    out(f"  {str(row['date']):<12} {row['max_z']:>7.1f} {row['worst_metric']:<14} "
        f"{row['temp_anomaly']:>7.1f} {row['hum_anomaly']:>7.1f} {row['co2_anomaly']:>7.1f} "
        f"{row['noise_anomaly']:>7.1f} {row['press_anomaly']:>7.1f}")

# Anomaly categories
anomaly_days = daily_anomaly[daily_anomaly['max_z'] > 2.5]
out(f"\nDays with significant anomalies (score > 2.5): {len(anomaly_days)}")

out(f"\nAnomaly breakdown by type (readings with |z| > 2.5):")
for name, col in metrics.items():
    count = (df[f'z_{name}'].abs() > 2.5).sum()
    out(f"  {name}: {count} readings ({count/len(df)*100:.2f}%)")

out("\nKey Findings:")
out(f"  - {len(anomaly_days)} days flagged with anomalous behavior (score > 2.5)")
anomaly_type_counts = top20['worst_metric'].value_counts()
out(f"  - Most common anomaly type: {anomaly_type_counts.index[0]} ({anomaly_type_counts.iloc[0]} of top 20)")
out(f"  - Most anomalous day: {top20.iloc[0]['date']} (score={top20.iloc[0]['max_z']:.1f}, driven by {top20.iloc[0]['worst_metric']})")
out("")

# ============================================================
# DEEP DIVE 7: HUMIDITY SOURCE IDENTIFICATION
# ============================================================
out("=" * 70)
out("DEEP DIVE 7: HUMIDITY SOURCE IDENTIFICATION")
out("=" * 70)

# Compute pressure drop metric before taking the high_hum copy
df['press_drop_6hr_min'] = df[col_press].diff(12).rolling(12).min()

high_hum = df[df[col_hum] > 75].copy()
out(f"\nHigh humidity periods (>75%): {len(high_hum)} readings ({len(high_hum)/len(df)*100:.1f}% of all)")

# (a) Weather-driven: high humidity + rapid pressure drop within 6 hours
weather_driven = high_hum[high_hum['press_drop_6hr_min'] < -2]

# (b) Occupancy-driven: high humidity + both noise and CO2 elevated
occupancy_driven = high_hum[(high_hum[col_noise] > 48) & (high_hum[col_co2] > 490)]

# (c) Time-of-day driven: high humidity during early morning (2am-6am) — condensation
tod_driven = high_hum[(high_hum['hour'] >= 2) & (high_hum['hour'] <= 6)]

total_high = len(high_hum)
out(f"\nSource Attribution (overlap possible):")
out(f"  Weather-driven (pressure drops):  {len(weather_driven):>5} readings ({len(weather_driven)/total_high*100:.1f}%)")
out(f"  Occupancy-driven (noise+CO2):     {len(occupancy_driven):>5} readings ({len(occupancy_driven)/total_high*100:.1f}%)")
out(f"  Time-of-day (2-6am condensation): {len(tod_driven):>5} readings ({len(tod_driven)/total_high*100:.1f}%)")

# Exclusive attribution
weather_only = weather_driven[~weather_driven.index.isin(occupancy_driven.index) & ~weather_driven.index.isin(tod_driven.index)]
occupancy_only = occupancy_driven[~occupancy_driven.index.isin(weather_driven.index) & ~occupancy_driven.index.isin(tod_driven.index)]
tod_only = tod_driven[~tod_driven.index.isin(weather_driven.index) & ~tod_driven.index.isin(occupancy_driven.index)]
unattributed = total_high - len(weather_driven) - len(occupancy_driven) - len(tod_driven)

out(f"\nExclusive attribution (non-overlapping):")
out(f"  Weather-only:   {len(weather_only):>5} ({len(weather_only)/total_high*100:.1f}%)")
out(f"  Occupancy-only: {len(occupancy_only):>5} ({len(occupancy_only)/total_high*100:.1f}%)")
out(f"  TOD-only:       {len(tod_only):>5} ({len(tod_only)/total_high*100:.1f}%)")
out(f"  Unclassified:   {unattributed:>5} ({unattributed/total_high*100:.1f}%)")

# Monthly breakdown
out(f"\nHigh humidity by month:")
monthly_hum = df.groupby(['month', 'month_name']).agg(
    high_hum_pct=(col_hum, lambda x: (x > 75).mean()),
    avg_hum=(col_hum, 'mean')
).reset_index()
for _, row in monthly_hum.iterrows():
    bar = "#" * int(row['high_hum_pct'] * 200)
    out(f"  {row['month_name']:<12} {row['high_hum_pct']:>6.1%} avg={row['avg_hum']:.0f}%  {bar}")

most_humid_month = monthly_hum.loc[monthly_hum['high_hum_pct'].idxmax()]
least_humid_month = monthly_hum.loc[monthly_hum['high_hum_pct'].idxmin()]

out("\nKey Findings:")
out(f"  - {len(high_hum)} high-humidity readings (>75%) across the year")
out(f"  - Weather (pressure drops) accounts for {len(weather_driven)/total_high*100:.0f}% of high-humidity events")
out(f"  - Occupancy accounts for {len(occupancy_driven)/total_high*100:.0f}% of high-humidity events")
out(f"  - Most humid month: {most_humid_month['month_name']} ({most_humid_month['high_hum_pct']:.1%} >75%)")
out(f"  - Least humid: {least_humid_month['month_name']} ({least_humid_month['high_hum_pct']:.1%})")
out("")

# ============================================================
# DEEP DIVE 8: ENERGY ESTIMATION
# ============================================================
out("=" * 70)
out("DEEP DIVE 8: ENERGY ESTIMATION")
out("=" * 70)

MASS = 200  # kg
CP = 1005   # J/(kg*K)
TARGET_TEMP = 20.0

# Outdoor proxy: minimum temperature in early morning (4am-6am)
df['outdoor_proxy'] = df[df['hour'].isin([4, 5])].groupby('date')[col_temp].transform('min')
df['outdoor_proxy'] = df.groupby('date')['outdoor_proxy'].transform('first')

daily_energy = df.groupby('date').apply(lambda g: pd.Series({
    'min_temp': g[col_temp].min(),
    'max_temp': g[col_temp].max(),
    'outdoor_proxy': g['outdoor_proxy'].min() if g['outdoor_proxy'].notna().any() else g[col_temp].min(),
    'temp_range': g[col_temp].max() - g[col_temp].min(),
    'month': g['month'].iloc[0],
    'month_name': g['month_name'].iloc[0]
})).reset_index()

daily_energy['heating_degree'] = np.maximum(0, TARGET_TEMP - daily_energy['outdoor_proxy'])

# Energy estimate: Q = m * Cp * dT (to heat the air mass)
# Then account for ventilation losses (rough factor: 2x for infiltration)
daily_energy['heating_energy_kwh'] = (
    daily_energy['heating_degree'] * MASS * CP / 3_600_000  # kWh to heat air mass once
) * 24  # sustained over 24 hours (continuous losses)
# Scale by actual occupied hours fraction
daily_energy['heating_energy_kwh'] = daily_energy['heating_degree'] * 2.4  # simplified kWh/day

monthly_energy = daily_energy.groupby(['month', 'month_name']).agg(
    avg_degree_days=('heating_degree', 'mean'),
    total_degree_days=('heating_degree', 'sum'),
    avg_energy_kwh=('heating_energy_kwh', 'mean'),
    total_energy_kwh=('heating_energy_kwh', 'sum'),
    avg_temp_range=('temp_range', 'mean')
).reset_index()

out("\nMonthly Heating Degree-Days and Energy:")
out(f"  {'Month':<12} {'Avg HDD':>9} {'Total HDD':>11} {'Avg kWh/day':>12} {'Total kWh':>11}")
out(f"  {'-'*12} {'-'*9} {'-'*11} {'-'*12} {'-'*11}")
for _, row in monthly_energy.iterrows():
    out(f"  {row['month_name']:<12} {row['avg_degree_days']:>9.1f} {row['total_degree_days']:>11.0f} "
        f"{row['avg_energy_kwh']:>12.1f} {row['total_energy_kwh']:>11.0f}")

total_hdd = daily_energy['heating_degree'].sum()
total_energy = daily_energy['heating_energy_kwh'].sum()

out(f"\nAnnual totals:")
out(f"  Total heating degree-days: {total_hdd:.0f}")
out(f"  Estimated annual heating energy: {total_energy:,.0f} kWh")
out(f"  Average daily energy: {daily_energy['heating_energy_kwh'].mean():.1f} kWh")
out(f"  Outdoor proxy range: {daily_energy['outdoor_proxy'].min():.1f}C to {daily_energy['outdoor_proxy'].max():.1f}C")

out("\nKey Findings:")
out(f"  - Annual heating requirement: ~{total_hdd:.0f} degree-days")
out(f"  - Estimated annual energy: ~{total_energy:,.0f} kWh (simplified model)")
out(f"  - Peak demand in {monthly_energy.loc[monthly_energy['avg_degree_days'].idxmax(), 'month_name']} "
    f"({monthly_energy['avg_degree_days'].max():.1f} HDD avg)")
out(f"  - Lowest demand in {monthly_energy.loc[monthly_energy['avg_degree_days'].idxmin(), 'month_name']} "
    f"({monthly_energy['avg_degree_days'].min():.1f} HDD avg)")
out("")

# ============================================================
# DEEP DIVE 9: WEEKLY PRODUCTIVITY PROXY
# ============================================================
out("=" * 70)
out("DEEP DIVE 9: WEEKLY PRODUCTIVITY PROXY")
out("=" * 70)

df['noise_above_45'] = np.where(df[col_noise] > 45, df[col_noise] - 45, 0) * 0.5

weekly_noise = df.groupby('year_week').agg(
    noise_total=('noise_above_45', 'sum'),
    high_noise_count=('noise_above_45', lambda x: (x > 0).sum()),
    avg_noise=(col_noise, 'mean'),
    max_noise=(col_noise, 'max'),
    days=('date', 'nunique'),
    week_start=('dt', 'min')
).reset_index()

weekly_noise = weekly_noise[weekly_noise['days'] >= 5]

out(f"\nWeekly Noise Summary (weeks with 5+ days):")
out(f"  Total weeks analyzed: {len(weekly_noise)}")
out(f"  Avg weekly noise score: {weekly_noise['noise_total'].mean():.1f}")
out(f"  Std dev: {weekly_noise['noise_total'].std():.1f}")

top10_noise = weekly_noise.nlargest(10, 'noise_total')
out(f"\nTop 10 Busiest Weeks:")
out(f"  {'Week':<10} {'Start Date':<12} {'Noise Score':>12} {'Avg dB':>8} {'Peak dB':>8} {'Days':>5}")
out(f"  {'-'*10} {'-'*12} {'-'*12} {'-'*8} {'-'*8} {'-'*5}")
for _, row in top10_noise.iterrows():
    out(f"  {row['year_week']:<10} {str(row['week_start'].date()):<12} {row['noise_total']:>12.1f} "
        f"{row['avg_noise']:>8.1f} {row['max_noise']:>8.0f} {row['days']:>5}")

# Monthly noise pattern
monthly_noise = df.groupby(['month', 'month_name']).agg(
    avg_noise=(col_noise, 'mean'),
    pct_high=(col_noise, lambda x: (x > 48).mean()),
    noise_total=('noise_above_45', 'sum')
).reset_index()

out(f"\nMonthly Noise Patterns:")
out(f"  {'Month':<12} {'Avg dB':>8} {'% >48 dB':>10} {'Noise Score':>12}")
out(f"  {'-'*12} {'-'*8} {'-'*10} {'-'*12}")
for _, row in monthly_noise.iterrows():
    bar = "#" * int(row['pct_high'] * 100)
    out(f"  {row['month_name']:<12} {row['avg_noise']:>8.1f} {row['pct_high']:>9.1%} {row['noise_total']:>12.1f}  {bar}")

# Is there a monthly cycle? Check autocorrelation of weekly noise by month
out("\nKey Findings:")
busiest_wk = top10_noise.iloc[0]
quietest_wk = weekly_noise.nsmallest(1, 'noise_total').iloc[0]
noisiest_month = monthly_noise.loc[monthly_noise['avg_noise'].idxmax()]
quietest_month_n = monthly_noise.loc[monthly_noise['avg_noise'].idxmin()]

# Check if noise follows a pattern (comparing summer vs winter months)
summer_noise = monthly_noise[monthly_noise['month'].isin([12, 1, 2])]['avg_noise'].mean()
winter_noise = monthly_noise[monthly_noise['month'].isin([6, 7, 8])]['avg_noise'].mean()
spring_noise = monthly_noise[monthly_noise['month'].isin([9, 10, 11])]['avg_noise'].mean()
autumn_noise = monthly_noise[monthly_noise['month'].isin([3, 4, 5])]['avg_noise'].mean()

out(f"  - Busiest week: {busiest_wk['year_week']} starting {busiest_wk['week_start'].date()} (score={busiest_wk['noise_total']:.0f})")
out(f"  - Quietest week: {quietest_wk['year_week']} starting {quietest_wk['week_start'].date()} (score={quietest_wk['noise_total']:.0f})")
out(f"  - Noisiest month: {noisiest_month['month_name']} (avg {noisiest_month['avg_noise']:.1f} dB)")
out(f"  - Quietest month: {quietest_month_n['month_name']} (avg {quietest_month_n['avg_noise']:.1f} dB)")
out(f"  - Seasonal avg: Summer={summer_noise:.1f}dB, Autumn={autumn_noise:.1f}dB, Winter={winter_noise:.1f}dB, Spring={spring_noise:.1f}dB")
out(f"  - Noise {'follows a seasonal pattern' if monthly_noise['avg_noise'].std() > 1.0 else 'is relatively constant across months'} (monthly std={monthly_noise['avg_noise'].std():.2f} dB)")
out("")

# ============================================================
# DEEP DIVE 10: CO2 HEALTH RISK WINDOWS
# ============================================================
out("=" * 70)
out("DEEP DIVE 10: CO2 HEALTH RISK WINDOWS")
out("=" * 70)

high_co2 = df[col_co2] > 800

# Identify consecutive runs
events = []
in_event = False
start_idx = None

for i in range(len(df)):
    if high_co2.iloc[i] and not in_event:
        in_event = True
        start_idx = i
    elif not high_co2.iloc[i] and in_event:
        in_event = False
        events.append({
            'start_idx': start_idx,
            'end_idx': i - 1,
            'start_time': df.iloc[start_idx]['dt'],
            'end_time': df.iloc[i - 1]['dt'],
            'duration_readings': i - start_idx,
            'duration_hours': (i - start_idx) * 0.5,
            'max_co2': df.iloc[start_idx:i][col_co2].max(),
            'mean_co2': df.iloc[start_idx:i][col_co2].mean(),
            'month': df.iloc[start_idx]['month'],
            'month_name': df.iloc[start_idx]['month_name']
        })

if in_event:
    events.append({
        'start_idx': start_idx,
        'end_idx': len(df) - 1,
        'start_time': df.iloc[start_idx]['dt'],
        'end_time': df.iloc[-1]['dt'],
        'duration_readings': len(df) - start_idx,
        'duration_hours': (len(df) - start_idx) * 0.5,
        'max_co2': df.iloc[start_idx:][col_co2].max(),
        'mean_co2': df.iloc[start_idx:][col_co2].mean(),
        'month': df.iloc[start_idx]['month'],
        'month_name': df.iloc[start_idx]['month_name']
    })

events_df = pd.DataFrame(events) if events else pd.DataFrame()

out(f"\nCO2 > 800 ppm Events: {len(events_df)} total events")

if len(events_df) > 0:
    short = events_df[events_df['duration_hours'] < 1]
    medium = events_df[(events_df['duration_hours'] >= 1) & (events_df['duration_hours'] <= 3)]
    sustained = events_df[events_df['duration_hours'] > 3]

    out(f"\nDuration Categories:")
    out(f"  Short (<1hr):      {len(short):>5} events ({short['duration_hours'].sum():.1f} total hrs)")
    out(f"  Medium (1-3hr):    {len(medium):>5} events ({medium['duration_hours'].sum():.1f} total hrs)")
    out(f"  Sustained (>3hr):  {len(sustained):>5} events ({sustained['duration_hours'].sum():.1f} total hrs)")

    monthly_co2_risk = events_df.groupby(['month', 'month_name']).agg(
        events=('duration_hours', 'count'),
        total_hours=('duration_hours', 'sum'),
        max_co2=('max_co2', 'max'),
        worst_event_hours=('duration_hours', 'max')
    ).reset_index()

    out(f"\nMonthly CO2 Risk Exposure:")
    out(f"  {'Month':<12} {'Events':>8} {'Total Hrs':>10} {'Max CO2':>9} {'Worst Event':>12}")
    out(f"  {'-'*12} {'-'*8} {'-'*10} {'-'*9} {'-'*12}")
    for _, row in monthly_co2_risk.iterrows():
        out(f"  {row['month_name']:<12} {row['events']:>8} {row['total_hours']:>10.1f} {row['max_co2']:>9.0f} {row['worst_event_hours']:>10.1f}h")

    worst = events_df.loc[events_df['duration_hours'].idxmax()]
    out(f"\nWorst Single Event:")
    out(f"  Start: {worst['start_time']}")
    out(f"  End:   {worst['end_time']}")
    out(f"  Duration: {worst['duration_hours']:.1f} hours ({worst['duration_readings']} readings)")
    out(f"  Peak CO2: {worst['max_co2']:.0f} ppm")
    out(f"  Mean CO2: {worst['mean_co2']:.0f} ppm")

    out(f"\nRisk Calendar Summary:")
    out(f"  Total exposure hours (>800ppm): {events_df['duration_hours'].sum():.1f} hrs")
    out(f"  Total events: {len(events_df)}")
    out(f"  Average event duration: {events_df['duration_hours'].mean():.1f} hrs")
    out(f"  Average peak CO2 per event: {events_df['max_co2'].mean():.0f} ppm")

    events_df['season'] = events_df['month'].map(
        lambda m: 'Summer' if m in [12, 1, 2] else 'Autumn' if m in [3, 4, 5] else
                  'Winter' if m in [6, 7, 8] else 'Spring'
    )
    seasonal = events_df.groupby('season').agg(
        events=('duration_hours', 'count'),
        total_hours=('duration_hours', 'sum')
    ).reset_index()
    out(f"\nSeasonal Risk Distribution:")
    for _, row in seasonal.iterrows():
        out(f"  {row['season']:<10} {row['events']:>5} events, {row['total_hours']:.1f} hours")

out("\nKey Findings:")
if len(events_df) > 0:
    out(f"  - {len(events_df)} CO2 exceedance events (>800 ppm) totaling {events_df['duration_hours'].sum():.0f} hours")
    out(f"  - {len(sustained)} sustained events (>3hr) — most concerning for health")
    out(f"  - Worst event: {worst['duration_hours']:.0f}hrs at {worst['start_time'].date()}, peak {worst['max_co2']:.0f} ppm")
    worst_risk_month = monthly_co2_risk.loc[monthly_co2_risk['total_hours'].idxmax()]
    out(f"  - Highest risk month: {worst_risk_month['month_name']} ({worst_risk_month['total_hours']:.0f} hours exposure)")
    out(f"  - Recommendation: {'Ventilation adequate' if events_df['duration_hours'].sum() < 50 else 'Consider improving ventilation during occupied hours — sustained CO2 >800ppm causes drowsiness and reduced cognitive function'}")
else:
    out("  - No CO2 exceedance events found!")

out("")
out("=" * 70)
out("ANALYSIS COMPLETE")
out("=" * 70)

# Save results
with open(OUTPUT_FILE, 'w') as f:
    f.write('\n'.join(results))
print(f"\nResults saved to {OUTPUT_FILE}")
