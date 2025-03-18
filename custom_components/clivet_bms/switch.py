""" for switch component """
# https://github.com/home-assistant/core/blob/dev/homeassistant/components/switch/__init__.py

# pylint: disable = too-few-public-methods
from __future__ import annotations
import logging

from homeassistant.core import HomeAssistant, callback, Event, State
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.switch import (
    SwitchEntity,
    SwitchDeviceClass
)

from homeassistant.util import Throttle
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import (
    DOMAIN,
    POWER_TRANSLATION,
    UNIT_TRANSLATION,
    DISINFECT_TRANSLATION,
    SG_TRANSLATION,
    EVU_TRANSLATION,
    REMOTER_TRANSLATION,
)

from .coordinator import WaterHeaterCoordinator

from homeassistant.const import (
    STATE_OFF,
    STATE_ON
)

from .clivet.device import WaterHeater
from .clivet.const import (
    PowerState,
    UnitMode,
    DisinfectFunc,
    SGCmd,
    EVUCmd,
    RemoterMode,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant,
                            entry: ConfigEntry,
                            async_add_entities: AddEntitiesCallback,
                            ):
    """ Setup switch entries """

    device = hass.data[DOMAIN]["device"]
    coordinator = hass.data[DOMAIN]["coordinator"]

    entities = [
        SystemStateSwitch(coordinator, device),
        UnitSwitch(coordinator, device),
        DisinfectSwitch(coordinator, device),
        SmartGridSwitch(coordinator, device),
        SolarSignalSwitch(coordinator, device),
        RemoterSwitch(coordinator, device),
        DebugStateSwitch(device),
    ]
    async_add_entities(entities)

class SystemStateSwitch(CoordinatorEntity, SwitchEntity):
    """Select component to set system state """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "power"
    _attr_device_class: SwitchDeviceClass = SwitchDeviceClass.SWITCH

    def __init__(self,
                    coordinator: WaterHeaterCoordinator, # pylint: disable=unused-argument
                    device: WaterHeater, # pylint: disable=unused-argument
                ) -> None:
        super().__init__(coordinator)
        self._device = device
        #self._attr_name = f"Power State"
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-power-state-switch"
        self._attr_is_on = POWER_TRANSLATION[int(self._device.power)]
        _LOGGER.debug("[INIT] Power State: {} ({})".format(self._attr_is_on, type(POWER_TRANSLATION[int(self._device.power)])))
        if self._attr_is_on:
            self._attr_state = STATE_ON
            _LOGGER.debug("[INIT] Power State (ON): {}".format(self._attr_state))
        else:
            self._attr_state = STATE_OFF
            _LOGGER.debug("[INIT] Power State (OFF): {}".format(self._attr_state))

    @property
    def device_info(self) -> DeviceInfo:
        """Get Device information."""
        return self._attr_device_info

    async def async_turn_on(self, **kwargs):
        """ Turn the entity on. """
        _LOGGER.debug("Turn on system")
        ret = await self._device.async_set_on()
        if not ret:
            _LOGGER.exception("Error turning on the system")
        self._attr_is_on = True
        self._attr_state = STATE_ON
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """ Turn the entity off. """
        _LOGGER.debug("Turn off system")
        ret = await self._device.async_set_off()
        if not ret:
            _LOGGER.exception("Error turning off the system")
        self._attr_is_on = False
        self._attr_state = STATE_OFF
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """ Handle updated data from the coordinator """
        if 'power' in self.coordinator.data.keys():
            self._attr_is_on = POWER_TRANSLATION[int(self.coordinator.data['power'])]
            _LOGGER.debug("[UPDATE] Power State: {}".format(self._attr_is_on))
            if POWER_TRANSLATION[int(self.coordinator.data['power'])]:
                self._attr_state = STATE_ON
            else:
                self._attr_state = STATE_OFF
        else:
            _LOGGER.exception('[UPDATE] error updating power state')
        self.async_write_ha_state()

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        return POWER_TRANSLATION[int(self._device.power)]

    @property
    def icon(self) -> str | None:
        """Icon of the entity."""
        return "mdi:power"

