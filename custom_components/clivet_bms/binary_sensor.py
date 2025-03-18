""" for Binary sensors components """
# https://github.com/home-assistant/core/blob/master/homeassistant/components/binary_sensor/__init__.py

import logging

from homeassistant.core import HomeAssistant, callback, Event, State
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)

from  homeassistant.helpers.event import (
    async_track_time_interval,
    async_track_state_change_event,
)

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from homeassistant.const import (
    STATE_OFF,
    STATE_ON,
)

from .const import (
    DOMAIN,
    WIFI_TRANSLATION,
    DEFROST_TRANSLATION,
    SOLAR_TRANSLATION,
    ALARM_TRANSLATION,
    COMPRESSOR_TRANSLATION,
    E_HEATER_TRANSLATION,
    VALVE_TRANSLATION,
    SOLAR_PUMP_TRANSLATION,
)

from .coordinator import WaterHeaterCoordinator
from .clivet.device import WaterHeater

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant,
                            entry: ConfigEntry,
                            async_add_entities: AddEntitiesCallback):
    """ Configuration des entités text à partir de la configuration
        ConfigEntry passée en argument
    """
    entities = []
    device = hass.data[DOMAIN]["device"]
    coordinator = hass.data[DOMAIN]["coordinator"]

    entities.append(WifiSensor(coordinator, device))
    entities.append(DefrostSensor(coordinator, device))
    entities.append(SolarSensor(coordinator, device))
    entities.append(AlarmSensor(coordinator, device))
    entities.append(CompressorSensor(coordinator, device))
    entities.append(ElectricHeaterSensor(coordinator, device))
    entities.append(FourWayValveSensor(coordinator, device))
    entities.append(SolarPanelPumpSensor(coordinator, device))
    async_add_entities(entities)

class WifiSensor(CoordinatorEntity, BinarySensorEntity):
    # pylint: disable = too-many-instance-attributes
    """ Representation of a binary sensor """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "wifi"
    _attr_device_class: BinarySensorDeviceClass | None = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category: EntityCategory | None = EntityCategory.DIAGNOSTIC
    _attr_is_on: bool | None = False
    _attr_state: None = STATE_OFF

    def __init__(self,
                    coordinator: WaterHeaterCoordinator, # pylint: disable=unused-argument
                    device: WaterHeater, # pylint: disable=unused-argument,
                    ) -> None:
        """ Class constructor """
        super().__init__(coordinator)
        self._device = device
        #self._attr_name = f"Wifi connection status"
        self._attr_entity_registry_enabled_default = True
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-wifi-status-binary-sensor"
        self._attr_is_on = WIFI_TRANSLATION[int(self._device.wifi_status)]
        if self._attr_is_on:
            self._attr_state = STATE_ON
        else:
            self._attr_state = STATE_OFF

    @property
    def device_info(self) -> DeviceInfo:
        """Get Device information."""
        return self._attr_device_info

    @property
    def icon(self) -> str | None:
        return "mdi:wifi"

    @callback
    def _handle_coordinator_update(self) -> None:
        """ Handle updated data from the coordinator """
        if 'wifi' in self.coordinator.data.keys():
            _LOGGER.debug("[UPDATE] wifi:{}".format(self.coordinator.data['wifi']))
            self._attr_is_on = WIFI_TRANSLATION[int(self.coordinator.data['wifi'])]
            if self._attr_is_on:
                self._attr_state = STATE_ON
            else:
                self._attr_state = STATE_OFF
        else:
            _LOGGER.exception('[UPDATE] error updating wifi connection status')
        self.async_write_ha_state()

