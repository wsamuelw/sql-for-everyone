import pandas as pd
import numpy as np
import json

df = pd.read_excel('Netatmo 2025.xlsx', sheet_name='Weather')
df['Timezone'] = pd.to_datetime(df['Timezone'])
df['month'] = df['Timezone'].dt.month
df['hour'] = df['Timezone'].dt.hour
df['dayOfWeek'] = df['Timezone'].dt.dayofweek
df['date'] = df['Timezone'].dt.date

month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

# ── Daily time series (7-day rolling, ~365 points) ──
daily = df.groupby('date').agg({
    'Temperature °C (studio desk)': 'mean',
    'Temperature °C (kitchen island)': 'mean',
    'Temperature °C (upstairs)': 'mean',
    'Humidity % (studio desk)': 'mean',
    'Humidity % (kitchen island)': 'mean',
    'Humidity % (upstairs)': 'mean',
    'CO2 ppm (studio desk)': 'mean',
    'Noise dB (studio desk)': 'mean',
    'Pressure Pa (studio desk)': 'mean',
}).reset_index()
daily['date'] = pd.to_datetime(daily['date'])
rolling = daily.set_index('date').rolling(7, min_periods=1).mean().reset_index()
rolling['date'] = rolling['date'].dt.strftime('%Y-%m-%d')

daily_timeseries = {
    'dates': rolling['date'].tolist(),
    'studio_temp': [round(v, 2) for v in rolling['Temperature °C (studio desk)'].tolist()],
    'kitchen_temp': [round(v, 2) for v in rolling['Temperature °C (kitchen island)'].tolist()],
    'upstairs_temp': [round(v, 2) for v in rolling['Temperature °C (upstairs)'].tolist()],
    'studio_humidity': [round(v, 1) for v in rolling['Humidity % (studio desk)'].tolist()],
    'kitchen_humidity': [round(v, 1) for v in rolling['Humidity % (kitchen island)'].tolist()],
    'upstairs_humidity': [round(v, 1) for v in rolling['Humidity % (upstairs)'].tolist()],
    'studio_co2': [round(v, 1) for v in rolling['CO2 ppm (studio desk)'].tolist()],
    'studio_noise': [round(v, 1) for v in rolling['Noise dB (studio desk)'].tolist()],
    'studio_pressure': [round(v, 1) for v in rolling['Pressure Pa (studio desk)'].tolist()],
}

# ── Hourly by season ──
season_map = {1:'Summer',2:'Summer',3:'Autumn',4:'Autumn',5:'Autumn',
              6:'Winter',7:'Winter',8:'Winter',9:'Spring',10:'Spring',11:'Spring',12:'Summer'}
df['season'] = df['month'].map(season_map)

hourly_season = df.groupby(['season', 'hour']).agg({
    'Temperature °C (studio desk)': 'mean',
    'Temperature °C (kitchen island)': 'mean',
    'Temperature °C (upstairs)': 'mean',
    'CO2 ppm (studio desk)': 'mean',
    'Noise dB (studio desk)': 'mean',
    'Humidity % (studio desk)': 'mean',
}).reset_index()

hourly_by_season = {}
for season in ['Summer', 'Autumn', 'Winter', 'Spring']:
    s = hourly_season[hourly_season['season'] == season]
    hourly_by_season[season] = {
        'hours': s['hour'].tolist(),
        'studio_temp': [round(v, 2) for v in s['Temperature °C (studio desk)'].tolist()],
        'kitchen_temp': [round(v, 2) for v in s['Temperature °C (kitchen island)'].tolist()],
        'upstairs_temp': [round(v, 2) for v in s['Temperature °C (upstairs)'].tolist()],
        'studio_co2': [round(v, 1) for v in s['CO2 ppm (studio desk)'].tolist()],
        'studio_noise': [round(v, 1) for v in s['Noise dB (studio desk)'].tolist()],
        'studio_humidity': [round(v, 1) for v in s['Humidity % (studio desk)'].tolist()],
    }

# ── Weekday vs weekend hourly ──
for label, mask in [('weekday', df['dayOfWeek'] < 5), ('weekend', df['dayOfWeek'] >= 5)]:
    subset = df[mask].groupby('hour').agg({
        'Temperature °C (studio desk)': 'mean',
        'CO2 ppm (studio desk)': 'mean',
        'Noise dB (studio desk)': 'mean',
    }).reset_index()
    key = label
    hourly_by_season[key] = {
        'hours': subset['hour'].tolist(),
        'studio_temp': [round(v, 2) for v in subset['Temperature °C (studio desk)'].tolist()],
        'studio_co2': [round(v, 1) for v in subset['CO2 ppm (studio desk)'].tolist()],
        'studio_noise': [round(v, 1) for v in subset['Noise dB (studio desk)'].tolist()],
    }

# ── CO2 heatmap (month × hour) ──
co2_matrix = df.groupby(['month', 'hour'])['CO2 ppm (studio desk)'].mean().unstack()
co2_heatmap = {
    'months': month_names,
    'hours': list(range(24)),
    'values': [[round(v, 1) for v in row] for row in co2_matrix.values.tolist()],
}

