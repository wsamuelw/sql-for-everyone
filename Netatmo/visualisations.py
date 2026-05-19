import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from matplotlib.gridspec import GridSpec

plt.rcParams.update({
    'figure.facecolor': '#0d1117',
    'axes.facecolor': '#161b22',
    'axes.edgecolor': '#30363d',
    'axes.labelcolor': '#c9d1d9',
    'text.color': '#c9d1d9',
    'xtick.color': '#8b949e',
    'ytick.color': '#8b949e',
    'grid.color': '#21262d',
    'figure.dpi': 150,
    'font.family': 'sans-serif',
    'font.size': 10,
})

df = pd.read_excel('Netatmo 2025.xlsx', sheet_name='Weather')
df['Timezone'] = pd.to_datetime(df['Timezone'])
df['month'] = df['Timezone'].dt.month
df['hour'] = df['Timezone'].dt.hour
df['day_of_week'] = df['Timezone'].dt.dayofweek
df['date'] = df['Timezone'].dt.date
df['week'] = df['Timezone'].dt.isocalendar().week.astype(int)

month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
dow_names = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']

# ═══════════════════════════════════════════════════════
# FIGURE 1: Seasonal Overview — The Big Picture
# ═══════════════════════════════════════════════════════
fig1 = plt.figure(figsize=(16, 10))
fig1.suptitle('Home Climate Overview 2025', fontsize=18, fontweight='bold', color='white', y=0.98)
gs = GridSpec(3, 2, figure=fig1, hspace=0.35, wspace=0.25)

# 1a: Temperature trend with 7-day rolling average
ax1 = fig1.add_subplot(gs[0, :])
daily_temp = df.groupby('date').agg({
    'Temperature °C (studio desk)': 'mean',
    'Temperature °C (kitchen island)': 'mean',
    'Temperature °C (upstairs)': 'mean',
}).reset_index()
daily_temp['date'] = pd.to_datetime(daily_temp['date'])
rolling = daily_temp.set_index('date').rolling(7).mean()

ax1.plot(rolling.index, rolling['Temperature °C (studio desk)'], color='#58a6ff', linewidth=1.5, label='Studio', alpha=0.9)
ax1.plot(rolling.index, rolling['Temperature °C (kitchen island)'], color='#f97583', linewidth=1.5, label='Kitchen', alpha=0.9)
ax1.plot(rolling.index, rolling['Temperature °C (upstairs)'], color='#56d364', linewidth=1.5, label='Upstairs', alpha=0.9)
ax1.fill_between(rolling.index, rolling['Temperature °C (studio desk)'], rolling['Temperature °C (upstairs)'], alpha=0.08, color='#58a6ff')
ax1.set_ylabel('Temperature (°C)')
ax1.set_title('Temperature — 7-Day Rolling Average', fontsize=12, color='#c9d1d9', pad=10)
ax1.legend(loc='upper right', framealpha=0.3, edgecolor='#30363d')
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax1.xaxis.set_major_locator(mdates.MonthLocator())
ax1.grid(True, alpha=0.3)

# Annotate seasons
for m, label in [(3, 'Spring'), (6, 'Summer'), (9, 'Autumn'), (12, 'Winter')]:
    ax1.axvline(pd.Timestamp(f'2025-{m:02d}-01'), color='#484f58', linestyle='--', alpha=0.5, linewidth=0.8)

# 1b: Monthly temperature boxplot
ax2 = fig1.add_subplot(gs[1, 0])
studio_monthly = [df[df['month']==m]['Temperature °C (studio desk)'].dropna() for m in range(1,13)]
bp = ax2.boxplot(studio_monthly, patch_artist=True, widths=0.6, showfliers=False)
colors_temp = plt.cm.RdYlBu_r(np.linspace(0.15, 0.85, 12))
for patch, color in zip(bp['boxes'], colors_temp):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax2.set_xticklabels(month_names, fontsize=8)
ax2.set_ylabel('Temperature (°C)')
ax2.set_title('Studio Temperature Distribution by Month', fontsize=11, color='#c9d1d9', pad=8)
ax2.grid(True, axis='y', alpha=0.3)

