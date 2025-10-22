"""
Button-Plattform für die Solar Forecast ML Integration.

Diese Datei erstellt die Entitäten für Buttons, die es dem Benutzer ermöglichen,
Aktionen wie eine manuelle Prognose oder einen Lernprozess auszulösen.

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
import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SolarForecastCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Richtet die Buttons ein."""
    coordinator: SolarForecastCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([
        ManualForecastButton(coordinator, entry),
        ManualLearningButton(coordinator, entry),
    ])
    _LOGGER.info("Buttons für manuelle Prognose und Lernen erfolgreich eingerichtet.")


class ManualForecastButton(ButtonEntity):
    """Ein Button, um die Prognose manuell auszulösen."""
    _attr_has_entity_name = True

    def __init__(self, coordinator: SolarForecastCoordinator, entry: ConfigEntry):
        """Initialisiere den Prognose-Button."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_manual_forecast"
        # KORREKTUR: Gekürzter, professioneller Name
        self._attr_name = "Manuelle Prognose"
        self._attr_icon = "mdi:refresh-circle"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Solar Forecast ML",
            manufacturer="Zara-Toorox",
            model="v4.4.6",
        )

    async def async_press(self) -> None:
        """Behandelt den Button-Druck."""
        await self.coordinator.async_manual_forecast()


class ManualLearningButton(ButtonEntity):
    """Ein Button, um den Lernprozess manuell auszulösen."""
    _attr_has_entity_name = True

    def __init__(self, coordinator: SolarForecastCoordinator, entry: ConfigEntry):
        """Initialisiere den Lern-Button."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_manual_learning"
        # KORREKTUR: Gekürzter, professioneller Name
        self._attr_name = "Manueller Lernprozess"
        self._attr_icon = "mdi:brain"
        # Die Geräte-Info verknüpft diesen Button mit dem selben Gerät wie die Sensoren
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )

    async def async_press(self) -> None:
        """Behandelt den Button-Druck."""
        await self.coordinator.async_manual_learning()

