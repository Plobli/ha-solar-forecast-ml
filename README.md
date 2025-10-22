# 🌞 Solar Forecast ML for Home Assistant

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Version](https://img.shields.io/badge/version-v4.4.6-blue.svg)](https://github.com/Zara-Toorox/ha-solar-forecast-ml/releases)
[![License](https://img.shields.io/badge/license-AGPLv3.-green.svg)](LICENSE)

**Empower Your Solar System with Adaptive, Self-Learning Forecasts – Tailored to Your Unique Setup for Smarter Energy Management.**

Solar Forecast ML is a self-learning integration for Home Assistant that provides accurate, adaptive solar energy production forecasts. It learns from your system's unique production patterns, historical data, and weather conditions to create tailored daily and hourly yield predictions.

---

## Core Features

### Intelligent Forecasting
- **Daily Forecasts**: Predicts today's and tomorrow's total production (kWh).
- **Next-Hour Prediction** (Optional): A short-term forecast for the upcoming hour, ideal for real-time automation.
- **Peak Production Hour**: Identifies the *historically* best time window to run high-energy-consumption devices, based on your system's learned production profile.
- **Production Time Window**: Tracks today's active solar production period from the first to the last hour of generation.

### Adaptive Machine Learning
- **Daily Learning Cycle**: Automatically runs at 23:00 (11 PM) to compare the day's prediction with the actual yield. It then calculates the error and adjusts the model's `base_capacity` weight for continuous improvement.
- **Hourly Profile Learning**: Learns your plant's typical production curve (e.g., "15% of energy is produced between 1-2 PM") by analyzing up to 60 days of historical hourly data. This profile is used for the next-hour forecast.
- **Accuracy Tracking**: Provides a 30-day rolling accuracy (MAPE) sensor to monitor model performance.
- **Hybrid Blending**: Can optionally blend its own prediction with an external sensor (like Forecast.Solar) for a more robust, weighted-average forecast.

### Data Integrity & Safety
- **Persistent Storage**: Safely stores learning files (`learned_weights.json`, `prediction_history.json`, `hourly_profile.json`) in `/config/solar_forecast_ml`. This data is included in Home Assistant backups and survives integration updates.
- **Migration**: Automatically migrates old data files from the `custom_components` directory to the safe `/config` location.
- **Race Condition Protection**: Uses an `asyncio.Lock` to ensure that learning, forecasting, and data collection processes never run at the same time, preventing data corruption.

### Integration & Insights
- **Required Entities**: Needs only a `weather` entity and a daily solar yield `sensor` (kWh) to function.
- **Optional Sensors**: Enhances accuracy by using sensors for: Current Power (W), Lux, Temperature, Wind, UV, and Rain.
- **Autarky Rate**: If a total daily consumption sensor is provided, it calculates the daily self-sufficiency percentage.
- **Average Yield**: A 30-day rolling average of your *actual* production.

---

## Learning Phases

The model progresses through phases for increasing accuracy. Patience is key.

Phase 1: Calibration (Days 1-7) Phase 2: Learning (Days 8-30) Phase 3: Optimized (Day 31+) [████░░░░░░░░░░░░░░░░] ~50-70% [████████████░░░░░░░░] ~70-85% [████████████████████] ~85-95% • Baseline from kWp • Daily weight adjustments • Full pattern recognition • Initial data collection • Hourly profile learning • Seasonal trend handling • Weather correlation setup • System-specific tuning • High reliability


---

## Installation

### Via HACS (Recommended)
1.  Go to HACS > Integrations > Click the 3-dot menu > **Custom repositories**.
2.  Add the repository URL: `https://github.com/Zara-Toorox/ha-solar-forecast-ml` (Category: Integration).
3.  Search for "Solar Forecast ML" and install it.
4.  Restart Home Assistant.

### Manual Installation
1.  Download the [latest release](https://github.com/Zara-Toorox/ha-solar-forecast-ml/releases).
2.  Copy the `custom_components/solar_forecast_ml` directory into your `/config/custom_components/` directory.
3.  Restart Home Assistant.

---

## Configuration

Add the integration via **Settings > Devices & Services > + Add Integration > "Solar Forecast ML"**.

### Required Fields
| Field | Description | Example |
|---|---|---|
| Weather Entity | Your primary weather provider. | `weather.openweathermap` |
| Power Entity | Daily solar yield sensor (in kWh) that resets to 0 at midnight. | `sensor.solar_daily_kwh` |

### Optional Fields
| Field | Description | Example |
|---|---|---|
| Total Consumption | Daily household consumption (kWh), for autarky calculation. | `sensor.daily_consumption_kwh` |
| Plant kWp | Your plant's peak power (e.g., 5.4). Used for initial calibration. | `5.4` |
| Current Power | *Instantaneous* production (in **W**). **Required for Next-Hour forecast.** | `sensor.inverter_power_w` |
| Forecast.Solar Sensor | An existing Forecast.Solar entity (kWh) for hybrid blending. | `sensor.forecast_solar_today` |
| Lux Sensor | Environmental light sensor. | `sensor.outdoor_lux` |
| Temp/Wind/UV/Rain | Additional environmental sensors to improve the model. | `sensor.outdoor_temp` |

### Options (Advanced)
Can be configured via **Settings > Devices & Services > Solar Forecast ML > Configure**.

| Option | Default | Description |
|---|---|---|
| Update Interval | 3600s (1h) | How often to check for new forecasts. Min: 300s. |
| Enable Diagnostic | True | Enables the 'Status' sensor with debug attributes. |
| Enable Hourly | False | Enables the 'Prognose Nächste Stunde' (Next Hour) sensor. |
| Notify on Startup | True | Sends a notification when the integration starts. |
| Notify on Forecast | False | Sends a notification with the new daily forecast. |
| Notify on Learning | False | Sends a notification with the detailed learning results (debug). |
| Notify on Successful Learning | True | Sends a brief notification confirming learning was successful. |

---

## Entities

The integration creates the following sensors and buttons.
*(Note: Default entity names are in German as defined in the code; you can rename them in Home Assistant.)*

| Entity ID | Default Name (German) | Description | Icon |
|---|---|---|---|
| `sensor.solar_forecast_ml_heute` | Solar Prognose Heute | Today's total forecast. | mdi:solar-power |
| `sensor.solar_forecast_ml_morgen` | Solar Prognose Morgen | Tomorrow's total forecast. | mdi:solar-power |
| `sensor.solar_forecast_ml_naechste_stunde` | Prognose Nächste Stunde | Next hour's forecast (if enabled). | mdi:clock-fast |
| `sensor.solar_forecast_ml_peak_production_hour` | Beste Stunde für Verbraucher | The historical best hour for consumption. | mdi:battery-charging-high |
| `sensor.solar_forecast_ml_production_time` | Produktionszeit Heute | Today's production window (e.g., "08:00 - 17:00"). | mdi:timer-sand |
| `sensor.solar_forecast_ml_autarky_today` | Autarkiegrad Heute | Self-sufficiency rate (if consumption sensor is set). | mdi:shield-sun |
| `sensor.solar_forecast_ml_average_yield` | Durchschnittsertrag (30 Tage) | 30-day rolling average of *actual* yield. | mdi:chart-line |
| `sensor.solar_forecast_ml_genauigkeit` | Prognose Genauigkeit | Model accuracy (100 - 30-day MAPE). | mdi:target-variant |
| `sensor.solar_forecast_ml_yesterday_deviation` | Prognose Abweichung Gestern | Yesterday's error in kWh (Actual - Predicted). | mdi:chart-bell-curve |
| `sensor.solar_forecast_ml_status` | Status | Diagnostic status and debug attributes. | mdi:information-outline |
| `button.solar_forecast_ml_manual_forecast` | Manuelle Prognose | Manually trigger a new forecast. | mdi:refresh-circle |
| `button.solar_forecast_ml_manual_learning` | Manueller Lernprozess | Manually trigger the learning cycle. | mdi:brain |

---

## Schedule

| Time | Event | Purpose |
|---|---|---|
| 06:00 (6 AM) | Morning Forecast | Triggers the main forecast for today and tomorrow. |
| Hourly (at :00) | Data Collection | Gathers live power data (if `Current Power` sensor is set) to build the hourly profile. |
| 23:00 (11 PM) | Learning Cycle | Compares yesterday's forecast with actual yield and adjusts model weights. |

---

## Troubleshooting

-   **Forecast is 0.0:** Check that your `sun.sun` entity is enabled and your Home Assistant timezone is set correctly. The forecast will be 0 at night.
-   **Low Accuracy:** Accuracy is calculated over 30 days. Please wait at least 7-10 days for the model to gather data and self-calibrate. Ensure your "Power Entity" resets daily at midnight.
-   **No "Next Hour" Sensor:** Go to Options and ensure "Enable Hourly" is checked. You *must* also configure the "Current Power (W)" sensor for this to work.
-   **Data in `/config/solar_forecast_ml`**: This is intentional. Storing data here ensures your learned model persists across updates and is included in HA backups.

---

## Contributing & Support

-   Found a bug? Please open an [Issue](https://github.com/Zara-Toorox/ha-solar-forecast-ml/issues).
-   Have a question? Join the [discussion](https://github.com/Zara-Toorox/ha-solar-forecast-ml/discussions).
-   Contributions are welcome! Please fork, create a feature branch, and submit a PR.

## License
AGPLv3.

---