# 1c: Humidity trend
ax3 = fig1.add_subplot(gs[1, 1])
daily_hum = df.groupby('date').agg({
    'Humidity % (studio desk)': 'mean',
    'Humidity % (kitchen island)': 'mean',
    'Humidity % (upstairs)': 'mean',
}).reset_index()
daily_hum['date'] = pd.to_datetime(daily_hum['date'])
hum_roll = daily_hum.set_index('date').rolling(7).mean()
ax3.plot(hum_roll.index, hum_roll['Humidity % (studio desk)'], color='#58a6ff', linewidth=1.5, label='Studio')
ax3.plot(hum_roll.index, hum_roll['Humidity % (kitchen island)'], color='#f97583', linewidth=1.5, label='Kitchen')
ax3.plot(hum_roll.index, hum_roll['Humidity % (upstairs)'], color='#56d364', linewidth=1.5, label='Upstairs')
ax3.axhline(y=60, color='#d29922', linestyle='--', alpha=0.6, linewidth=1, label='Comfort zone (40-60%)')
ax3.axhline(y=40, color='#d29922', linestyle='--', alpha=0.6, linewidth=1)
ax3.fill_between(hum_roll.index, 40, 60, alpha=0.06, color='#d29922')
ax3.set_ylabel('Humidity (%)')
ax3.set_title('Humidity — 7-Day Rolling Average', fontsize=11, color='#c9d1d9', pad=8)
ax3.legend(loc='upper right', framealpha=0.3, edgecolor='#30363d', fontsize=8)
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax3.xaxis.set_major_locator(mdates.MonthLocator())
ax3.grid(True, alpha=0.3)

# 1d: Pressure trend with weather interpretation
ax4 = fig1.add_subplot(gs[2, 0])
daily_press = df.groupby('date')['Pressure Pa (studio desk)'].mean().reset_index()
daily_press['date'] = pd.to_datetime(daily_press['date'])
press_roll = daily_press.set_index('date').rolling(7).mean()
ax4.plot(press_roll.index, press_roll['Pressure Pa (studio desk)'], color='#d2a8ff', linewidth=1.5)
ax4.axhline(y=1013.25, color='#8b949e', linestyle=':', alpha=0.5, label='Standard atmosphere')
ax4.set_ylabel('Pressure (hPa)')
ax4.set_title('Barometric Pressure — 7-Day Rolling Average', fontsize=11, color='#c9d1d9', pad=8)
ax4.legend(loc='upper right', framealpha=0.3, edgecolor='#30363d', fontsize=8)
ax4.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax4.xaxis.set_major_locator(mdates.MonthLocator())
ax4.grid(True, alpha=0.3)

# 1e: Kitchen-Studio temperature differential
ax5 = fig1.add_subplot(gs[2, 1])
df['kitchen_studio_diff'] = df['Temperature °C (kitchen island)'] - df['Temperature °C (studio desk)']
daily_diff = df.groupby('date')['kitchen_studio_diff'].mean().reset_index()
daily_diff['date'] = pd.to_datetime(daily_diff['date'])
diff_roll = daily_diff.set_index('date').rolling(7).mean()
ax5.plot(diff_roll.index, diff_roll['kitchen_studio_diff'], color='#f0883e', linewidth=1.5)
ax5.axhline(y=0, color='#8b949e', linestyle='-', alpha=0.4)
ax5.fill_between(diff_roll.index, diff_roll['kitchen_studio_diff'], 0,
                  where=diff_roll['kitchen_studio_diff'] > 0, alpha=0.15, color='#f97583', label='Kitchen warmer')
ax5.fill_between(diff_roll.index, diff_roll['kitchen_studio_diff'], 0,
                  where=diff_roll['kitchen_studio_diff'] < 0, alpha=0.15, color='#58a6ff', label='Studio warmer')
ax5.set_ylabel('Δ Temperature (°C)')
ax5.set_title('Kitchen − Studio Temperature Differential', fontsize=11, color='#c9d1d9', pad=8)
ax5.legend(loc='upper right', framealpha=0.3, edgecolor='#30363d', fontsize=8)
ax5.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax5.xaxis.set_major_locator(mdates.MonthLocator())
ax5.grid(True, alpha=0.3)

