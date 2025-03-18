""" for sensors components """
# https://github.com/home-assistant/core/blob/master/homeassistant/components/sensor/__init__.py

import logging
from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant, callback, Event, State
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from  homeassistant.helpers.event import (
    async_track_time_interval,
    async_track_state_change_event,
)

from homeassistant.const import (
    ATTR_TEMPERATURE,
    UnitOfTime,
    UnitOfTemperature,
    UnitOfElectricCurrent,
)

from .const import (
    DOMAIN,
    MODEL_TRANSLATION,
)

from .coordinator import WaterHeaterCoordinator

from .clivet.device import WaterHeater
from .clivet.const import (
    UnitMode,
)


_LOGGER = logging.getLogger(__name__)
MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)

async def async_setup_entry(hass: HomeAssistant,
                            entry: ConfigEntry,
                            async_add_entities: AddEntitiesCallback):
    """ Configuration des entités sensor à partir de la configuration
        ConfigEntry passée en argument
    """
    entities = []
    device = hass.data[DOMAIN]["device"]
    coordinator = hass.data[DOMAIN]["coordinator"]
    if entry.data.get("Mode") == "Modbus RTU":
        entities.append(DiagnosticsSensor(device, "Device", entry.data))
        entities.append(DiagnosticsSensor(device, "Address", entry.data))
        entities.append(DiagModbusSensor(device, entry.data))
    elif entry.data.get("Mode") == "Modbus TCP":
        entities.append(DiagModbusSensor(device, entry.data))
    else:
        _LOGGER.error("Mode unknown")

    entities.append(DiagT5USensor(coordinator, device))
    entities.append(DiagT5LSensor(coordinator, device))
    entities.append(DiagT3Sensor(coordinator, device))
    entities.append(DiagT4Sensor(coordinator, device))
    entities.append(DiagTPSensor(coordinator, device))
    entities.append(DiagTHSensor(coordinator, device))
    entities.append(DiagTXSensor(coordinator, device))
    entities.append(DiagCompTimeSensor(coordinator, device))
    entities.append(CompCurrentSensor(coordinator, device))
    entities.append(FanSpeedSensor(coordinator, device))
    entities.append(ErrCodeSensor(coordinator, device))
    entities.append(DiagModelSensor(device))
    entities.append(DiagMainVersionSensor(device))
    entities.append(DiagWireVersionSensor(device))

    async_add_entities(entities)

class DiagnosticsSensor(SensorEntity):
    # pylint: disable = too-many-instance-attributes
    """ Representation of a Sensor """
    _attr_has_entity_name: bool = True
    _attr_entity_category: EntityCategory | None = EntityCategory.DIAGNOSTIC

    def __init__(self,
                    device: WaterHeater, # pylint: disable=unused-argument,
                    name:str, # pylint: disable=unused-argument
                    entry_infos, # pylint: disable=unused-argument
                    ) -> None:
        """ Class constructor """
        self._device = device
        self._attr_name = f"{self._device.name} {name}"
        self._attr_entity_registry_enabled_default = True
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{name}-sensor"
        self._attr_native_value = entry_infos.get(name)

    @property
    def icon(self) -> str | None:
        return "mdi:monitor"

    @property
    def should_poll(self) -> bool:
        """ Do not poll for those entities """
        return False

class DiagModbusSensor(SensorEntity):
    # pylint: disable = too-many-instance-attributes
    """ Representation of a Sensor """
    _attr_has_entity_name: bool = True
    _attr_entity_category: EntityCategory | None = EntityCategory.DIAGNOSTIC

    def __init__(self,
                    device: WaterHeater, # pylint: disable=unused-argument,
                    entry_infos, # pylint: disable=unused-argument
                    ) -> None:
        """ Class constructor """
        self._device = device
        self._attr_entity_registry_enabled_default = True
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-Modbus-RTU-sensor"
        if entry_infos.get("Mode") == 'Modbus RTU':
            self._attr_name = f"{self._device.name} Modbus RTU"
            self._attr_native_value = "{} {}{}{}".format(entry_infos.get("Baudrate"),
                                                        entry_infos.get("Sizebyte"),
                                                        entry_infos.get("Parity")[0],
                                                        entry_infos.get("Stopbits"))
        elif entry_infos.get("Mode") == 'Modbus TCP':
            self._attr_name = f"{self._device.name} Modbus TCP"
            self._attr_native_value = "{}:{}".format(entry_infos.get("Address"),
                                                        entry_infos.get("Port"))

    @property
    def icon(self) -> str | None:
        return "mdi:monitor"

    @property
    def should_poll(self) -> bool:
        """ Do not poll for those entities """
        return False

