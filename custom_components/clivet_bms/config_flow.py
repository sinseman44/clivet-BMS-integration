""" Le Config Flow du chauffe-eau """

import logging
import voluptuous as vol

from homeassistant import exceptions
import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigFlow
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import CONF_BASE
from .const import DOMAIN, CONF_NAME

from .clivet.operations import Operations
from .clivet.const import (
    DEFAULT_MODE,
    DEFAULT_TCP_ADDR,
    DEFAULT_TCP_PORT,
    DEFAULT_TCP_RETRIES,
    DEFAULT_TCP_RECO_DELAY,
    DEFAULT_TCP_RECO_DELAY_MAX,
    DEFAULT_ADDR,
    DEFAULT_BAUDRATE,
    DEFAULT_PARITY,
    DEFAULT_STOPBITS,
    DEFAULT_BYTESIZE
)

_LOGGER = logging.getLogger(__name__)

class WaterHeaterConfigFlow(ConfigFlow, domain=DOMAIN):
    """ La classe qui implémente le config flow notre DOMAIN. 
        Elle doit dériver de FlowHandler
    """

    # La version de notre configFlow va permettre de migrer les entités
    # vers une version plus récente en cas de changement
    VERSION = 1
    # le dictionnaire qui va recevoir tous les user_input. On le vide au démarrage
    _user_inputs: dict = {}
    _conn = None

    async def async_step_user(self,
                                user_input: dict | None = None) -> FlowResult:
        """ Gestion de l'étape 'user'.
            Point d'entrée du configFlow. Cette méthode est appelée 2 fois:
            1. 1ere fois sans user_input -> Affichage du formulaire de configuration
            2. 2eme fois avec les données saisies par l'utilisateur dans user_input -> Sauvegarde des données saisies 
        """
        errors = {}
        user_form = vol.Schema( #pylint: disable=invalid-name
            {
                vol.Required("Mode", default=str(DEFAULT_MODE)): vol.In(["Modbus TCP", "Modbus RTU"])
            }
        )

        if user_input:
            self._user_inputs.update(user_input)
            if user_input["Mode"] == "Modbus RTU":
                # go to next step
                return await self.async_step_rtu()
            elif user_input["Mode"] == "Modbus TCP":
                # go to next step
                return await self.async_step_tcp()
            else:
                _LOGGER.warning("no choice :p")

        # first call or error
        return self.async_show_form(step_id="user", 
                                    data_schema=user_form,
                                    errors=errors)

    async def async_step_tcp(self, 
                            user_input: dict | None = None) -> FlowResult:
        """ Gestion de l'étape 'tcp'.
            Cette méthode est appelée 2 fois:
            1. 1ere fois sans user_input -> Affichage du formulaire de configuration
            2. 2eme fois avec les données saisies par l'utilisateur dans user_input -> Sauvegarde des données saisies 
        """
        errors = {}
        tcp_form = vol.Schema( #pylint: disable=invalid-name
            {
                vol.Required("Name", default="clivet"): vol.Coerce(str),
                vol.Required("Modbus", default=DEFAULT_ADDR): vol.Coerce(int),
                vol.Required("Address", default=DEFAULT_TCP_ADDR): vol.Coerce(str),
                vol.Required("Port", default=DEFAULT_TCP_PORT): vol.Coerce(int),
                vol.Required("Retries", default=DEFAULT_TCP_RETRIES): vol.Coerce(int),
                vol.Required("Reconnect_delay_min", default=DEFAULT_TCP_RECO_DELAY): vol.Coerce(float),
                vol.Required("Reconnect_delay_max", default=DEFAULT_TCP_RECO_DELAY_MAX): vol.Coerce(float),
                vol.Required("Timeout", default=5): vol.Coerce(int),
                vol.Optional("Debug", default=False): cv.boolean
            }
        )
        if user_input:
            _LOGGER.debug("[config_flow|tcp] values received: {}".format(user_input))
            self._user_inputs.update(user_input)
            self._conn = Operations(mode="Modbus TCP",
                                    timeout=self._user_inputs["Timeout"],
                                    debug=self._user_inputs["Debug"],
                                    addr=self._user_inputs["Address"],
                                    port=self._user_inputs["Port"],
                                    modbus=self._user_inputs["Modbus"],
                                    retries=self._user_inputs["Retries"],
                                    reco_delay_min=self._user_inputs["Reconnect_delay_min"],
                                    reco_delay_max=self._user_inputs["Reconnect_delay_max"])
            try:
                await self._conn.async_connect()
                if not self._conn.connected():
                    raise CannotConnectError(reason="Client Modbus TCP not connected")
                _LOGGER.debug("test communication with water heater system")
                ret, _ = await self._conn.async_get_firmware_version()
                if not ret:
                    self._conn.disconnect()
                    raise CannotConnectError(reason="Communication error")
                self._conn.disconnect()

                # go to next step
                return await self.async_step_temp()

            except CannotConnectError:
                _LOGGER.exception("Cannot connect to water heater system")
                errors[CONF_BASE] = "cannot_connect"
            except Exception as e:
                _LOGGER.exception("Config Flow generic error")

        # first call or error
        return self.async_show_form(step_id="tcp", 
                                    data_schema=tcp_form,
                                    errors=errors)

    async def async_step_rtu(self, 
                            user_input: dict | None = None) -> FlowResult:
        """ Gestion de l'étape 'rtu'.
            Cette méthode est appelée 2 fois:
            1. 1ere fois sans user_input -> Affichage du formulaire de configuration
            2. 2eme fois avec les données saisies par l'utilisateur dans user_input -> Sauvegarde des données saisies 
        """
        errors = {}
        rtu_form = vol.Schema( #pylint: disable=invalid-name
            {
                vol.Required("Name", default="clivet"): vol.Coerce(str),
                vol.Required("Device", default="/dev/ttyUSB0"): vol.Coerce(str),
                vol.Required("Address", default=DEFAULT_ADDR): vol.Coerce(int),
                vol.Required("Baudrate", default=str(DEFAULT_BAUDRATE)): vol.In(["9600", "19200"]),
                vol.Required("Sizebyte", default=DEFAULT_BYTESIZE): vol.Coerce(int),
                vol.Required("Parity", default="NONE"): vol.In(["EVEN", "NONE"]),
                vol.Required("Stopbits", default=DEFAULT_STOPBITS): vol.Coerce(int),
                vol.Required("Timeout", default=5): vol.Coerce(int),
                vol.Optional("Debug", default=False): cv.boolean
            }
        )

        if user_input:
            _LOGGER.debug("[config_flow|rtu] values received: {}".format(user_input))
            # Second call; On memorise les données dans le dictionnaire
            self._user_inputs.update(user_input)
            self._conn = Operations(mode="Modbus RTU",
                                    timeout=self._user_inputs["Timeout"],
                                    debug=self._user_inputs["Debug"],
                                    port=self._user_inputs["Device"],
                                    addr=self._user_inputs["Address"],
                                    baudrate=int(self._user_inputs["Baudrate"]),
                                    parity=self._user_inputs["Parity"][0],
                                    stopbits=self._user_inputs["Stopbits"],
                                    bytesize=self._user_inputs["Sizebyte"])
            try:
                await self._conn.async_connect()
                if not self._conn.connected():
                    raise CannotConnectError(reason="Client Modbus RTU not connected")
                #_LOGGER.debug("test communication with clivet system")
                ret, _ = await self._conn.async_get_firmware_version()
                if not ret:
                    self._conn.disconnect()
                    raise CannotConnectError(reason="Communication error")
                self._conn.disconnect()

                # go to next step
                return await self.async_step_temp()

            except CannotConnectError:
                _LOGGER.exception("Cannot connect to water heater system")
                errors[CONF_BASE] = "cannot_connect"
            except Exception as e:
                _LOGGER.exception("Config Flow generic error")

        # first call or error
        return self.async_show_form(step_id="rtu", 
                                    data_schema=rtu_form,
                                    errors=errors)

    async def async_step_temp(self, 
                                user_input: dict | None = None) -> FlowResult:
        """ Gestion de l'étape 'temperature'.
            Cette méthode est appelée 2 fois:
            1. 1ere fois sans user_input -> Affichage du formulaire de configuration
            2. 2eme fois avec les données saisies par l'utilisateur dans user_input -> Sauvegarde des données saisies 
        """
        errors = {}
        temp_form = vol.Schema({ #pylint: disable=invalid-name
            vol.Required("Choice",
                        default=str("Maximum")): vol.In(["Maximum", "Moyenne", "Minimum"])
        })

        if user_input:
            self._user_inputs.update(user_input)
            # Create entities
            return self.async_create_entry(title=CONF_NAME,
                                            data=self._user_inputs)

        # first call or error
        return self.async_show_form(step_id="temp", 
                                    data_schema=temp_form,
                                    errors=errors)

class KnownError(exceptions.HomeAssistantError):
    """ Base class for errors known to this config flow
        [error_name] is the value passed to [errors] in async_show_form, which should match
        a key under "errors" in string.json

        [applies_to_field] is the name of the field name that contains the error (for async_show_form)
        if the field doesn't exist in the form, CONF_BASE will be used instead.
    """
    error_name = "unknown_error"
    applies_to_field = CONF_BASE

    def __init__(self, *args: object, **kwargs: dict[str, str]) -> None:
        super().__init__(*args)
        self._extra_info = kwargs

    def get_errors_and_placeholders(self, schema):
        """ Return dicts of errors and description_placeholders for adding to async_show_form """
        key = self.applies_to_field
        if key not in {k.schema for k in schema}:
            key = CONF_BASE
        return ({key: self.error_name}, self._extra_info or {})

class CannotConnectError(KnownError):
    """ Error to indicate we cannot connect """
    error_name = "cannot_connect"