fig1.savefig('01_seasonal_overview.png', bbox_inches='tight', facecolor='#0d1117')
plt.close()
print('Saved: 01_seasonal_overview.png')


# ═══════════════════════════════════════════════════════
# FIGURE 2: Daily Rhythm — The 24-Hour Pulse
# ═══════════════════════════════════════════════════════
fig2 = plt.figure(figsize=(16, 8))
fig2.suptitle('Daily Rhythm — How Your Home Breathes', fontsize=18, fontweight='bold', color='white', y=0.98)
gs2 = GridSpec(2, 3, figure=fig2, hspace=0.35, wspace=0.3)

# 2a: Hourly temperature profiles by season
ax = fig2.add_subplot(gs2[0, 0])
seasons = {1: ('Winter', '#58a6ff'), 4: ('Spring', '#56d364'), 7: ('Summer', '#f97583'), 10: ('Autumn', '#d29922')}
for m, (name, color) in seasons.items():
    seasonal = df[(df['month'] >= m) & (df['month'] <= m+2)]
    hourly_avg = seasonal.groupby('hour')['Temperature °C (studio desk)'].mean()
    ax.plot(hourly_avg.index, hourly_avg.values, color=color, linewidth=2, label=name, marker='o', markersize=3)
ax.set_xlabel('Hour of Day')
ax.set_ylabel('Temperature (°C)')
ax.set_title('Temperature by Hour & Season', fontsize=11, color='#c9d1d9', pad=8)
ax.legend(framealpha=0.3, edgecolor='#30363d', fontsize=8)
ax.set_xticks(range(0, 24, 4))
ax.grid(True, alpha=0.3)

# 2b: Hourly CO2 profiles
ax = fig2.add_subplot(gs2[0, 1])
for m, (name, color) in seasons.items():
    seasonal = df[(df['month'] >= m) & (df['month'] <= m+2)]
    hourly_avg = seasonal.groupby('hour')['CO2 ppm (studio desk)'].mean()
    ax.plot(hourly_avg.index, hourly_avg.values, color=color, linewidth=2, label=name, marker='o', markersize=3)
ax.axhline(y=1000, color='#f85149', linestyle='--', alpha=0.5, label='Poor air quality')
ax.set_xlabel('Hour of Day')
ax.set_ylabel('CO2 (ppm)')
ax.set_title('CO2 by Hour & Season', fontsize=11, color='#c9d1d9', pad=8)
ax.legend(framealpha=0.3, edgecolor='#30363d', fontsize=8)
ax.set_xticks(range(0, 24, 4))
ax.grid(True, alpha=0.3)

# 2c: Hourly noise profiles
ax = fig2.add_subplot(gs2[0, 2])
for m, (name, color) in seasons.items():
    seasonal = df[(df['month'] >= m) & (df['month'] <= m+2)]
    hourly_avg = seasonal.groupby('hour')['Noise dB (studio desk)'].mean()
    ax.plot(hourly_avg.index, hourly_avg.values, color=color, linewidth=2, label=name, marker='o', markersize=3)
ax.set_xlabel('Hour of Day')
ax.set_ylabel('Noise (dB)')
ax.set_title('Noise by Hour & Season', fontsize=11, color='#c9d1d9', pad=8)
ax.legend(framealpha=0.3, edgecolor='#30363d', fontsize=8)
ax.set_xticks(range(0, 24, 4))
ax.grid(True, alpha=0.3)

