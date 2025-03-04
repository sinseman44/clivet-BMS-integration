""" for Coordinator integration. """
from __future__ import annotations
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant, callback
from homeassistant.util import Throttle
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    DOMAIN,
)

from .clivet.device import WaterHeater

_LOGGER = logging.getLogger(__name__)

class WaterHeaterCoordinator(DataUpdateCoordinator):
    """ clivet coordinator """

    def __init__(self,
                    hass: HomeAssistant, 
                    device: WaterHeater,
                ) -> None:
        """ Class constructor """
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name=DOMAIN,
            update_method=device.async_update,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=30),
        )