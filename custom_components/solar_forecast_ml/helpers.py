"""
Hilfsfunktionen für die Solar Forecast ML Integration.

Diese Datei enthält unabhängige, wiederverwendbare Funktionen für
Dateioperationen und Berechnungen, die vom Koordinator genutzt werden.
"""

import json
import logging
import os
import shutil

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
    Gibt ein leeres Dictionary zurück, wenn die Datei nicht existiert oder fehlerhaft ist.
    """
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        _LOGGER.error(f"Fehler beim Lesen der Datei {filepath}: {e}")
        return {}


def _write_history_file(filepath: str, data: dict):
    """
    Blockierende Hilfsfunktion zum Speichern von Daten in einer JSON-Datei.
    Erstellt das Verzeichnis, falls es nicht existiert.
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        _LOGGER.error(f"Fehler beim Speichern der Datei {filepath}: {e}")


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
                # move statt copy, um die alte Datei direkt zu verschieben
                shutil.move(old_path, new_path)
                _LOGGER.info(f"✅ Migrated {os.path.basename(old_path)} to safe location.")
                migrated_count += 1
            except Exception as e:
                _LOGGER.error(f"❌ Failed to migrate {os.path.basename(old_path)}: {e}")
        elif os.path.exists(old_path):
            # Wenn die neue Datei schon existiert, die alte einfach löschen
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
        
    import datetime
    now = datetime.datetime.now()
    month = now.month
    
    # Saisonale kWh pro kWp basierend auf deutschen PV-Anlagen-Durchschnittswerten
    # Berechnet aus realen Anlagen-Performance-Daten (normalisiert pro kWp)
    if month in [12, 1, 2]:  # Winter
        daily_kwh_per_kwp = 2.0  # Niedrige Sonnenstunden, flacher Winkel
    elif month in [3, 4, 5]:  # Frühling
        daily_kwh_per_kwp = 4.0  # Steigende Sonnenstunden, guter Winkel
    elif month in [6, 7, 8]:  # Sommer
        daily_kwh_per_kwp = 6.4  # Maximale Sonnenstunden, optimaler Winkel
    else:  # Herbst (9,10,11)
        daily_kwh_per_kwp = 4.0  # Sinkende Sonnenstunden, noch guter Winkel
    
    # Berechnung für die tatsächliche Anlagengröße des Nutzers
    base_capacity = plant_kwp * daily_kwh_per_kwp
    
    # Begrenzung auf realistischen Bereich pro Saison
    min_capacity = plant_kwp * 1.5  # Sehr schlechte Tage (Nebel, Sturm)
    max_capacity = plant_kwp * 8.0  # Absolute Spitzentage (klarer Himmel, Sommer)
    clamped_capacity = max(min_capacity, min(max_capacity, base_capacity))
    
    season_names = {12: "Winter", 1: "Winter", 2: "Winter", 
                   3: "Frühling", 4: "Frühling", 5: "Frühling",
                   6: "Sommer", 7: "Sommer", 8: "Sommer",
                   9: "Herbst", 10: "Herbst", 11: "Herbst"}
    
    _LOGGER.info(f"🏭 Saisonale Kalibrierung ({season_names[month]}): {plant_kwp:.2f} kWp × {daily_kwh_per_kwp} kWh/kWp = {clamped_capacity:.2f} kWh Base Capacity")
    return clamped_capacity

