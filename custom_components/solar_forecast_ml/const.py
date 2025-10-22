"""Konstanten für die Solar Forecast ML Integration."""

DOMAIN = "solar_forecast_ml"

# --- Konfigurationsschlüssel ---
CONF_WEATHER_ENTITY = "weather_entity"
CONF_POWER_ENTITY = "power_entity"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_PLANT_KWP = "plant_kwp"
CONF_TOTAL_CONSUMPTION_TODAY = "total_consumption_today"  # NEU für Autarkie

# Optionale Sensoren
CONF_FORECAST_SOLAR = "forecast_solar_sensor"
CONF_CURRENT_POWER = "current_power_sensor"
CONF_LUX_SENSOR = "lux_sensor"
CONF_TEMP_SENSOR = "temp_sensor"
CONF_WIND_SENSOR = "wind_sensor"
CONF_UV_SENSOR = "uv_sensor"
CONF_RAIN_SENSOR = "rain_sensor"

# --- Optionsschlüssel (Toggles) ---
CONF_DIAGNOSTIC = "enable_diagnostic"
CONF_HOURLY = "enable_hourly"
CONF_NOTIFY_FORECAST = "notify_forecast"
CONF_NOTIFY_LEARNING = "notify_learning"
CONF_NOTIFY_STARTUP = "notify_startup"
CONF_NOTIFY_SUCCESSFUL_LEARNING = "notify_successful_learning"

# --- Standardwerte ---
DEFAULT_UPDATE_INTERVAL = 3600
DEFAULT_BASE_CAPACITY = 10.0

# Notification Defaults
DEFAULT_NOTIFY_FORECAST = False
DEFAULT_NOTIFY_LEARNING = False
DEFAULT_NOTIFY_STARTUP = True
DEFAULT_NOTIFY_SUCCESSFUL_LEARNING = True

# --- Dateipfade ---
DATA_DIR = "/config/solar_forecast_ml"
WEIGHTS_FILE = f"{DATA_DIR}/learned_weights.json"
HISTORY_FILE = f"{DATA_DIR}/prediction_history.json"
HOURLY_PROFILE_FILE = f"{DATA_DIR}/hourly_profile.json"

# Alte Pfade für die Migration
OLD_DATA_DIR = "/config/custom_components/solar_forecast_ml"
OLD_WEIGHTS_FILE = f"{OLD_DATA_DIR}/learned_weights.json"
OLD_HISTORY_FILE = f"{OLD_DATA_DIR}/prediction_history.json"
OLD_HOURLY_PROFILE_FILE = f"{OLD_DATA_DIR}/hourly_profile.json"

# --- Modell-Konstanten ---
DEFAULT_WEIGHTS = {
    'base': 1.0, 
    'lux': 0.3,     # Für logarithmische Skalierung optimiert
    'temp': 0.05,
    'wind': 0.01,   # KORRIGIERT: Positiv (Wind kühlt Module = bessere Leistung)
    'uv': 0.08, 
    'fs': 0.5, 
    'rain': -0.2
}

WEATHER_FACTORS = {
    'sunny': 1.0, 'partlycloudy': 0.7, 'cloudy': 0.4,
    'rainy': 0.2, 'pouring': 0.1, 'snowy': 0.1, 'clear-night': 0.0,
    'fog': 0.3, "exceptional": 1.0, "hail": 0.1, "lightning": 0.2,
    "lightning-rainy": 0.1, "snowy-rainy": 0.1,
    "windy": 0.8, "windy-variant": 0.8,
}