class DiagT5USensor(CoordinatorEntity, SensorEntity):
    # pylint: disable = too-many-instance-attributes
    """ Representation of a Sensor """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "water_temp_upper_pos"
    _attr_device_class: SensorDeviceClass | None = SensorDeviceClass.TEMPERATURE

    def __init__(self,
                    coordinator: WaterHeaterCoordinator, # pylint: disable=unused-argument
                    device: WaterHeater, # pylint: disable=unused-argument
                    ) -> None:
        """ Class constructor """
        super().__init__(coordinator)
        self._device = device
        #self._attr_name = f"Water temp in upper position"
        self._attr_entity_registry_enabled_default = True
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-water-temp-upper-sensor"
        self._attr_native_value = "{}".format(self._device.temp_t5u)
        if self._device.unit_mode == UnitMode.CELCIUS:
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        elif self._device.unit_mode == UnitMode.FAHRENHEIT:
            self._attr_native_unit_of_measurement = UnitOfTemperature.FAHRENHEIT

    @property
    def device_info(self) -> DeviceInfo:
        """Get Device information."""
        return self._attr_device_info

    @property
    def icon(self) -> str | None:
        return "mdi:thermometer"

    @callback
    def _handle_coordinator_update(self) -> None:
        """ Handle updated data from the coordinator """
        if 'T5U' in self.coordinator.data.keys():
            _LOGGER.debug("[UPDATE] T5U:{}".format(self.coordinator.data['T5U']))
            self._attr_native_value = "{}".format(self.coordinator.data['T5U'])
        else:
            _LOGGER.exception('[UPDATE] error updating T5U value')
        self.async_write_ha_state()

class DiagT5LSensor(CoordinatorEntity, SensorEntity):
    # pylint: disable = too-many-instance-attributes
    """ Representation of a Sensor """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "water_temp_lower_pos"
    _attr_device_class: SensorDeviceClass | None = SensorDeviceClass.TEMPERATURE

    def __init__(self,
                    coordinator: WaterHeaterCoordinator, # pylint: disable=unused-argument
                    device: WaterHeater, # pylint: disable=unused-argument
                    ) -> None:
        """ Class constructor """
        super().__init__(coordinator)
        self._device = device
        #self._attr_name = f"Water temp in lower position"
        self._attr_entity_registry_enabled_default = True
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-water-temp-lower-sensor"
        self._attr_native_value = "{}".format(self._device.temp_t5l)
        if self._device.unit_mode == UnitMode.CELCIUS:
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        elif self._device.unit_mode == UnitMode.FAHRENHEIT:
            self._attr_native_unit_of_measurement = UnitOfTemperature.FAHRENHEIT

    @property
    def device_info(self) -> DeviceInfo:
        """Get Device information."""
        return self._attr_device_info

    @property
    def icon(self) -> str | None:
        return "mdi:thermometer"

    @callback
    def _handle_coordinator_update(self) -> None:
        """ Handle updated data from the coordinator """
        if 'T5L' in self.coordinator.data.keys():
            _LOGGER.debug("[UPDATE] T5L:{}".format(self.coordinator.data['T5L']))
            self._attr_native_value = "{}".format(self.coordinator.data['T5L'])
        else:
            _LOGGER.exception('[UPDATE] error updating T5L value')
        self.async_write_ha_state()