# 2d: Weekday vs Weekend heatmap-style — CO2
ax = fig2.add_subplot(gs2[1, 0])
weekday_co2 = df[df['day_of_week'] < 5].groupby('hour')['CO2 ppm (studio desk)'].mean()
weekend_co2 = df[df['day_of_week'] >= 5].groupby('hour')['CO2 ppm (studio desk)'].mean()
ax.plot(weekday_co2.index, weekday_co2.values, color='#58a6ff', linewidth=2, label='Weekday', marker='o', markersize=3)
ax.plot(weekend_co2.index, weekend_co2.values, color='#f97583', linewidth=2, label='Weekend', marker='o', markersize=3)
ax.fill_between(weekday_co2.index, weekday_co2.values, weekend_co2.values, alpha=0.1, color='#d29922')
ax.set_xlabel('Hour of Day')
ax.set_ylabel('CO2 (ppm)')
ax.set_title('CO2: Weekday vs Weekend', fontsize=11, color='#c9d1d9', pad=8)
ax.legend(framealpha=0.3, edgecolor='#30363d', fontsize=8)
ax.set_xticks(range(0, 24, 4))
ax.grid(True, alpha=0.3)

# 2e: Weekday vs Weekend — Noise
ax = fig2.add_subplot(gs2[1, 1])
weekday_noise = df[df['day_of_week'] < 5].groupby('hour')['Noise dB (studio desk)'].mean()
weekend_noise = df[df['day_of_week'] >= 5].groupby('hour')['Noise dB (studio desk)'].mean()
ax.plot(weekday_noise.index, weekday_noise.values, color='#58a6ff', linewidth=2, label='Weekday', marker='o', markersize=3)
ax.plot(weekend_noise.index, weekend_noise.values, color='#f97583', linewidth=2, label='Weekend', marker='o', markersize=3)
ax.fill_between(weekday_noise.index, weekday_noise.values, weekend_noise.values, alpha=0.1, color='#d29922')
ax.set_xlabel('Hour of Day')
ax.set_ylabel('Noise (dB)')
ax.set_title('Noise: Weekday vs Weekend', fontsize=11, color='#c9d1d9', pad=8)
ax.legend(framealpha=0.3, edgecolor='#30363d', fontsize=8)
ax.set_xticks(range(0, 24, 4))
ax.grid(True, alpha=0.3)

# 2f: Room temperature difference by hour
ax = fig2.add_subplot(gs2[1, 2])
df['kit_stu_diff'] = df['Temperature °C (kitchen island)'] - df['Temperature °C (studio desk)']
df['up_stu_diff'] = df['Temperature °C (upstairs)'] - df['Temperature °C (studio desk)']
hourly_diff_kit = df.groupby('hour')['kit_stu_diff'].mean()
hourly_diff_up = df.groupby('hour')['up_stu_diff'].mean()
ax.plot(hourly_diff_kit.index, hourly_diff_kit.values, color='#f97583', linewidth=2, label='Kitchen − Studio', marker='o', markersize=3)
ax.plot(hourly_diff_up.index, hourly_diff_up.values, color='#56d364', linewidth=2, label='Upstairs − Studio', marker='o', markersize=3)
ax.axhline(y=0, color='#8b949e', linestyle='-', alpha=0.4)
ax.set_xlabel('Hour of Day')
ax.set_ylabel('Δ Temperature (°C)')
ax.set_title('Room Temperature Differentials by Hour', fontsize=11, color='#c9d1d9', pad=8)
ax.legend(framealpha=0.3, edgecolor='#30363d', fontsize=8)
ax.set_xticks(range(0, 24, 4))
ax.grid(True, alpha=0.3)

fig2.savefig('02_daily_rhythm.png', bbox_inches='tight', facecolor='#0d1117')
plt.close()
print('Saved: 02_daily_rhythm.png')


# ═══════════════════════════════════════════════════════
# FIGURE 3: Air Quality Deep Dive
# ═══════════════════════════════════════════════════════
fig3 = plt.figure(figsize=(16, 8))
fig3.suptitle('Air Quality & Ventilation Insights', fontsize=18, fontweight='bold', color='white', y=0.98)
gs3 = GridSpec(3, 3, figure=fig3, hspace=0.45, wspace=0.3)