class UnitSwitch(CoordinatorEntity, SwitchEntity):
    """Select component to set unit mode """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "unit"
    _attr_device_class: SwitchDeviceClass = SwitchDeviceClass.SWITCH
    _attr_entity_category: EntityCategory = EntityCategory.CONFIG

    def __init__(self,
                    coordinator: WaterHeaterCoordinator, # pylint: disable=unused-argument
                    device: WaterHeater, # pylint: disable=unused-argument
                ) -> None:
        super().__init__(coordinator)
        self._device = device
        #self._attr_name = f"Unit (°C/°F)"
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-unit-switch"
        self._attr_is_on = UNIT_TRANSLATION[int(self._device.unit_mode)]

    @property
    def device_info(self) -> DeviceInfo:
        """Get Device information."""
        return self._attr_device_info

    async def async_turn_on(self, **kwargs):
        """ choose Fahrenheit. """
        _LOGGER.debug("choose Fahrenheit")
        _ret:bool = False
        _ret = await self._device.async_set_unit('fahrenheit')
        if not _ret:
            _LOGGER.exception("Error choosing fahrenheit")
        self._attr_is_on = True
        self._attr_state = STATE_ON
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """ choose Celcius. """
        _LOGGER.debug("choose Celcius")
        _ret:bool = False
        _ret = await self._device.async_set_unit('celcius')
        if not _ret:
            _LOGGER.exception("Error choosing celcius")
        self._attr_is_on = False
        self._attr_state = STATE_OFF
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """ Handle updated data from the coordinator """
        if 'unit' in self.coordinator.data.keys():
            self._attr_is_on = UNIT_TRANSLATION[int(self.coordinator.data['unit'])]
            _LOGGER.debug("[UPDATE] Unit: {}".format(self.coordinator.data['unit']))
            if UNIT_TRANSLATION[int(self.coordinator.data['unit'])]:
                self._attr_state = STATE_ON
            else:
                self._attr_state = STATE_OFF
        else:
            _LOGGER.exception('[UPDATE] error updating unit mode')
        self.async_write_ha_state()

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        return UNIT_TRANSLATION[int(self._device.unit_mode)]

    @property
    def icon(self) -> str | None:
        """Icon of the entity."""
        return "mdi:temperature-celsius"

class DisinfectSwitch(CoordinatorEntity, SwitchEntity):
    """Select component to set disinfection """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "disinfect"
    _attr_device_class: SwitchDeviceClass = SwitchDeviceClass.SWITCH
    _attr_entity_category: EntityCategory = EntityCategory.CONFIG

    def __init__(self,
                    coordinator: WaterHeaterCoordinator, # pylint: disable=unused-argument
                    device: WaterHeater, # pylint: disable=unused-argument
                ) -> None:
        super().__init__(coordinator)
        self._device = device
        #self._attr_name = f"Disinfect"
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-disinfect-switch"
        self._attr_is_on = DISINFECT_TRANSLATION[int(self._device.disinfect)]

    @property
    def device_info(self) -> DeviceInfo:
        """Get Device information."""
        return self._attr_device_info

    async def async_turn_on(self, **kwargs):
        """ turn on disinfection. """
        _LOGGER.debug("turn on disinfection")
        _ret:bool = False
        _ret = await self._device.async_set_disinfect(DisinfectFunc.ON)
        if not _ret:
            _LOGGER.exception("Error turning on disinfection")
        self._attr_is_on = True
        self._attr_state = STATE_ON
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """ turn off disinfection. """
        _LOGGER.debug("turn off disinfection")
        _ret:bool = False
        _ret = await self._device.async_set_disinfect(DisinfectFunc.OFF)
        if not _ret:
            _LOGGER.exception("Error turning off disinfection")
        self._attr_is_on = False
        self._attr_state = STATE_OFF
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """ Handle updated data from the coordinator """
        if 'desinfect' in self.coordinator.data.keys():
            self._attr_is_on = DISINFECT_TRANSLATION[int(self.coordinator.data['desinfect'])]
            _LOGGER.debug("[UPDATE] Disinfect: {}".format(self.coordinator.data['desinfect']))
            if DISINFECT_TRANSLATION[int(self.coordinator.data['desinfect'])]:
                self._attr_state = STATE_ON
            else:
                self._attr_state = STATE_OFF
        else:
            _LOGGER.exception('[UPDATE] error updating disinfect function')
        self.async_write_ha_state()

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        return DISINFECT_TRANSLATION[int(self._device.disinfect)]

    @property
    def icon(self) -> str | None:
        """Icon of the entity."""
        return "mdi:virus-outline"