class DiagT3Sensor(CoordinatorEntity, SensorEntity):
    # pylint: disable = too-many-instance-attributes
    """ Representation of a Sensor """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "t3_temp"
    _attr_device_class: SensorDeviceClass | None = SensorDeviceClass.TEMPERATURE

    def __init__(self,
                    coordinator: WaterHeaterCoordinator, # pylint: disable=unused-argument
                    device: WaterHeater, # pylint: disable=unused-argument
                    ) -> None:
        """ Class constructor """
        super().__init__(coordinator)
        self._device = device
        #self._attr_name = f"Condenser temperature"
        self._attr_entity_registry_enabled_default = True
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-condenser-temp-sensor"
        self._attr_native_value = "{}".format(self._device.temp_t3)
        if self._device.unit_mode == UnitMode.CELCIUS:
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        elif self._device.unit_mode == UnitMode.FAHRENHEIT:
            self._attr_native_unit_of_measurement = UnitOfTemperature.FAHRENHEIT

    @property
    def device_info(self) -> DeviceInfo:
        """Get Device information."""
        return self._attr_device_info

    @property
    def icon(self) -> str | None:
        return "mdi:thermometer"

    @callback
    def _handle_coordinator_update(self) -> None:
        """ Handle updated data from the coordinator """
        if 'T3' in self.coordinator.data.keys():
            _LOGGER.debug("[UPDATE] T3:{}".format(self.coordinator.data['T3']))
            self._attr_native_value = "{}".format(self.coordinator.data['T3'])
        else:
            _LOGGER.exception('[UPDATE] error updating T3 value')
        self.async_write_ha_state()

class DiagT4Sensor(CoordinatorEntity, SensorEntity):
    # pylint: disable = too-many-instance-attributes
    """ Representation of a Sensor """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "t4_temp"
    _attr_device_class: SensorDeviceClass | None = SensorDeviceClass.TEMPERATURE

    def __init__(self,
                    coordinator: WaterHeaterCoordinator, # pylint: disable=unused-argument
                    device: WaterHeater, # pylint: disable=unused-argument
                    ) -> None:
        """ Class constructor """
        super().__init__(coordinator)
        self._device = device
        #self._attr_name = f"Outdoor ambient temperature"
        self._attr_entity_registry_enabled_default = True
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-outdoor-ambient-temp-sensor"
        self._attr_native_value = "{}".format(self._device.temp_t4)
        if self._device.unit_mode == UnitMode.CELCIUS:
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        elif self._device.unit_mode == UnitMode.FAHRENHEIT:
            self._attr_native_unit_of_measurement = UnitOfTemperature.FAHRENHEIT

    @property
    def device_info(self) -> DeviceInfo:
        """Get Device information."""
        return self._attr_device_info

    @property
    def icon(self) -> str | None:
        return "mdi:thermometer"

    @callback
    def _handle_coordinator_update(self) -> None:
        """ Handle updated data from the coordinator """
        if 'T4' in self.coordinator.data.keys():
            _LOGGER.debug("[UPDATE] T4:{}".format(self.coordinator.data['T4']))
            self._attr_native_value = "{}".format(self.coordinator.data['T4'])
        else:
            _LOGGER.exception('[UPDATE] error updating T4 value')
        self.async_write_ha_state()

class DiagTPSensor(CoordinatorEntity, SensorEntity):
    # pylint: disable = too-many-instance-attributes
    """ Representation of a Sensor """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "tp_temp"
    _attr_device_class: SensorDeviceClass | None = SensorDeviceClass.TEMPERATURE

    def __init__(self,
                    coordinator: WaterHeaterCoordinator, # pylint: disable=unused-argument
                    device: WaterHeater, # pylint: disable=unused-argument
                    ) -> None:
        """ Class constructor """
        super().__init__(coordinator)
        self._device = device
        #self._attr_name = f"Compressor exhaust temperature"
        self._attr_entity_registry_enabled_default = True
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-compressor-exhaust-temp-sensor"
        self._attr_native_value = "{}".format(self._device.temp_tp)
        if self._device.unit_mode == UnitMode.CELCIUS:
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        elif self._device.unit_mode == UnitMode.FAHRENHEIT:
            self._attr_native_unit_of_measurement = UnitOfTemperature.FAHRENHEIT

    @property
    def device_info(self) -> DeviceInfo:
        """Get Device information."""
        return self._attr_device_info

    @property
    def icon(self) -> str | None:
        return "mdi:thermometer"

    @callback
    def _handle_coordinator_update(self) -> None:
        """ Handle updated data from the coordinator """
        if 'TP' in self.coordinator.data.keys():
            _LOGGER.debug("[UPDATE] TP:{}".format(self.coordinator.data['TP']))
            self._attr_native_value = "{}".format(self.coordinator.data['TP'])
        else:
            _LOGGER.exception('[UPDATE] error updating TP value')
        self.async_write_ha_state()

