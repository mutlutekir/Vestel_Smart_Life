"""Binary sensors for refrigerators: the door."""
from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import VestelAcCoordinator, appliances
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    stored = hass.data[DOMAIN][entry.entry_id]
    coordinator: VestelAcCoordinator = stored["coordinator"]
    entities: list[BinarySensorEntity] = [
        _VestelFridgeDoor(coordinator, entry.entry_id, device)
        for device in stored.get("fridges", [])
    ]
    for device in stored.get("appliances", []):
        status = coordinator.data.get(device["device_id"], {})
        for role in status.get("flags", {}):
            entities.append(_VestelApplianceFlag(coordinator, entry.entry_id, device, role))
        if status.get("problem") is not None:
            entities.append(_VestelApplianceProblem(coordinator, entry.entry_id, device))
    async_add_entities(entities)


class _VestelFridgeDoor(CoordinatorEntity[VestelAcCoordinator], BinarySensorEntity):
    """Open when the refrigerator reports anything other than "both doors closed".

    That is the app's own rule. Which of the two doors is open is not exposed: the
    meaning of the individual values is not confirmed, see the raw value attribute.
    """

    _attr_has_entity_name = True
    _attr_name = "Kapı"
    _attr_device_class = BinarySensorDeviceClass.DOOR

    def __init__(
        self, coordinator: VestelAcCoordinator, entry_id: str, device: dict[str, str]
    ) -> None:
        super().__init__(coordinator)
        self._device_id = device["device_id"]
        self._attr_unique_id = f"{entry_id}_{self._device_id}_fridge_door"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            manufacturer="Vestel",
            name=device.get("device_name") or self._device_id,
            model="Buzdolabı",
        )

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data.get(self._device_id, {}).get("door_open")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"ham_deger": self.coordinator.data.get(self._device_id, {}).get("door_raw")}


def _family_device_info(device: dict[str, str]) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, device["device_id"])},
        manufacturer="Vestel",
        name=device.get("device_name") or device["device_id"],
        model=appliances.FAMILY_NAMES.get(device.get("device_type"), "Vestel"),
    )


class _VestelApplianceFlag(CoordinatorEntity[VestelAcCoordinator], BinarySensorEntity):
    """One on/off bit of a washing machine, dryer, dishwasher, oven or fridge-freezer."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: VestelAcCoordinator, entry_id: str, device: dict[str, str], role: str
    ) -> None:
        super().__init__(coordinator)
        self._device_id = device["device_id"]
        self._role = role
        self._attr_name = appliances.role_name(role)
        self._attr_unique_id = (
            f"{entry_id}_{self._device_id}_flag_{role.lower().replace('.', '_')}"
        )
        self._attr_device_info = _family_device_info(device)
        if role not in appliances.MAIN_ROLES:
            self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data.get(self._device_id, {}).get("flags", {}).get(self._role)


class _VestelApplianceProblem(CoordinatorEntity[VestelAcCoordinator], BinarySensorEntity):
    """On while the appliance reports an error; the error names are an attribute."""

    _attr_has_entity_name = True
    _attr_name = "Hata Var"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(
        self, coordinator: VestelAcCoordinator, entry_id: str, device: dict[str, str]
    ) -> None:
        super().__init__(coordinator)
        self._device_id = device["device_id"]
        self._attr_unique_id = f"{entry_id}_{self._device_id}_problem"
        self._attr_device_info = _family_device_info(device)

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data.get(self._device_id, {}).get("problem")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"hatalar": self.coordinator.data.get(self._device_id, {}).get("errors", [])}