class DefrostSensor(CoordinatorEntity, BinarySensorEntity):
    # pylint: disable = too-many-instance-attributes
    """ Representation of a binary sensor """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "defrost"
    _attr_device_class: BinarySensorDeviceClass | None = BinarySensorDeviceClass.RUNNING
    _attr_is_on: bool | None = False
    _attr_state: None = STATE_OFF

    def __init__(self,
                    coordinator: WaterHeaterCoordinator, # pylint: disable=unused-argument
                    device: WaterHeater, # pylint: disable=unused-argument,
                    ) -> None:
        """ Class constructor """
        super().__init__(coordinator)
        self._device = device
        #self._attr_name = f"Defrost status"
        self._attr_entity_registry_enabled_default = True
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-defrost-status-binary-sensor"
        self._attr_is_on = DEFROST_TRANSLATION[int(self._device.defrost_status)]
        if self._attr_is_on:
            self._attr_state = STATE_ON
        else:
            self._attr_state = STATE_OFF

    @property
    def device_info(self) -> DeviceInfo:
        """Get Device information."""
        return self._attr_device_info

    @property
    def icon(self) -> str | None:
        return "mdi:snowflake-melt"

    @callback
    def _handle_coordinator_update(self) -> None:
        """ Handle updated data from the coordinator """
        if 'defrost' in self.coordinator.data.keys():
            _LOGGER.debug("[UPDATE] defrost:{}".format(self.coordinator.data['defrost']))
            self._attr_is_on = DEFROST_TRANSLATION[int(self.coordinator.data['defrost'])]
            if self._attr_is_on:
                self._attr_state = STATE_ON
            else:
                self._attr_state = STATE_OFF
        else:
            _LOGGER.exception('[UPDATE] error updating defrost status')
        self.async_write_ha_state()

class SolarSensor(CoordinatorEntity, BinarySensorEntity):
    # pylint: disable = too-many-instance-attributes
    """ Representation of a binary sensor """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "solar_kit"
    _attr_device_class: BinarySensorDeviceClass | None = BinarySensorDeviceClass.RUNNING
    _attr_entity_category: EntityCategory | None = EntityCategory.DIAGNOSTIC
    _attr_is_on: bool | None = False
    _attr_state: None = STATE_OFF

    def __init__(self,
                    coordinator: WaterHeaterCoordinator, # pylint: disable=unused-argument
                    device: WaterHeater, # pylint: disable=unused-argument,
                    ) -> None:
        """ Class constructor """
        super().__init__(coordinator)
        self._device = device
        #self._attr_name = f"Solar kit status"
        self._attr_entity_registry_enabled_default = True
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-solar-kit-status-binary-sensor"
        self._attr_is_on = SOLAR_TRANSLATION[int(self._device.solar_kit_status)]
        if self._attr_is_on:
            self._attr_state = STATE_ON
        else:
            self._attr_state = STATE_OFF

    @property
    def device_info(self) -> DeviceInfo:
        """Get Device information."""
        return self._attr_device_info

    @property
    def icon(self) -> str | None:
        return "mdi:solar-power"

    @callback
    def _handle_coordinator_update(self) -> None:
        """ Handle updated data from the coordinator """
        if 'solar_kit' in self.coordinator.data.keys():
            _LOGGER.debug("[UPDATE] solar kit:{}".format(self.coordinator.data['solar_kit']))
            self._attr_is_on = SOLAR_TRANSLATION[int(self.coordinator.data['solar_kit'])]
            if self._attr_is_on:
                self._attr_state = STATE_ON
            else:
                self._attr_state = STATE_OFF
        else:
            _LOGGER.exception('[UPDATE] error updating solar kit status')
        self.async_write_ha_state()

class AlarmSensor(CoordinatorEntity, BinarySensorEntity):
    # pylint: disable = too-many-instance-attributes
    """ Representation of a binary sensor """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "alarm"
    _attr_device_class: BinarySensorDeviceClass | None = BinarySensorDeviceClass.RUNNING
    _attr_entity_category: EntityCategory | None = EntityCategory.DIAGNOSTIC
    _attr_is_on: bool | None = False
    _attr_state: None = STATE_OFF

    def __init__(self,
                    coordinator: WaterHeaterCoordinator, # pylint: disable=unused-argument
                    device: WaterHeater, # pylint: disable=unused-argument,
                    ) -> None:
        """ Class constructor """
        super().__init__(coordinator)
        self._device = device
        #self._attr_name = f"Alarm"
        self._attr_entity_registry_enabled_default = True
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-alarm-binary-sensor"
        self._attr_is_on = ALARM_TRANSLATION[int(self._device.alarm)]
        if self._attr_is_on:
            self._attr_state = STATE_ON
        else:
            self._attr_state = STATE_OFF

    @property
    def device_info(self) -> DeviceInfo:
        """Get Device information."""
        return self._attr_device_info

    @property
    def icon(self) -> str | None:
        return "mdi:alarm-light"

    @callback
    def _handle_coordinator_update(self) -> None:
        """ Handle updated data from the coordinator """
        if 'alarm' in self.coordinator.data.keys():
            _LOGGER.debug("[UPDATE] alarm:{}".format(self.coordinator.data['alarm']))
            self._attr_is_on = ALARM_TRANSLATION[int(self.coordinator.data['alarm'])]
            if self._attr_is_on:
                self._attr_state = STATE_ON
            else:
                self._attr_state = STATE_OFF
        else:
            _LOGGER.exception('[UPDATE] error updating alarm status')
        self.async_write_ha_state()