class DiagTHSensor(CoordinatorEntity, SensorEntity):
    # pylint: disable = too-many-instance-attributes
    """ Representation of a Sensor """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "th_temp"
    _attr_device_class: SensorDeviceClass | None = SensorDeviceClass.TEMPERATURE

    def __init__(self,
                    coordinator: WaterHeaterCoordinator, # pylint: disable=unused-argument
                    device: WaterHeater, # pylint: disable=unused-argument
                    ) -> None:
        """ Class constructor """
        super().__init__(coordinator)
        self._device = device
        #self._attr_name = f"Suction temperature"
        self._attr_entity_registry_enabled_default = True
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-suction-temp-sensor"
        self._attr_native_value = "{}".format(self._device.temp_th)
        if self._device.unit_mode == UnitMode.CELCIUS:
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        elif self._device.unit_mode == UnitMode.FAHRENHEIT:
            self._attr_native_unit_of_measurement = UnitOfTemperature.FAHRENHEIT

    @property
    def device_info(self) -> DeviceInfo:
        """Get Device information."""
        return self._attr_device_info

    @property
    def icon(self) -> str | None:
        return "mdi:thermometer"

    @callback
    def _handle_coordinator_update(self) -> None:
        """ Handle updated data from the coordinator """
        if 'TH' in self.coordinator.data.keys():
            _LOGGER.debug("[UPDATE] TH:{}".format(self.coordinator.data['TH']))
            self._attr_native_value = "{}".format(self.coordinator.data['TH'])
        else:
            _LOGGER.exception('[UPDATE] error updating TH value')
        self.async_write_ha_state()

class DiagTXSensor(CoordinatorEntity, SensorEntity):
    # pylint: disable = too-many-instance-attributes
    """ Representation of a Sensor """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "tx_temp"
    _attr_device_class: SensorDeviceClass | None = SensorDeviceClass.TEMPERATURE

    def __init__(self,
                    coordinator: WaterHeaterCoordinator, # pylint: disable=unused-argument
                    device: WaterHeater, # pylint: disable=unused-argument
                    ) -> None:
        """ Class constructor """
        super().__init__(coordinator)
        self._device = device
        #self._attr_name = f"Display temperature"
        self._attr_entity_registry_enabled_default = True
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-display-temp-sensor"
        self._attr_native_value = "{}".format(self._device.temp_tx)
        if self._device.unit_mode == UnitMode.CELCIUS:
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        elif self._device.unit_mode == UnitMode.FAHRENHEIT:
            self._attr_native_unit_of_measurement = UnitOfTemperature.FAHRENHEIT

    @property
    def device_info(self) -> DeviceInfo:
        """Get Device information."""
        return self._attr_device_info

    @property
    def icon(self) -> str | None:
        return "mdi:thermometer"

    @callback
    def _handle_coordinator_update(self) -> None:
        """ Handle updated data from the coordinator """
        if 'TX' in self.coordinator.data.keys():
            _LOGGER.debug("[UPDATE] TX:{}".format(self.coordinator.data['TX']))
            self._attr_native_value = "{}".format(self.coordinator.data['TX'])
        else:
            _LOGGER.exception('[UPDATE] error updating TX value')
        self.async_write_ha_state()