# 3a: CO2 heatmap — month x hour
ax = fig3.add_subplot(gs3[0:2, 0:2])
co2_pivot = df.groupby(['month', 'hour'])['CO2 ppm (studio desk)'].mean().unstack()
im = ax.imshow(co2_pivot.values, aspect='auto', cmap='YlOrRd', vmin=450, vmax=600)
ax.set_yticks(range(12))
ax.set_yticklabels(month_names)
ax.set_xticks(range(0, 24, 2))
ax.set_xticklabels([f'{h:02d}' for h in range(0, 24, 2)])
ax.set_xlabel('Hour of Day')
ax.set_title('CO2 Heatmap — Studio (Month × Hour)', fontsize=11, color='#c9d1d9', pad=8)
plt.colorbar(im, ax=ax, label='CO2 (ppm)', shrink=0.8)

# 3b: CO2 exceedance events
ax = fig3.add_subplot(gs3[2, 0:2])
high_co2 = df[df['CO2 ppm (studio desk)'] > 800].copy()
high_co2['date_only'] = pd.to_datetime(high_co2['date'])
daily_exceed = high_co2.groupby('date_only').size()
ax.bar(daily_exceed.index, daily_exceed.values, color='#f85149', alpha=0.6, width=1)
ax.axhline(y=daily_exceed.mean(), color='#d29922', linestyle='--', alpha=0.7, label=f'Avg: {daily_exceed.mean():.1f} readings/day')
ax.set_ylabel('Readings > 800ppm')
ax.set_title('Daily CO2 Exceedance Events (>800ppm)', fontsize=11, color='#c9d1d9', pad=8)
ax.legend(framealpha=0.3, edgecolor='#30363d', fontsize=8)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.grid(True, alpha=0.3)

# 3c: CO2 vs Temperature scatter
ax = fig3.add_subplot(gs3[0:2, 2])
sample = df.dropna(subset=['CO2 ppm (studio desk)', 'Temperature °C (studio desk)']).sample(2000, random_state=42)
scatter = ax.scatter(sample['Temperature °C (studio desk)'], sample['CO2 ppm (studio desk)'],
                     c=sample['hour'], cmap='twilight', alpha=0.4, s=10, edgecolors='none')
plt.colorbar(scatter, ax=ax, label='Hour of Day', shrink=0.8)
ax.set_xlabel('Temperature (°C)')
ax.set_ylabel('CO2 (ppm)')
ax.set_title('CO2 vs Temperature (coloured by hour)', fontsize=11, color='#c9d1d9', pad=8)
ax.grid(True, alpha=0.3)

fig3.savefig('03_air_quality.png', bbox_inches='tight', facecolor='#0d1117')
plt.close()
print('Saved: 03_air_quality.png')


# ═══════════════════════════════════════════════════════
# FIGURE 4: Actionable Insights Dashboard
# ═══════════════════════════════════════════════════════
fig4 = plt.figure(figsize=(16, 8))
fig4.suptitle('Actionable Insights — What the Data Tells You', fontsize=18, fontweight='bold', color='white', y=0.98)
gs4 = GridSpec(2, 3, figure=fig4, hspace=0.4, wspace=0.3)

# 4a: Best/worst ventilation hours
ax = fig4.add_subplot(gs4[0, 0])
hourly_co2 = df.groupby('hour')['CO2 ppm (studio desk)'].mean()
colors_bar = ['#56d364' if v < 490 else '#d29922' if v < 510 else '#f85149' for v in hourly_co2.values]
ax.bar(hourly_co2.index, hourly_co2.values, color=colors_bar, alpha=0.8)
ax.set_xlabel('Hour of Day')
ax.set_ylabel('Avg CO2 (ppm)')
ax.set_title('CO2 by Hour — Green = Best to Ventilate', fontsize=11, color='#c9d1d9', pad=8)
ax.set_xticks(range(0, 24, 4))
ax.grid(True, axis='y', alpha=0.3)

# 4b: Heating efficiency — kitchen vs studio by month
ax = fig4.add_subplot(gs4[0, 1])
monthly_kit_stu = df.groupby('month')['kitchen_studio_diff'].mean()
colors_eff = ['#58a6ff' if v < 0 else '#f97583' for v in monthly_kit_stu.values]
ax.bar(range(12), monthly_kit_stu.values, color=colors_eff, alpha=0.8)
ax.set_xticks(range(12))
ax.set_xticklabels(month_names, fontsize=8)
ax.axhline(y=0, color='#8b949e', linestyle='-', alpha=0.4)
ax.set_ylabel('Δ Temperature (°C)')
ax.set_title('Kitchen vs Studio — Seasonal Shift', fontsize=11, color='#c9d1d9', pad=8)
ax.grid(True, axis='y', alpha=0.3)

