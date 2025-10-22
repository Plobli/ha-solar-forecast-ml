"""
Sensor-Plattform für die Solar Forecast ML Integration.

Diese Datei ist verantwortlich für die Erstellung und Verwaltung aller
Sensor-Entitäten, die ihre Daten vom zentralen Koordinator beziehen.

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
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import SolarForecastCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """
    Richtet die Sensoren für die Solar Forecast ML Plattform ein.
    """
    coordinator: SolarForecastCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities_to_add = [
        DiagnosticStatusSensor(coordinator, entry),
        YesterdayDeviationSensor(coordinator, entry),
        SolarAccuracySensor(coordinator, entry),
        SolarForecastSensor(coordinator, entry, "heute"),
        SolarForecastSensor(coordinator, entry, "morgen"),
        PeakProductionHourSensor(coordinator, entry),
        ProductionTimeSensor(coordinator, entry),
        AverageYieldSensor(coordinator, entry),
        AutarkySensor(coordinator, entry),
    ]

    if coordinator.enable_hourly:
        entities_to_add.append(NextHourSensor(coordinator, entry))
        
    async_add_entities(entities_to_add)


class BaseSolarSensor(CoordinatorEntity[SolarForecastCoordinator], SensorEntity):
    """Basisklasse für alle Sensoren, um Code zu teilen."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: SolarForecastCoordinator, entry: ConfigEntry):
        """Initialisiere den Basis-Sensor."""
        super().__init__(coordinator)
        self.entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Solar Forecast ML",
            manufacturer="Zara-Toorox",
            model="v4.4.6",
        )


class SolarForecastSensor(BaseSolarSensor):
    """Sensor für die Energie-Prognosewerte (Heute/Morgen)."""

    def __init__(self, coordinator: SolarForecastCoordinator, entry: ConfigEntry, key: str):
        super().__init__(coordinator, entry)
        self._key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        clean_name = "Solar Prognose Heute" if key == "heute" else "Solar Prognose Morgen"
        self._attr_name = clean_name
        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self._attr_state_class = SensorStateClass.TOTAL
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_icon = "mdi:solar-power"

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key, 0.0) if self.coordinator.data else 0.0


class NextHourSensor(BaseSolarSensor):
    """Sensor für die Prognose der nächsten Stunde."""

    def __init__(self, coordinator: SolarForecastCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_naechste_stunde"
        self._attr_name = "Prognose Nächste Stunde"
        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:clock-fast"
        
    @property
    def native_value(self):
        return round(self.coordinator.next_hour_pred, 2)


class PeakProductionHourSensor(BaseSolarSensor):
    """Sensor für die Stunde mit der höchsten erwarteten Produktion."""

    _entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: SolarForecastCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_peak_production_hour"
        self._attr_name = "Beste Stunde für Verbraucher"
        self._attr_icon = "mdi:battery-charging-high"

    @property
    def native_value(self):
        return self.coordinator.peak_production_time_today


class ProductionTimeSensor(BaseSolarSensor):
    """Sensor für die heutige Produktionszeit."""

    _entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: SolarForecastCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_production_time"
        self._attr_name = "Produktionszeit Heute"
        self._attr_icon = "mdi:timer-sand"

    @property
    def native_value(self):
        return self.coordinator.production_time_today


class YesterdayDeviationSensor(BaseSolarSensor):
    """Sensor für die konkrete Prognoseabweichung des Vortages in kWh."""

    _entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: SolarForecastCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_yesterday_deviation"
        self._attr_name = "Prognose Abweichung Gestern"
        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:chart-bell-curve"

    @property
    def native_value(self):
        error_kwh = self.coordinator.last_day_error_kwh
        return round(error_kwh, 2) if error_kwh is not None else None


class SolarAccuracySensor(BaseSolarSensor):
    """Sensor für die prozentuale Genauigkeit des Modells."""

    _entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: SolarForecastCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_genauigkeit"
        self._attr_name = "Prognose Genauigkeit"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:target-variant"

    @property
    def native_value(self):
        return round(self.coordinator.data.get("genauigkeit", 0.0), 1) if self.coordinator.data else 0.0


class AverageYieldSensor(BaseSolarSensor):
    """Sensor für den durchschnittlichen Tagesertrag der letzten 30 Tage."""

    _entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: SolarForecastCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_average_yield"
        self._attr_name = "Durchschnittsertrag (30 Tage)"
        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:chart-line"

    @property
    def native_value(self):
        return self.coordinator.data.get("average_yield_30_days", 0.0) if self.coordinator.data else 0.0


class AutarkySensor(BaseSolarSensor):
    """Sensor für den heutigen Autarkiegrad."""

    _entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: SolarForecastCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_autarky_today"
        self._attr_name = "Autarkiegrad Heute"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:shield-sun"

    @property
    def native_value(self):
        return round(self.coordinator.autarky_today, 1) if self.coordinator.autarky_today is not None else None


class DiagnosticStatusSensor(BaseSolarSensor):
    """Sensor für den textuellen Status der Integration."""

    _entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: SolarForecastCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_status"
        self._attr_name = "Status"
        self._attr_icon = "mdi:information-outline"

    @property
    def native_value(self) -> str:
        return self.coordinator._get_status_text()
        
    @property
    def extra_state_attributes(self) -> dict:
        """Stellt zusätzliche Debug-Informationen als Attribute bereit."""
        last_learned_ts = self.coordinator.last_successful_learning
        return {
            "last_successful_learning": dt_util.as_local(last_learned_ts).isoformat() if last_learned_ts else "Noch nicht",
            # KORREKTUR: Check hinzugefügt, um Absturz bei None zu verhindern
            "last_update": dt_util.as_local(self.coordinator.last_update).isoformat() if self.coordinator.last_update else "Noch nicht",
            "base_capacity": f"{self.coordinator.base_capacity:.2f} kWh",
            "weights": self.coordinator.weights,
        }