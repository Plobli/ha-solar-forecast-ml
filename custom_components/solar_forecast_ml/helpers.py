"""
Hilfsfunktionen für die Solar Forecast ML Integration.

Diese Datei enthält unabhängige, wiederverwendbare Funktionen für
Dateioperationen und Berechnungen, die vom Koordinator genutzt werden.

Copyright (C) 2025 Zara-Toorox

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import logging
import os
import shutil
import datetime # <<< KORREKTER ORT FÜR DEN IMPORT

# Die Funktionen sind aufgeteilt. Wir brauchen:
# 1. load_json aus util.json
# 2. save_json aus helpers.json
# 3. HomeAssistantError aus exceptions
from homeassistant.util import json as ha_util_json
from homeassistant.helpers import json as ha_helpers_json
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DATA_DIR,
    DEFAULT_BASE_CAPACITY,
    HISTORY_FILE,
    HOURLY_PROFILE_FILE,
    OLD_HISTORY_FILE,
    OLD_HOURLY_PROFILE_FILE,
    OLD_WEIGHTS_FILE,
    WEIGHTS_FILE,
)

_LOGGER = logging.getLogger(__name__)


def _read_history_file(filepath: str) -> dict:
    """
    Blockierende Hilfsfunktion zum Lesen einer JSON-Datei.
    Verwendet ha_util_json.load_json für robustes Laden.
    Gibt ein leeres Dictionary zurück, wenn die Datei nicht existiert oder fehlerhaft ist.
    """
    try:
        return ha_util_json.load_json(filepath, default={})
    except HomeAssistantError as e:
        _LOGGER.error(f"Fehler beim Lesen der Datei {filepath} mit ha_json: {e}")
        return {}


def _write_history_file(filepath: str, data: dict):
    """
    Blockierende Hilfsfunktion zum Speichern von Daten in einer JSON-Datei.
    Verwendet ha_helpers_json.save_json für atomare Schreibvorgänge.
    Erstellt das Verzeichnis automatisch und sicher.
    """
    try:
        ha_helpers_json.save_json(filepath, data, private=True)
    except HomeAssistantError as e:
        _LOGGER.error(f"Fehler beim atomaren Speichern der Datei {filepath}: {e}")


def _migrate_data_files():
    """
    Migriert Lerndateien vom alten Speicherort (innerhalb von custom_components)
    zum neuen, sicheren Speicherort (/config/solar_forecast_ml).
    Diese Funktion wird einmalig beim Start nach einem Update ausgeführt.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    migrations = [
        (OLD_HISTORY_FILE, HISTORY_FILE),
        (OLD_WEIGHTS_FILE, WEIGHTS_FILE),
        (OLD_HOURLY_PROFILE_FILE, HOURLY_PROFILE_FILE),
    ]
    migrated_count = 0
    for old_path, new_path in migrations:
        if os.path.exists(old_path) and not os.path.exists(new_path):
            try:
                shutil.move(old_path, new_path)
                _LOGGER.info(f"✅ Migrated {os.path.basename(old_path)} to safe location.")
                migrated_count += 1
            except Exception as e:
                _LOGGER.error(f"❌ Failed to migrate {os.path.basename(old_path)}: {e}")
        elif os.path.exists(old_path):
            try:
                os.remove(old_path)
                _LOGGER.debug(f"🗑️ Removed old data file: {os.path.basename(old_path)}")
            except Exception as e:
                _LOGGER.warning(f"Could not remove old data file {os.path.basename(old_path)}: {e}")

    if migrated_count > 0:
        _LOGGER.info(f"🎉 Data migration completed! {migrated_count} files moved.")


def calculate_initial_base_capacity(plant_kwp: float) -> float:
    """
    Intelligente Startwert-Berechnung der Basiskapazität basierend auf der Anlagenleistung (kWp).
    Optimiert mit saisonalen Faktoren basierend auf deutschen PV-Anlagen-Performance-Daten.
    """
    if not isinstance(plant_kwp, (int, float)) or plant_kwp <= 0:
        return DEFAULT_BASE_CAPACITY

    now = datetime.datetime.now()
    month = now.month

    # Saisonale kWh pro kWp basierend auf deutschen PV-Anlagen-Durchschnittswerten
    if month in [12, 1, 2]:  # Winter
        daily_kwh_per_kwp = 2.0
    elif month in [3, 4, 5]:  # Frühling
        daily_kwh_per_kwp = 4.0
    elif month in [6, 7, 8]:  # Sommer
        daily_kwh_per_kwp = 6.4
    else:  # Herbst (9,10,11)
        daily_kwh_per_kwp = 4.0

    base_capacity = plant_kwp * daily_kwh_per_kwp

    # Begrenzung auf realistischen Bereich pro Saison
    min_capacity = plant_kwp * 1.5
    max_capacity = plant_kwp * 8.0
    clamped_capacity = max(min_capacity, min(max_capacity, base_capacity))

    season_names = {12: "Winter", 1: "Winter", 2: "Winter",
                    3: "Frühling", 4: "Frühling", 5: "Frühling",
                    6: "Sommer", 7: "Sommer", 8: "Sommer",
                    9: "Herbst", 10: "Herbst", 11: "Herbst"}

    _LOGGER.info(f"🏭 Saisonale Kalibrierung ({season_names[month]}): {plant_kwp:.2f} kWp × {daily_kwh_per_kwp} kWh/kWp = {clamped_capacity:.2f} kWh Base Capacity")
    return clamped_capacity