class SmartGridSwitch(CoordinatorEntity, SwitchEntity):
    """Select component to set smart grid """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "sg"
    _attr_device_class: SwitchDeviceClass = SwitchDeviceClass.SWITCH
    _attr_entity_category: EntityCategory = EntityCategory.CONFIG

    def __init__(self,
                    coordinator: WaterHeaterCoordinator, # pylint: disable=unused-argument
                    device: WaterHeater, # pylint: disable=unused-argument
                ) -> None:
        super().__init__(coordinator)
        self._device = device
        #self._attr_name = f"Smart Grid"
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-smart-grid-switch"
        self._attr_is_on = SG_TRANSLATION[int(self._device.smart_grid)]

    @property
    def device_info(self) -> DeviceInfo:
        """Get Device information."""
        return self._attr_device_info

    async def async_turn_on(self, **kwargs):
        """ turn on smart grid. """
        _LOGGER.debug("turn on smart grid")
        _ret:bool = False
        _ret = await self._device.async_set_smart_grid(SGCmd.ON)
        if not _ret:
            _LOGGER.exception("Error turning on smart grid")
        self._attr_is_on = True
        self._attr_state = STATE_ON
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """ turn off smart grid. """
        _LOGGER.debug("turn off smart grid")
        _ret:bool = False
        _ret = await self._device.async_set_smart_grid(SGCmd.OFF)
        if not _ret:
            _LOGGER.exception("Error turning off smart grid")
        self._attr_is_on = False
        self._attr_state = STATE_OFF
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """ Handle updated data from the coordinator """
        if 'sg' in self.coordinator.data.keys():
            self._attr_is_on = SG_TRANSLATION[int(self.coordinator.data['sg'])]
            _LOGGER.debug("[UPDATE] Smart Grid: {}".format(self.coordinator.data['sg']))
            if SG_TRANSLATION[int(self.coordinator.data['sg'])]:
                self._attr_state = STATE_ON
            else:
                self._attr_state = STATE_OFF
        else:
            _LOGGER.exception('[UPDATE] error updating smart grid function')
        self.async_write_ha_state()

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        return SG_TRANSLATION[int(self._device.smart_grid)]

    @property
    def icon(self) -> str | None:
        """Icon of the entity."""
        return "mdi:transmission-tower-export"

class SolarSignalSwitch(CoordinatorEntity, SwitchEntity):
    """Select component to set solar signal """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "evu"
    _attr_device_class: SwitchDeviceClass = SwitchDeviceClass.SWITCH
    _attr_entity_category: EntityCategory = EntityCategory.CONFIG

    def __init__(self,
                    coordinator: WaterHeaterCoordinator, # pylint: disable=unused-argument
                    device: WaterHeater, # pylint: disable=unused-argument
                ) -> None:
        super().__init__(coordinator)
        self._device = device
        #self._attr_name = f"Solar Signal EVU"
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-solar-signal-evu-switch"
        self._attr_is_on = EVU_TRANSLATION[int(self._device.evu)]

    @property
    def device_info(self) -> DeviceInfo:
        """Get Device information."""
        return self._attr_device_info

    async def async_turn_on(self, **kwargs):
        """ turn on solar signal EVU. """
        _LOGGER.debug("turn on solar signal EVU")
        _ret:bool = False
        _ret = await self._device.async_set_solar_signal_evu(EVUCmd.ON)
        if not _ret:
            _LOGGER.exception("Error turning on solar signal EVU")
        self._attr_is_on = True
        self._attr_state = STATE_ON
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """ turn off solar signal EVU. """
        _LOGGER.debug("turn off solar signal EVU")
        _ret:bool = False
        _ret = await self._device.async_set_solar_signal_evu(EVUCmd.OFF)
        if not _ret:
            _LOGGER.exception("Error turning off solar signal EVU")
        self._attr_is_on = False
        self._attr_state = STATE_OFF
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """ Handle updated data from the coordinator """
        if 'evu' in self.coordinator.data.keys():
            self._attr_is_on = EVU_TRANSLATION[int(self.coordinator.data['evu'])]
            _LOGGER.debug("[UPDATE] Solar Signal EVU: {}".format(self.coordinator.data['evu']))
            if EVU_TRANSLATION[int(self.coordinator.data['evu'])]:
                self._attr_state = STATE_ON
            else:
                self._attr_state = STATE_OFF
        else:
            _LOGGER.exception('[UPDATE] error updating solar signal EVU function')
        self.async_write_ha_state()

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        return EVU_TRANSLATION[int(self._device.evu)]

    @property
    def icon(self) -> str | None:
        """Icon of the entity."""
        return "mdi:solar-power-variant-outline"

