"""Select platform: vertical louver position control.

Confirmed against real device captures (see README): the louver field is a
single 0-6 value where 0 = durdur (stop/fixed at last position), 1-5 = sabit
kademe (fixed step, 1=en yatay/açık .. 5=en dik), 6 = salınım (continuous
swing).

Horizontal louver control is intentionally not exposed: its encoding has not
been confirmed on a real unit yet, so nothing writes those bits.
"""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import VestelAcCoordinator
from .api import VestelAcApi
from .const import (
    DOMAIN,
    FRIDGE_COOLER_TEMPS,
    FRIDGE_FREEZER_TEMPS,
    FRIDGE_MODES,
    LOUVER_OPTION_NAMES,
    LOUVER_OPTIONS,
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    stored = hass.data[DOMAIN][entry.entry_id]
    coordinator: VestelAcCoordinator = stored["coordinator"]
    api: VestelAcApi = stored["api"]
    devices: list[dict[str, str]] = stored["devices"]

    entities: list[SelectEntity] = []
    for device in devices:
        entities.append(
            _VestelAcLouverSelect(
                coordinator, api, entry.entry_id, device, axis="vertical", name="Dikey Kanatçık"
            )
        )
    for device in stored.get("fridges", []):
        entities.append(_VestelFridgeSetpoint(coordinator, api, entry.entry_id, device, "cooler"))
        entities.append(_VestelFridgeSetpoint(coordinator, api, entry.entry_id, device, "freezer"))
        entities.append(_VestelFridgeMode(coordinator, api, entry.entry_id, device))
    async_add_entities(entities)


def _fridge_device_info(device: dict[str, str]) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, device["device_id"])},
        manufacturer="Vestel",
        name=device.get("device_name") or device["device_id"],
        model="Buzdolabı",
    )


class _VestelFridgeSetpoint(CoordinatorEntity[VestelAcCoordinator], SelectEntity):
    """Cooler or freezer temperature, chosen from the values the app offers."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: VestelAcCoordinator,
        api: VestelAcApi,
        entry_id: str,
        device: dict[str, str],
        zone: str,
    ) -> None:
        super().__init__(coordinator)
        self._api = api
        self._device_id = device["device_id"]
        self._zone = zone
        temps = FRIDGE_COOLER_TEMPS if zone == "cooler" else FRIDGE_FREEZER_TEMPS
        self._by_option = {f"{t} °C": t for t in temps}
        self._attr_options = list(self._by_option)
        self._attr_name = "Soğutucu Sıcaklığı" if zone == "cooler" else "Dondurucu Sıcaklığı"
        self._attr_unique_id = f"{entry_id}_{self._device_id}_fridge_{zone}_setpoint"
        self._attr_device_info = _fridge_device_info(device)

    @property
    def current_option(self) -> str | None:
        value = self.coordinator.data.get(self._device_id, {}).get(f"{self._zone}_set")
        label = f"{value} °C"
        return label if label in self._by_option else None

    async def async_select_option(self, option: str) -> None:
        value = self._by_option[option]
        await self._api.async_set_fridge_setpoints(self._device_id, **{self._zone: value})
        await self.coordinator.async_request_refresh()


class _VestelFridgeMode(CoordinatorEntity[VestelAcCoordinator], SelectEntity):
    """The refrigerator mode (normal, super freeze, holiday, ...)."""

    _attr_has_entity_name = True
    _attr_name = "Mod"
    _attr_options = list(FRIDGE_MODES.values())

    def __init__(
        self,
        coordinator: VestelAcCoordinator,
        api: VestelAcApi,
        entry_id: str,
        device: dict[str, str],
    ) -> None:
        super().__init__(coordinator)
        self._api = api
        self._device_id = device["device_id"]
        self._attr_unique_id = f"{entry_id}_{self._device_id}_fridge_mode"
        self._attr_device_info = _fridge_device_info(device)

    @property
    def current_option(self) -> str | None:
        return self.coordinator.data.get(self._device_id, {}).get("mode")

    async def async_select_option(self, option: str) -> None:
        raw = next(k for k, v in FRIDGE_MODES.items() if v == option)
        await self._api.async_set_fridge_mode(self._device_id, raw)
        await self.coordinator.async_request_refresh()


class _VestelAcLouverSelect(CoordinatorEntity[VestelAcCoordinator], SelectEntity):
    """The vertical louver axis, 0-6 as a dropdown."""

    _attr_has_entity_name = True
    _attr_options = list(LOUVER_OPTIONS.keys())

    def __init__(
        self,
        coordinator: VestelAcCoordinator,
        api: VestelAcApi,
        entry_id: str,
        device: dict[str, str],
        axis: str,
        name: str,
    ) -> None:
        super().__init__(coordinator)
        self._api = api
        self._device_id = device["device_id"]
        self._axis = axis  # only "vertical" is exposed
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_{self._device_id}_{axis}_louver"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, self._device_id)})

    @property
    def current_option(self) -> str | None:
        status = self.coordinator.data.get(self._device_id, {})
        value = status.get(self._axis)
        if value is None:
            return None
        return LOUVER_OPTION_NAMES.get(value, "durdur")

    async def async_select_option(self, option: str) -> None:
        status = self.coordinator.data.get(self._device_id, {})
        current_raw = status.get("fanpo_raw", 0)
        value = LOUVER_OPTIONS[option]
        kwargs = {self._axis: value}
        await self._api.async_set_fanpo(self._device_id, current_raw, **kwargs)
        await self.coordinator.async_request_refresh()