class CompressorSensor(CoordinatorEntity, BinarySensorEntity):
    # pylint: disable = too-many-instance-attributes
    """ Representation of a binary sensor """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "compressor"
    _attr_device_class: BinarySensorDeviceClass | None = BinarySensorDeviceClass.RUNNING
    _attr_is_on: bool | None = False
    _attr_state: None = STATE_OFF

    def __init__(self,
                    coordinator: WaterHeaterCoordinator, # pylint: disable=unused-argument
                    device: WaterHeater, # pylint: disable=unused-argument,
                    ) -> None:
        """ Class constructor """
        super().__init__(coordinator)
        self._device = device
        #self._attr_name = f"Compressor"
        self._attr_entity_registry_enabled_default = True
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-compressor-binary-sensor"
        self._attr_is_on = COMPRESSOR_TRANSLATION[int(self._device.compressor)]
        if self._attr_is_on:
            self._attr_state = STATE_ON
        else:
            self._attr_state = STATE_OFF

    @property
    def device_info(self) -> DeviceInfo:
        """Get Device information."""
        return self._attr_device_info

    @property
    def icon(self) -> str | None:
        return "mdi:pump"

    @callback
    def _handle_coordinator_update(self) -> None:
        """ Handle updated data from the coordinator """
        if 'compressor' in self.coordinator.data.keys():
            _LOGGER.debug("[UPDATE] compressor:{}".format(self.coordinator.data['compressor']))
            self._attr_is_on = COMPRESSOR_TRANSLATION[int(self.coordinator.data['compressor'])]
            if self._attr_is_on:
                self._attr_state = STATE_ON
            else:
                self._attr_state = STATE_OFF
        else:
            _LOGGER.exception('[UPDATE] error updating compressor status')
        self.async_write_ha_state()

class ElectricHeaterSensor(CoordinatorEntity, BinarySensorEntity):
    # pylint: disable = too-many-instance-attributes
    """ Representation of a binary sensor """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "elec_heater"
    _attr_device_class: BinarySensorDeviceClass | None = BinarySensorDeviceClass.RUNNING
    _attr_is_on: bool | None = False
    _attr_state: None = STATE_OFF

    def __init__(self,
                    coordinator: WaterHeaterCoordinator, # pylint: disable=unused-argument
                    device: WaterHeater, # pylint: disable=unused-argument,
                    ) -> None:
        """ Class constructor """
        super().__init__(coordinator)
        self._device = device
        #self._attr_name = f"Electric Heater"
        self._attr_entity_registry_enabled_default = True
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-electric-heater-binary-sensor"
        self._attr_is_on = E_HEATER_TRANSLATION[int(self._device.elecheater)]
        if self._attr_is_on:
            self._attr_state = STATE_ON
        else:
            self._attr_state = STATE_OFF

    @property
    def device_info(self) -> DeviceInfo:
        """Get Device information."""
        return self._attr_device_info

    @property
    def icon(self) -> str | None:
        return "mdi:radiator"

    @callback
    def _handle_coordinator_update(self) -> None:
        """ Handle updated data from the coordinator """
        if 'elecHeater' in self.coordinator.data.keys():
            _LOGGER.debug("[UPDATE] Electric Heater:{}".format(self.coordinator.data['elecHeater']))
            self._attr_is_on = E_HEATER_TRANSLATION[int(self.coordinator.data['elecHeater'])]
            if self._attr_is_on:
                self._attr_state = STATE_ON
            else:
                self._attr_state = STATE_OFF
        else:
            _LOGGER.exception('[UPDATE] error updating electric heater status')
        self.async_write_ha_state()