class RemoterSwitch(CoordinatorEntity, SwitchEntity):
    """Select component to set remoter mode """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "remoter"
    _attr_device_class: SwitchDeviceClass = SwitchDeviceClass.SWITCH
    _attr_entity_category: EntityCategory = EntityCategory.CONFIG

    def __init__(self,
                    coordinator: WaterHeaterCoordinator, # pylint: disable=unused-argument
                    device: WaterHeater, # pylint: disable=unused-argument
                ) -> None:
        super().__init__(coordinator)
        self._device = device
        #self._attr_name = f"Remoter"
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-remoter-switch"
        self._attr_is_on = REMOTER_TRANSLATION[int(self._device.remoter)]

    @property
    def device_info(self) -> DeviceInfo:
        """Get Device information."""
        return self._attr_device_info

    async def async_turn_on(self, **kwargs):
        """ turn on remoter. """
        _LOGGER.debug("turn on remoter")
        _ret:bool = False
        _ret = await self._device.async_set_remoter(RemoterMode.ON)
        if not _ret:
            _LOGGER.exception("Error turning on remoter")
        self._attr_is_on = True
        self._attr_state = STATE_ON
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """ turn off remoter. """
        _LOGGER.debug("turn off remoter")
        _ret:bool = False
        _ret = await self._device.async_set_remoter(RemoterMode.OFF)
        if not _ret:
            _LOGGER.exception("Error turning off remoter")
        self._attr_is_on = False
        self._attr_state = STATE_OFF
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """ Handle updated data from the coordinator """
        if 'remoterMode' in self.coordinator.data.keys():
            self._attr_is_on = REMOTER_TRANSLATION[int(self.coordinator.data['remoterMode'])]
            _LOGGER.debug("[UPDATE] Remoter: {}".format(self.coordinator.data['remoterMode']))
            if REMOTER_TRANSLATION[int(self.coordinator.data['remoterMode'])]:
                self._attr_state = STATE_ON
            else:
                self._attr_state = STATE_OFF
        else:
            _LOGGER.exception('[UPDATE] error updating remoter function')
        self.async_write_ha_state()

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        return REMOTER_TRANSLATION[int(self._device.remoter)]

    @property
    def icon(self) -> str | None:
        """Icon of the entity."""
        return "mdi:remote"

class DebugStateSwitch(SwitchEntity):
    """Select component to set system state """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "modbus_debug"
    _attr_device_class: SwitchDeviceClass = SwitchDeviceClass.SWITCH
    _attr_entity_category: EntityCategory = EntityCategory.DIAGNOSTIC

    def __init__(self,
                device: WaterHeater, # pylint: disable=unused-argument
                ) -> None:
        super().__init__()
        self._device = device
        #self._attr_name = f"Modbus Debug"
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-modbus-debug-switch"
        self._attr_is_on = bool(int(self._device.debug))
        if bool(int(self._device.debug)):
            self._attr_state = STATE_ON
        else:
            self._attr_state = STATE_OFF

    @property
    def device_info(self) -> DeviceInfo:
        """Get Device information."""
        return self._attr_device_info

    async def async_turn_on(self, **kwargs):
        """ Turn the entity on. """
        _LOGGER.debug("Turn on Debug")
        await self._device.async_set_debug(True)
        self._attr_is_on = True
        self._attr_state = STATE_ON

    async def async_turn_off(self, **kwargs):
        """ Turn the entity off. """
        _LOGGER.debug("Turn off Debug")
        await self._device.async_set_debug(False)
        self._attr_is_on = False
        self._attr_state = STATE_OFF

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        return self._device.debug

    @property
    def icon(self) -> str | None:
        """Icon of the entity."""
        return "mdi:bug"