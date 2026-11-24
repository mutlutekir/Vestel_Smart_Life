"""Switch platform: turbo/sleep/ionizer/eco toggles (packed in ACFANPO) plus
an auto-off enable/disable switch (ACOFFTV) - all confirmed against real
device captures, see README."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from . import VestelAcCoordinator
from .api import VestelAcApi
from .const import DOMAIN

FANPO_TOGGLES = {
    "turbo": "Turbo",
    "sleep": "Uyku Modu",
    "ionizer": "İyonizer",
    "eco": "Tasarruf Modu",
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    stored = hass.data[DOMAIN][entry.entry_id]
    coordinator: VestelAcCoordinator = stored["coordinator"]
    api: VestelAcApi = stored["api"]
    devices: list[dict[str, str]] = stored["devices"]

    entities: list[SwitchEntity] = []
    for device in devices:
        for key, label in FANPO_TOGGLES.items():
            entities.append(
                _VestelAcFanpoToggle(coordinator, api, entry.entry_id, device, key, label)
            )
        entities.append(_VestelAcAutoOffEnabled(coordinator, api, entry.entry_id, device))
    for device in stored.get("fridges", []):
        for register, key, label in FRIDGE_SWITCHES:
            entities.append(
                _VestelFridgeSwitch(coordinator, api, entry.entry_id, device, register, key, label)
            )
    async_add_entities(entities)


# (register, status key, entity name)
FRIDGE_SWITCHES = (
    ("RFCLOCK", "child_lock", "Çocuk Kilidi"),
    ("RFSSAVE", "screen_saver", "Ekran Koruyucu"),
)


class _VestelFridgeSwitch(CoordinatorEntity[VestelAcCoordinator], SwitchEntity):
    """Refrigerator child lock or screen saver (0 / 1 registers)."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: VestelAcCoordinator,
        api: VestelAcApi,
        entry_id: str,
        device: dict[str, str],
        register: str,
        key: str,
        label: str,
    ) -> None:
        super().__init__(coordinator)
        self._api = api
        self._device_id = device["device_id"]
        self._register = register
        self._key = key
        self._attr_name = label
        self._attr_unique_id = f"{entry_id}_{self._device_id}_fridge_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            manufacturer="Vestel",
            name=device.get("device_name") or self._device_id,
            model="Buzdolabı",
        )

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data.get(self._device_id, {}).get(self._key)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._api.async_set_fridge_flag(self._device_id, self._register, True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._api.async_set_fridge_flag(self._device_id, self._register, False)
        await self.coordinator.async_request_refresh()


class _VestelAcFanpoToggle(CoordinatorEntity[VestelAcCoordinator], SwitchEntity):
    """A single ACFANPO packed toggle bit (turbo/sleep/ionizer/eco)."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: VestelAcCoordinator,
        api: VestelAcApi,
        entry_id: str,
        device: dict[str, str],
        key: str,
        label: str,
    ) -> None:
        super().__init__(coordinator)
        self._api = api
        self._device_id = device["device_id"]
        self._key = key
        self._attr_name = label
        self._attr_unique_id = f"{entry_id}_{self._device_id}_{key}"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, self._device_id)})

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data.get(self._device_id, {}).get(self._key)

    async def async_turn_on(self, **kwargs) -> None:
        await self._set(True)

    async def async_turn_off(self, **kwargs) -> None:
        await self._set(False)

    async def _set(self, value: bool) -> None:
        status = self.coordinator.data.get(self._device_id, {})
        current_raw = status.get("fanpo_raw", 0)
        await self._api.async_set_fanpo(self._device_id, current_raw, **{self._key: value})
        await self.coordinator.async_request_refresh()


class _VestelAcAutoOffEnabled(CoordinatorEntity[VestelAcCoordinator], SwitchEntity):
    """Enables/disables the auto-off (delayed shutdown) timer.

    Turning this on (re)sends whatever hour/minute the companion
    time.vestel_smart_life_auto_off entity currently holds (default 00:00 if never
    set); turning it off sends the 2047 "disabled" sentinel.
    """

    _attr_has_entity_name = True
    _attr_name = "Otomatik Kapatma Aktif"

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
        self._attr_unique_id = f"{entry_id}_{self._device_id}_auto_off_enabled"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, self._device_id)})

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data.get(self._device_id, {}).get("auto_off_enabled")

    async def async_turn_on(self, **kwargs) -> None:
        status = self.coordinator.data.get(self._device_id, {})
        hour = status.get("auto_off_hour") or 0
        minute = status.get("auto_off_minute") or 0
        await self._api.async_set_auto_off(
            self._device_id, hour, minute, now=dt_util.now()
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self._api.async_clear_auto_off(self._device_id)
        await self.coordinator.async_request_refresh()