class DiagCompTimeSensor(CoordinatorEntity, SensorEntity):
    # pylint: disable = too-many-instance-attributes
    """ Representation of a Sensor """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "comp_time"
    _attr_device_class: SensorDeviceClass | None = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement: str = UnitOfTime.SECONDS

    def __init__(self,
                    coordinator: WaterHeaterCoordinator, # pylint: disable=unused-argument
                    device: WaterHeater, # pylint: disable=unused-argument
                    ) -> None:
        """ Class constructor """
        super().__init__(coordinator)
        self._device = device
        #self._attr_name = f"Compressor running time"
        self._attr_entity_registry_enabled_default = True
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-compressor-running-time-sensor"
        self._attr_native_value = "{}".format(self._device.compressor_time)

    @property
    def device_info(self) -> DeviceInfo:
        """Get Device information."""
        return self._attr_device_info

    @property
    def icon(self) -> str | None:
        return "mdi:clock-outline"

    @callback
    def _handle_coordinator_update(self) -> None:
        """ Handle updated data from the coordinator """
        if 'comp_time' in self.coordinator.data.keys():
            _LOGGER.debug("[UPDATE] Compressor time:{}".format(self.coordinator.data['comp_time']))
            self._attr_native_value = "{}".format(self.coordinator.data['comp_time'])
        else:
            _LOGGER.exception('[UPDATE] error updating compressor time')
        self.async_write_ha_state()

class DiagModelSensor(SensorEntity):
    # pylint: disable = too-many-instance-attributes
    """ Representation of a Sensor """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "model"
    _attr_entity_category: EntityCategory | None = EntityCategory.DIAGNOSTIC

    def __init__(self,
                    device: WaterHeater, # pylint: disable=unused-argument
                    ) -> None:
        """ Class constructor """
        self._device = device
        #self._attr_name = f"Model"
        self._attr_entity_registry_enabled_default = True
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-model-sensor"
        self._attr_native_value = "{}".format(MODEL_TRANSLATION[int(self._device.model)])

    @property
    def device_info(self) -> DeviceInfo:
        """Get Device information."""
        return self._attr_device_info

    @property
    def icon(self) -> str | None:
        return "mdi:text-short"

    @property
    def should_poll(self) -> bool:
        """ Do not poll for those entities """
        return False

class DiagMainVersionSensor(SensorEntity):
    # pylint: disable = too-many-instance-attributes
    """ Representation of a Sensor """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "pcb_version"
    _attr_entity_category: EntityCategory | None = EntityCategory.DIAGNOSTIC

    def __init__(self,
                    device: WaterHeater, # pylint: disable=unused-argument
                    ) -> None:
        """ Class constructor """
        self._device = device
        #self._attr_name = f"PCB firmware version"
        self._attr_entity_registry_enabled_default = True
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-pcb-firmware-version-sensor"
        self._attr_native_value = "{}".format(self._device.firm_vers)

    @property
    def device_info(self) -> DeviceInfo:
        """Get Device information."""
        return self._attr_device_info

    @property
    def icon(self) -> str | None:
        return "mdi:text-short"

    @property
    def should_poll(self) -> bool:
        """ Do not poll for those entities """
        return False

class DiagWireVersionSensor(SensorEntity):
    # pylint: disable = too-many-instance-attributes
    """ Representation of a Sensor """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "wire_version"
    _attr_entity_category: EntityCategory | None = EntityCategory.DIAGNOSTIC

    def __init__(self,
                    device: WaterHeater, # pylint: disable=unused-argument
                    ) -> None:
        """ Class constructor """
        self._device = device
        #self._attr_name = f"Wire controller firmware version"
        self._attr_entity_registry_enabled_default = True
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-wire-firmware-version-sensor"
        self._attr_native_value = "{}".format(self._device.wire_vers)

    @property
    def device_info(self) -> DeviceInfo:
        """Get Device information."""
        return self._attr_device_info

    @property
    def icon(self) -> str | None:
        return "mdi:text-short"

    @property
    def should_poll(self) -> bool:
        """ Do not poll for those entities """
        return False

