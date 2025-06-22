import requests
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from matplotlib.lines import Line2D
import matplotlib.font_manager as fm
import platform
from matplotlib.dates import date2num

# --- Use emoji-support font if available ---
def get_emoji_font():
    sys_platform = platform.system()
    if sys_platform == "Windows":
        return "Segoe UI Emoji"
    elif sys_platform == "Darwin":
        return "Apple Color Emoji"
    else:
        return "Noto Color Emoji"

emoji_font = fm.FontProperties(family=get_emoji_font())

# --- User Input ---
API_KEY = '8a4a72bb0bc6ff1c96d0c42cc2095ef4'  # Replace with your actual key
CITY = input("Enter city name: ")
UNITS = 'metric'

# Optional specific datetime input
user_dt_input = input("Enter date and time (YYYY-MM-DD HH:MM) to get forecast info (or leave blank): ")
user_dt = None
if user_dt_input.strip():
    try:
        user_dt = datetime.strptime(user_dt_input.strip(), "%Y-%m-%d %H:%M")
    except ValueError:
        print("Invalid date-time format! Proceeding with full forecast visualization...")

# --- Fetch Weather Data ---
url = f'https://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={API_KEY}&units={UNITS}'
response = requests.get(url)
data = response.json()

if data.get("cod") != "200":
    print("Error fetching weather data:", data.get("message", "Unknown error"))
    exit()

# --- Weather Emoji Mapping ---
def map_weather_to_emoji(description):
    desc = description.lower()
    if "clear" in desc:
        return "☀️"
    elif "few clouds" in desc:
        return "🌤️"
    elif "scattered clouds" in desc:
        return "🌤️"
    elif "broken clouds" in desc:
        return "⛅"
    elif "overcast clouds" in desc:
        return "☁️"
    elif "clouds" in desc:
        return "☁️"
    elif "rain" in desc:
        return "🌧️"
    elif "thunderstorm" in desc:
        return "⛈️"
    else:
        return "❓"

# --- Parse Data ---
dates, temps, weather_conditions, precipitations, weather_emojis = [], [], [], [], []
matched_forecast = None

for item in data['list']:
    dt = datetime.strptime(item['dt_txt'], '%Y-%m-%d %H:%M:%S')
    temp = item['main']['temp']
    main = item['weather'][0]['main']
    description = item['weather'][0]['description']
    pop = int(item.get('pop', 0) * 100)
    
    dates.append(dt)
    temps.append(temp)
    weather_conditions.append(main)
    precipitations.append(pop)
    weather_emojis.append(map_weather_to_emoji(description))

    # If user entered a specific datetime, find the closest forecast time
    if user_dt and abs((dt - user_dt).total_seconds()) < 2 * 3600:  # +/- 2 hour tolerance
        matched_forecast = {
            'datetime': dt,
            'temp': temp,
            'description': description,
            'pop': pop,
            'emoji': map_weather_to_emoji(description)
        }

# --- Display user-requested forecast if applicable ---
if matched_forecast:
    print("\n--- Forecast near your specified time ---")
    print("Date & Time :", matched_forecast['datetime'].strftime("%Y-%m-%d %H:%M"))
    print("Temperature :", f"{matched_forecast['temp']} °C")
    print("Condition   :", matched_forecast['description'], matched_forecast['emoji'])
    print("Precipitation Probability:", f"{matched_forecast['pop']}%")
else:
    if user_dt:
        print("No exact match found for your input time. Showing full 5-day forecast instead.\n")

# --- Plotting ---
sns.set(style="whitegrid")
plt.figure(figsize=(15, 7))
ax = plt.gca()

# Color mapping
color_map = {
    'Clear': 'orange',
    'Clouds': 'gray',
    'Rain': 'blue',
    'Thunderstorm': 'purple',
}

# Plot by condition
for condition in set(weather_conditions):
    x = [dates[i] for i in range(len(dates)) if weather_conditions[i] == condition]
    y = [temps[i] for i in range(len(temps)) if weather_conditions[i] == condition]
    ax.plot(x, y, marker='o', color=color_map.get(condition, 'black'), label=condition)

# Emoji Annotations
for i in range(len(dates)):
    emoji = weather_emojis[i]
    hour = dates[i].strftime('%H:%M')
    ax.annotate(f"{emoji}\n{precipitations[i]}%\n{hour}",
                (dates[i], temps[i]),
                textcoords="offset points",
                xytext=(0, 10),
                ha='center',
                fontsize=9,
                fontproperties=emoji_font)

# Highlight Days
unique_days = sorted(set(dt.date() for dt in dates))
highlight_colors = ['#fce4ec', '#e3f2fd', '#e8f5e9', '#fff3e0', '#ede7f6']
for i, day in enumerate(unique_days):
    start = datetime.combine(day, datetime.min.time())
    end = datetime.combine(day, datetime.max.time())
    ax.axvspan(date2num(start), date2num(end), color=highlight_colors[i % len(highlight_colors)], alpha=0.3)

# Legend
legend_elements = [
    Line2D([0], [0], marker='o', color='orange', label='Clear ☀️', markersize=8),
    Line2D([0], [0], marker='o', color='gray', label='Clouds ⛅/☁️/🌤️', markersize=8),
    Line2D([0], [0], marker='o', color='blue', label='Rain 🌧️', markersize=8),
    Line2D([0], [0], marker='o', color='purple', label='Thunderstorm ⛈️', markersize=8),
]
ax.legend(handles=legend_elements, title="Weather Type", prop=emoji_font)

# Final Plot Touches
plt.title(f'5-Day Temperature Forecast - {CITY}', fontsize=16, weight='bold')
plt.xlabel('Date and Time')
plt.ylabel('Temperature (°C)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.grid(True)
plt.show()

