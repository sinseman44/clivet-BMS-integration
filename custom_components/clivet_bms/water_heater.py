""" for Water Heater integration. """
# https://github.com/home-assistant/core/tree/master/homeassistant/components/water_heater

from __future__ import annotations
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant, callback
from homeassistant.util import Throttle
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.water_heater import (
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
    ConfigEntry,
)

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from homeassistant.components.water_heater.const import (
    STATE_ECO,
    STATE_ELECTRIC,
    STATE_PERFORMANCE,
    STATE_HIGH_DEMAND,
    STATE_HEAT_PUMP
)

from .const import (
    DOMAIN,
    SUPPORTED_OPE_LIST,
    OPE_TRANSLATION,
)

from .coordinator import WaterHeaterCoordinator

from homeassistant.const import (
    ATTR_TEMPERATURE,
    PRECISION_TENTHS,
    PRECISION_WHOLE,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_OFF,
    STATE_ON,
    UnitOfTemperature,
)

from .clivet.device import WaterHeater
from .clivet.const import (
    MIN_C_TEMP,
    MAX_C_TEMP,
    MIN_F_TEMP,
    MAX_F_TEMP,
    OperatingMode,
    PowerState,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant,
                            entry: ConfigEntry,
                            async_add_entities: AddEntitiesCallback
                            ) -> None:
    """Setup switch entries"""

    entities = []
    coordinator = hass.data[DOMAIN]["coordinator"]
    device = hass.data[DOMAIN]["device"]

    entities.append(ClivetWaterHeaterEntity(coordinator, device))
    async_add_entities(entities)

class ClivetWaterHeaterEntity(CoordinatorEntity, WaterHeaterEntity):
    """ Reperesentation of a water heater entity """
    # pylint: disable = too-many-instance-attributes

    _attr_current_operation: str | None = None
    _attr_current_temperature: float | None = 0.0
    _attr_is_away_mode_on: bool | None = False
    _attr_max_temp: float = MAX_C_TEMP
    _attr_min_temp: float = MIN_C_TEMP
    _attr_operation_list: list[str] | None = SUPPORTED_OPE_LIST
    _attr_precision: float = PRECISION_TENTHS
    _attr_state: None = STATE_HEAT_PUMP
    _attr_supported_features: WaterHeaterEntityFeature = WaterHeaterEntityFeature(WaterHeaterEntityFeature.TARGET_TEMPERATURE | 
                                                                                WaterHeaterEntityFeature.OPERATION_MODE |
                                                                                WaterHeaterEntityFeature.AWAY_MODE |
                                                                                WaterHeaterEntityFeature.ON_OFF)
    _attr_target_temperature_high: float | None = MAX_C_TEMP
    _attr_target_temperature_low: float | None = MIN_C_TEMP
    _attr_target_temperature: float | None = 0.0
    _attr_target_temperature_step: float | None = 1.0
    _attr_temperature_unit: str = UnitOfTemperature.CELSIUS

    def __init__(self,
                coordinator: WaterHeaterCoordinator, # pylint: disable=unused-argument
                device: WaterHeater, # pylint: disable=unused-argument
                ) -> None:
        """ Class constructor """
        super().__init__(coordinator)
        self._device = device
        self._attr_name = f"{self._device.name}"
        self._attr_device_info = self._device.device_info
        self._attr_unique_id = f"{DOMAIN}-{self._device.name}-water-heater"
        self._attr_current_temperature = self._device.current_temp
        self._attr_target_temperature = self._device.target_temp
        self._attr_current_operation = OPE_TRANSLATION[int(self._device.operation_mode)]

    async def async_set_temperature(self,
                                    **kwargs,
                                    ) -> None:
        """ set new target temperature """
        _LOGGER.debug("[Water Heater] set target temp - kwargs: {}".format(kwargs))
        if "temperature" in kwargs:
            target_temp = kwargs.get("temperature")
            ret = await self._device.async_set_target_temp(temp = target_temp)
            if not ret:
                _LOGGER.error("[Water Heater] Error sending target temperature: {}".format(target_temp))
        else:
            _LOGGER.exception("[Water Heater] Target temperature not defined")
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, 
                             **kwargs: Any
                            ) -> None:
        """ Turn the entity on """
        _LOGGER.debug("[Water Heater] turn on - kwargs: {}".format(kwargs))
        ret = await self._device.async_set_on()
        if not ret:
            _LOGGER.exception("[Water Heater] Error setting on")
        await self.coordinator.async_request_refresh()
        
    async def async_turn_off(self, 
                             **kwargs: Any
                            ) -> None:
        """ Turn the entity off """
        _LOGGER.debug("[Water Heater] turn off - kwargs: {}".format(kwargs))
        ret = await self._device.async_set_off()
        if not ret:
            _LOGGER.exception("[Water Heater] Error setting off")
        await self.coordinator.async_request_refresh()

    async def async_set_operation_mode(self, 
                                        operation_mode: str
                                        ) -> None:
        """Set new target operation mode."""
        _LOGGER.debug("[Water Heater] set operating mode: {}".format(operation_mode))
        for k,v in OPE_TRANSLATION.items():
            if v == operation_mode:
                opt = k
                break
        ret = await self._device.async_set_setting_mode(mode = OperatingMode(opt))
        if not ret:
            _LOGGER.exception("Error setting new operating mode")
        await self.coordinator.async_request_refresh()

    async def async_turn_away_mode_on(self) -> None:
        """Turn away (vacation) mode on."""
        _LOGGER.debug("[Water Heater] Turn away (vacation) mode on")
        await self.coordinator.async_request_refresh()

    async def async_turn_away_mode_off(self) -> None:
        """Turn away (vacation) mode off."""
        _LOGGER.debug("[Water Heater] Turn away (vacation) mode off")
        await self.coordinator.async_request_refresh()

    @property
    def target_temperature(self) -> int:
        """ Return the temperature we try to reach. """
        return self._device.target_temp

    @property
    def min_temp(self):
        """ Return the minimum temperature. """
        return self._device.min_temp_ts

    @property
    def max_temp(self):
        """ Return the maximum temperature. """
        return self._device.max_temp_ts

    @callback
    def _handle_coordinator_update(self) -> None:
        """ Handle updated data from the coordinator """
        if 'cur_temp' and 'target_temp' and 'ope' and 'power' in self.coordinator.data.keys():
            _LOGGER.debug("[Water Heater] (UPDATE) temp: {} - target: {} - ope mode: {} - power: {}".format(
                self.coordinator.data['cur_temp'],
                self.coordinator.data['target_temp'],
                self.coordinator.data['ope'],
                self.coordinator.data['power']))
            self._attr_current_temperature = self.coordinator.data['cur_temp']
            self._attr_target_temperature = self.coordinator.data['target_temp']
            self._attr_current_operation = OPE_TRANSLATION[int(self.coordinator.data['ope'])]
            if self.coordinator.data['power'] == PowerState.STATE_OFF:
                self.__attr_state = STATE_OFF
            elif self.coordinator.data['power'] == PowerState.STATE_ON:
                self.__attr_state = STATE_ON
        else:
            _LOGGER.exception('[UPDATE] error updating water heater values')
        self.async_write_ha_state()