class CompCurrentSensor(CoordinatorEntity, SensorEntity):
    # pylint: disable = too-many-instance-attributes
    """ Representation of a Sensor """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "comp_current"
    _attr_device_class: SensorDeviceClass | None = SensorDeviceClass.CURRENT
    _attr_native_unit_of_measurement: str = UnitOfElectricCurrent.AMPERE

    def __init__(self,
                    coordinator: WaterHeaterCoordinator, # pylint: disable=unused-argument
                    device: WaterHeater, # pylint: disable=unused-argument
                    ) -> None:
        """ Class constructor """
        super().__init__(coordinator)
        self._device = device
        #self._attr_name = f"Compressor current"
        self._attr_entity_registry_enabled_default = True
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-compressor-current-sensor"
        self._attr_native_value = "{}".format(self._device.comp_current)

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
        if 'comp_current' in self.coordinator.data.keys():
            _LOGGER.debug("[UPDATE] compressor current:{}".format(self.coordinator.data['comp_current']))
            self._attr_native_value = "{}".format(self.coordinator.data['comp_current'])
        else:
            _LOGGER.exception('[UPDATE] error updating electric heater status')
        self.async_write_ha_state()

class FanSpeedSensor(CoordinatorEntity, SensorEntity):
    # pylint: disable = too-many-instance-attributes
    """ Representation of a Sensor """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "fan_speed"
    _attr_entity_category: EntityCategory | None = EntityCategory.DIAGNOSTIC

    def __init__(self,
                    coordinator: WaterHeaterCoordinator, # pylint: disable=unused-argument
                    device: WaterHeater, # pylint: disable=unused-argument
                    ) -> None:
        """ Class constructor """
        super().__init__(coordinator)
        self._device = device
        #self._attr_name = f"Fan speed"
        self._attr_entity_registry_enabled_default = True
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-fan-speed-sensor"
        self._attr_native_value = "{}".format(self._device.fan_speed)

    @property
    def device_info(self) -> DeviceInfo:
        """Get Device information."""
        return self._attr_device_info

    @property
    def icon(self) -> str | None:
        return "mdi:fan"

    @callback
    def _handle_coordinator_update(self) -> None:
        """ Handle updated data from the coordinator """
        if 'fan_speed' in self.coordinator.data.keys():
            _LOGGER.debug("[UPDATE] fan speed:{}".format(self.coordinator.data['fan_speed']))
            self._attr_native_value = "{}".format(self.coordinator.data['fan_speed'])
        else:
            _LOGGER.exception('[UPDATE] error updating fan speed status')
        self.async_write_ha_state()

class ErrCodeSensor(CoordinatorEntity, SensorEntity):
    # pylint: disable = too-many-instance-attributes
    """ Representation of a Sensor """
    _attr_has_entity_name: bool = True
    _attr_translation_key:str = "err_code"
    _attr_entity_category: EntityCategory | None = EntityCategory.DIAGNOSTIC

    def __init__(self,
                    coordinator: WaterHeaterCoordinator, # pylint: disable=unused-argument
                    device: WaterHeater, # pylint: disable=unused-argument
                    ) -> None:
        """ Class constructor """
        super().__init__(coordinator)
        self._device = device
        #self._attr_name = f"Error Code"
        self._attr_entity_registry_enabled_default = True
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-error-code-sensor"
        self._attr_native_value = "{}".format(self._device.err_code)

    @property
    def device_info(self) -> DeviceInfo:
        """Get Device information."""
        return self._attr_device_info

    @property
    def icon(self) -> str | None:
        return "mdi:alert-circle-outline"

    @callback
    def _handle_coordinator_update(self) -> None:
        """ Handle updated data from the coordinator """
        if 'err_code' in self.coordinator.data.keys():
            _LOGGER.debug("[UPDATE] Error code:{}".format(self.coordinator.data['err_code']))
            self._attr_native_value = "{}".format(self.coordinator.data['err_code'])
        else:
            _LOGGER.exception('[UPDATE] error updating error code')
        self.async_write_ha_state()