# 4c: Humidity risk zones
ax = fig4.add_subplot(gs4[0, 2])
monthly_hum = df.groupby('month')['Humidity % (studio desk)'].mean()
colors_hum = ['#f85149' if v > 70 else '#d29922' if v > 60 else '#56d364' for v in monthly_hum.values]
ax.bar(range(12), monthly_hum.values, color=colors_hum, alpha=0.8)
ax.axhspan(40, 60, alpha=0.08, color='#56d364')
ax.axhline(y=60, color='#d29922', linestyle='--', alpha=0.5, linewidth=1)
ax.axhline(y=70, color='#f85149', linestyle='--', alpha=0.5, linewidth=1)
ax.set_xticks(range(12))
ax.set_xticklabels(month_names, fontsize=8)
ax.set_ylabel('Avg Humidity (%)')
ax.set_title('Monthly Humidity — Mould Risk Zone', fontsize=11, color='#c9d1d9', pad=8)
ax.grid(True, axis='y', alpha=0.3)

# 4d: Weekly activity pattern (noise)
ax = fig4.add_subplot(gs4[1, 0])
weekly_noise = df.groupby('day_of_week')['Noise dB (studio desk)'].mean()
ax.bar(range(7), weekly_noise.values, color='#d2a8ff', alpha=0.8)
ax.set_xticks(range(7))
ax.set_xticklabels(dow_names)
ax.set_ylabel('Avg Noise (dB)')
ax.set_title('Noise by Day of Week — Activity Pattern', fontsize=11, color='#c9d1d9', pad=8)
ax.grid(True, axis='y', alpha=0.3)

# 4e: Temperature stability (std dev by month)
ax = fig4.add_subplot(gs4[1, 1])
monthly_std = df.groupby('month')['Temperature °C (studio desk)'].std()
ax.plot(range(12), monthly_std.values, color='#58a6ff', linewidth=2, marker='o', markersize=6)
ax.fill_between(range(12), monthly_std.values, alpha=0.15, color='#58a6ff')
ax.set_xticks(range(12))
ax.set_xticklabels(month_names, fontsize=8)
ax.set_ylabel('Std Dev (°C)')
ax.set_title('Temperature Stability — Lower = More Consistent', fontsize=11, color='#c9d1d9', pad=8)
ax.grid(True, alpha=0.3)

# 4f: Key stats summary
ax = fig4.add_subplot(gs4[1, 2])
ax.axis('off')
stats_text = (
    f"KEY METRICS (Studio)\n"
    f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    f"Avg Temperature:    {df['Temperature °C (studio desk)'].mean():.1f}°C\n"
    f"Temp Range:         {df['Temperature °C (studio desk)'].min():.1f} – {df['Temperature °C (studio desk)'].max():.1f}°C\n"
    f"Avg Humidity:       {df['Humidity % (studio desk)'].mean():.0f}%\n"
    f"Avg CO2:            {df['CO2 ppm (studio desk)'].mean():.0f} ppm\n"
    f"CO2 > 800ppm days:  {len(df[df['CO2 ppm (studio desk)'] > 800].groupby('date'))}\n"
    f"Avg Noise:          {df['Noise dB (studio desk)'].mean():.1f} dB\n"
    f"Peak Noise Hour:    {df.groupby('hour')['Noise dB (studio desk)'].mean().idxmax()}:00\n"
    f"Lowest CO2 Hour:    {df.groupby('hour')['CO2 ppm (studio desk)'].mean().idxmin()}:00\n"
)
ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', fontfamily='monospace', color='#c9d1d9',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#21262d', edgecolor='#30363d'))

fig4.savefig('04_actionable_insights.png', bbox_inches='tight', facecolor='#0d1117')
plt.close()
print('Saved: 04_actionable_insights.png')

print('\nDone — 4 visualisations saved.')