class FourWayValveSensor(CoordinatorEntity, BinarySensorEntity):
    # pylint: disable = too-many-instance-attributes
    """ Representation of a binary sensor """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "valve"
    _attr_device_class: BinarySensorDeviceClass | None = BinarySensorDeviceClass.RUNNING
    _attr_is_on: bool | None = False
    _attr_state: None = STATE_OFF

    def __init__(self,
                    coordinator: WaterHeaterCoordinator, # pylint: disable=unused-argument
                    device: WaterHeater, # pylint: disable=unused-argument,
                    ) -> None:
        """ Class constructor """
        super().__init__(coordinator)
        self._device = device
        #self._attr_name = f"4 Way valve"
        self._attr_entity_registry_enabled_default = True
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-4-way-valve-binary-sensor"
        self._attr_is_on = VALVE_TRANSLATION[int(self._device.fourwayvalve)]
        if self._attr_is_on:
            self._attr_state = STATE_ON
        else:
            self._attr_state = STATE_OFF

    @property
    def device_info(self) -> DeviceInfo:
        """Get Device information."""
        return self._attr_device_info

    @property
    def icon(self) -> str | None:
        return "mdi:pipe-valve"

    @callback
    def _handle_coordinator_update(self) -> None:
        """ Handle updated data from the coordinator """
        if 'valve' in self.coordinator.data.keys():
            _LOGGER.debug("[UPDATE] 4 way valve:{}".format(self.coordinator.data['valve']))
            self._attr_is_on = VALVE_TRANSLATION[int(self.coordinator.data['valve'])]
            if self._attr_is_on:
                self._attr_state = STATE_ON
            else:
                self._attr_state = STATE_OFF
        else:
            _LOGGER.exception('[UPDATE] error updating 4 way valve status')
        self.async_write_ha_state()

class SolarPanelPumpSensor(CoordinatorEntity, BinarySensorEntity):
    # pylint: disable = too-many-instance-attributes
    """ Representation of a binary sensor """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "solar_panel_pump"
    _attr_device_class: BinarySensorDeviceClass | None = BinarySensorDeviceClass.RUNNING
    _attr_entity_category: EntityCategory | None = EntityCategory.DIAGNOSTIC
    _attr_is_on: bool | None = False
    _attr_state: None = STATE_OFF

    def __init__(self,
                    coordinator: WaterHeaterCoordinator, # pylint: disable=unused-argument
                    device: WaterHeater, # pylint: disable=unused-argument,
                    ) -> None:
        """ Class constructor """
        super().__init__(coordinator)
        self._device = device
        #self._attr_name = f"Solar panel water pump"
        self._attr_entity_registry_enabled_default = True
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-solar-pump-binary-sensor"
        self._attr_is_on = SOLAR_PUMP_TRANSLATION[int(self._device.solar_pump)]
        if self._attr_is_on:
            self._attr_state = STATE_ON
        else:
            self._attr_state = STATE_OFF

    @property
    def device_info(self) -> DeviceInfo:
        """Get Device information."""
        return self._attr_device_info

    @property
    def icon(self) -> str | None:
        return "mdi:water-pump"

    @callback
    def _handle_coordinator_update(self) -> None:
        """ Handle updated data from the coordinator """
        if 'solarPump' in self.coordinator.data.keys():
            _LOGGER.debug("[UPDATE] solar panel water pump:{}".format(self.coordinator.data['solarPump']))
            self._attr_is_on = SOLAR_PUMP_TRANSLATION[int(self.coordinator.data['solarPump'])]
            if self._attr_is_on:
                self._attr_state = STATE_ON
            else:
                self._attr_state = STATE_OFF
        else:
            _LOGGER.exception('[UPDATE] error updating solar panel water pump status')
        self.async_write_ha_state()