# ── Monthly stats ──
monthly = df.groupby('month').agg({
    'Temperature °C (studio desk)': ['mean', 'min', 'max', 'std'],
    'Temperature °C (kitchen island)': 'mean',
    'Humidity % (studio desk)': 'mean',
    'CO2 ppm (studio desk)': 'mean',
    'Noise dB (studio desk)': 'mean',
    'Pressure Pa (studio desk)': 'mean',
}).reset_index()

monthly_stats = {
    'months': month_names,
    'temp_mean': [round(v, 2) for v in monthly[('Temperature °C (studio desk)', 'mean')].tolist()],
    'temp_min': [round(v, 2) for v in monthly[('Temperature °C (studio desk)', 'min')].tolist()],
    'temp_max': [round(v, 2) for v in monthly[('Temperature °C (studio desk)', 'max')].tolist()],
    'temp_std': [round(v, 2) for v in monthly[('Temperature °C (studio desk)', 'std')].fillna(0).tolist()],
    'kitchen_temp': [round(v, 2) for v in monthly[('Temperature °C (kitchen island)', 'mean')].tolist()],
    'humidity': [round(v, 1) for v in monthly[('Humidity % (studio desk)', 'mean')].tolist()],
    'co2': [round(v, 1) for v in monthly[('CO2 ppm (studio desk)', 'mean')].tolist()],
    'noise': [round(v, 1) for v in monthly[('Noise dB (studio desk)', 'mean')].tolist()],
    'pressure': [round(v, 1) for v in monthly[('Pressure Pa (studio desk)', 'mean')].tolist()],
}

# ── Room differentials ──
df['kitchenStudioDiff'] = df['Temperature °C (kitchen island)'] - df['Temperature °C (studio desk)']
df['upstairsStudioDiff'] = df['Temperature °C (upstairs)'] - df['Temperature °C (studio desk)']

daily_diff = df.groupby('date').agg({
    'kitchenStudioDiff': 'mean',
    'upstairsStudioDiff': 'mean',
}).reset_index()
daily_diff['date'] = pd.to_datetime(daily_diff['date'])
diff_roll = daily_diff.set_index('date').rolling(7, min_periods=1).mean().reset_index()
diff_roll['date'] = diff_roll['date'].dt.strftime('%Y-%m-%d')

room_diff = {
    'dates': diff_roll['date'].tolist(),
    'kitchen_studio': [round(v, 3) for v in diff_roll['kitchenStudioDiff'].tolist()],
    'upstairs_studio': [round(v, 3) for v in diff_roll['upstairsStudioDiff'].tolist()],
}

# ── Ventilation hours (CO2 by hour) ──
hourly_co2 = df.groupby('hour')['CO2 ppm (studio desk)'].mean()
ventilation = {
    'hours': list(range(24)),
    'co2': [round(v, 1) for v in hourly_co2.values.tolist()],
}

# ── Key metrics ──
metrics = {
    'avg_temp': round(df['Temperature °C (studio desk)'].mean(), 1),
    'temp_min': round(df['Temperature °C (studio desk)'].min(), 1),
    'temp_max': round(df['Temperature °C (studio desk)'].max(), 1),
    'avg_humidity': round(df['Humidity % (studio desk)'].mean(), 0),
    'avg_co2': round(df['CO2 ppm (studio desk)'].mean(), 0),
    'co2_high_days': int(len(df[df['CO2 ppm (studio desk)'] > 800].groupby('date'))),
    'avg_noise': round(df['Noise dB (studio desk)'].mean(), 1),
    'peak_noise_hour': int(df.groupby('hour')['Noise dB (studio desk)'].mean().idxmax()),
    'lowest_co2_hour': int(df.groupby('hour')['CO2 ppm (studio desk)'].mean().idxmin()),
    'avg_pressure': round(df['Pressure Pa (studio desk)'].mean(), 1),
}

# ── CO2 scatter sample ──
sample = df.dropna(subset=['CO2 ppm (studio desk)', 'Temperature °C (studio desk)']).sample(3000, random_state=42)
co2_scatter = {
    'temp': [round(v, 2) for v in sample['Temperature °C (studio desk)'].tolist()],
    'co2': [round(v, 0) for v in sample['CO2 ppm (studio desk)'].tolist()],
    'hour': [int(v) for v in sample['hour'].tolist()],
}

# ── Combine all ──
data = {
    'daily_timeseries': daily_timeseries,
    'hourly_by_season': hourly_by_season,
    'co2_heatmap': co2_heatmap,
    'monthly_stats': monthly_stats,
    'room_diff': room_diff,
    'ventilation': ventilation,
    'metrics': metrics,
    'co2_scatter': co2_scatter,
}

with open('data.json', 'w') as f:
    json.dump(data, f)

print(f'Exported data.json ({len(json.dumps(data)) // 1024}KB)')
