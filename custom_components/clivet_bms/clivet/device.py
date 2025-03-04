""" local API to manage system """ 

import re, sys, os
import logging as log
import asyncio

from homeassistant.helpers.entity import DeviceInfo
from ..const import DOMAIN

from . import const
from .operations import Operations, ModbusConnexionError

_LOGGER = log.getLogger(__name__)

class WaterHeater:
    ''' WaterHeater Device class '''

    #_rtu_port:str = ""
    #_rtu_addr:int = const.DEFAULT_ADDR
    #_rtu_baudrate:int = const.DEFAULT_BAUDRATE
    #_rtu_parity:str = const.DEFAULT_PARITY
    #_rtu_bytesize:int = const.DEFAULT_BYTESIZE
    #_rtu_stopbits:int = const.DEFAULT_STOPBITS
#
    #_tcp_port:int = const.DEFAULT_TCP_PORT
    #_tcp_addr:str = const.DEFAULT_TCP_ADDR
    #_tcp_modbus:int = const.DEFAULT_ADDR
    #_tcp_retries:int = const.DEFAULT_TCP_RETRIES
    #_tcp_reco_delay_min:float = const.DEFAULT_TCP_RECO_DELAY
    #_tcp_reco_delay_max:float = const.DEFAULT_TCP_RECO_DELAY_MAX
#
    #def __init__(self, 
    #            mode:str = "",
    #            name:str = "",
    #            timeout:int = 1,
    #            debug:bool = False, 
    #            choice:str = "",
    #            **kwargs
    #            ) -> None:
    #    ''' Class constructor '''
    #    self._mode = mode
    #    self._name = name
    #    self._debug = debug
    #    self._timeout = timeout
    #    self._choice = choice
    #    self.__dict__.update(kwargs)
    #    if self._mode == "Modbus RTU":
    #        self._rtu_port = kwargs.get('port', '')
    #        self._rtu_addr = kwargs.get('addr', const.DEFAULT_ADDR)
    #        self._rtu_baudrate = kwargs.get('baudrate', const.DEFAULT_BAUDRATE)
    #        self._rtu_parity = kwargs.get('parity', const.DEFAULT_PARITY)
    #        self._rtu_bytesize = kwargs.get('bytesize', const.DEFAULT_BYTESIZE)
    #        self._rtu_stopbits = kwargs.get('stopbits', const.DEFAULT_STOPBITS)
    #        self._client = Operations(mode=self._mode,
    #                                    timeout=self._timeout,
    #                                    debug=self._debug,
    #                                    port=self._rtu_port,
    #                                    addr=self._rtu_addr,
    #                                    baudrate=self._rtu_baudrate,
    #                                    parity=self._rtu_parity,
    #                                    bytesize=self._rtu_bytesize,
    #                                    stopbits=self._rtu_stopbits)
    #    elif self._mode == "Modbus TCP":
    #        self._tcp_port = kwargs.get('port', const.DEFAULT_TCP_PORT)
    #        self._tcp_addr = kwargs.get('addr', const.DEFAULT_TCP_ADDR)
    #        self._tcp_modbus = kwargs.get('modbus', const.DEFAULT_ADDR)
    #        self._tcp_retries = kwargs.get('retries', const.DEFAULT_TCP_RETRIES)
    #        self._tcp_reco_delay_min = kwargs.get('reco_delay_min', const.DEFAULT_TCP_RECO_DELAY)
    #        self._tcp_reco_delay_max = kwargs.get('reco_delay_max', const.DEFAULT_TCP_RECO_DELAY_MAX)
    #        self._client = Operations(mode=self._mode,
    #                                    timeout=self._timeout,
    #                                    debug=self._debug,
    #                                    addr=self._tcp_addr,
    #                                    port=self._tcp_port,
    #                                    modbus=self._tcp_modbus,
    #                                    retries=self._tcp_retries,
    #                                    reco_delay_min=self._tcp_reco_delay_min,
    #                                    reco_delay_max=self._tcp_reco_delay_max)
    #    else:
    #        raise InitialisationError('unknown mode ({})'.format(self._mode))
    #    self._power = const.PowerState.STATE_OFF
    #    self._target_temp:float = 0.0
    #    self._current_temp:float = 0.0
    #    self._model = const.Model.MODEL_190
    #    self._firm_vers = 1
    #    self._wire_controller_vers = 1
    #    self._unit_mode = const.UnitMode.CELCIUS
    #    self._desinfect = const.DisinfectFunc.OFF
    #    self._remoter_mode = const.RemoterMode.OFF
    #    self._remoter_signal = const.RemoterSignal.PANEL_CANNOT_WORK
    #    self._sg = const.SGCmd.OFF
    #    self._evu = const.EVUCmd.OFF
    #    self._solar = const.SolarSignal.SOLAR_PANEL_OFF
    #    self._operation_mode = const.OperatingMode.INVALID
    #    self._min_temp_ts:float = 0.0
    #    self._max_temp_ts:float = 0.0
    #    self._temp_t5l:float = 0.0
    #    self._temp_t5u:float = 0.0
    #    self._temp_t3:float = 0.0
    #    self._temp_t4:float = 0.0
    #    self._temp_tp:float = 0.0
    #    self._temp_th:float = 0.0
    #    self._temp_tx:float = 0.0
    #    self._compressor_time:int = 0
    #    self._compressor_current:int = 0
    #    self._wifi_status = const.WifiStatus.NOT_CONNECT
    #    self._defrost = const.DefrostMode.OFF
    #    self._solar_kit = const.SolarKitMode.OFF
    #    self._vacation = const.VacationMode.NOT_ACTIVE
    #    self._alarm = const.AlarmStatus.OFF
    #    self._solar_pump = const.SolarPanelWaterPumpStatus.OFF
    #    self._compressor = const.CompressorStatus.OFF
    #    self._elecheater = const.ElectricHeaterStatus.OFF
    #    self._fourwayvalve = const.FourWayValveStatus.OFF
    #    self._fan_speed:str = "OFF"

    def __init__(self, 
                    mode: str = "",
                    name: str = "",
                    timeout: int = 1,
                    debug: bool = False, 
                    choice: str = "",
                    **kwargs) -> None:
        ''' Class constructor '''

        self._mode = mode
        self._name = name
        self._debug = debug
        self._timeout = timeout
        self._choice = choice

        # Initialize connection settings
        if self._mode == "Modbus RTU":
            self._init_rtu(kwargs)
        elif self._mode == "Modbus TCP":
            self._init_tcp(kwargs)
        else:
            raise InitialisationError(f"Unknown mode ({self._mode})")

        # Initialize operational states
        self._initialize_states()

        _LOGGER.info(f"WaterHeater initialized in {self._mode} mode")

    def _init_rtu(self, kwargs: dict):
        """ Initialize RTU communication settings """
        self._rtu_port = kwargs.get('port', const.DEFAULT_ADDR)
        self._rtu_addr = kwargs.get('addr', const.DEFAULT_ADDR)
        self._rtu_baudrate = kwargs.get('baudrate', const.DEFAULT_BAUDRATE)
        self._rtu_parity = kwargs.get('parity', const.DEFAULT_PARITY)
        self._rtu_bytesize = kwargs.get('bytesize', const.DEFAULT_BYTESIZE)
        self._rtu_stopbits = kwargs.get('stopbits', const.DEFAULT_STOPBITS)

        self._client = Operations(
            mode=self._mode,
            timeout=self._timeout,
            debug=self._debug,
            port=self._rtu_port,
            addr=self._rtu_addr,
            baudrate=self._rtu_baudrate,
            parity=self._rtu_parity,
            bytesize=self._rtu_bytesize,
            stopbits=self._rtu_stopbits
        )

        _LOGGER.debug(f"RTU settings: Port={self._rtu_port}, Addr={self._rtu_addr}, Baudrate={self._rtu_baudrate}")

    def _init_tcp(self, kwargs: dict):
        """ Initialize TCP communication settings """
        self._tcp_port = kwargs.get('port', const.DEFAULT_TCP_PORT)
        self._tcp_addr = kwargs.get('addr', const.DEFAULT_TCP_ADDR)
        self._tcp_modbus = kwargs.get('modbus', const.DEFAULT_ADDR)
        self._tcp_retries = kwargs.get('retries', const.DEFAULT_TCP_RETRIES)
        self._tcp_reco_delay_min = kwargs.get('reco_delay_min', const.DEFAULT_TCP_RECO_DELAY)
        self._tcp_reco_delay_max = kwargs.get('reco_delay_max', const.DEFAULT_TCP_RECO_DELAY_MAX)

        self._client = Operations(
            mode=self._mode,
            timeout=self._timeout,
            debug=self._debug,
            addr=self._tcp_addr,
            port=self._tcp_port,
            modbus=self._tcp_modbus,
            retries=self._tcp_retries,
            reco_delay_min=self._tcp_reco_delay_min,
            reco_delay_max=self._tcp_reco_delay_max
        )

        _LOGGER.debug(f"TCP settings: Addr={self._tcp_addr}, Port={self._tcp_port}, Retries={self._tcp_retries}")

    def _initialize_states(self):
        """ Initialize water heater's operational states """
        self._power = const.PowerState.STATE_OFF
        self._target_temp: float = 0.0
        self._current_temp: float = 0.0
        self._model = const.Model.MODEL_190
        self._firm_vers = 1
        self._wire_controller_vers = 1
        self._unit_mode = const.UnitMode.CELCIUS
        self._desinfect = const.DisinfectFunc.OFF
        self._remoter_mode = const.RemoterMode.OFF
        self._remoter_signal = const.RemoterSignal.PANEL_CANNOT_WORK
        self._sg = const.SGCmd.OFF
        self._evu = const.EVUCmd.OFF
        self._solar = const.SolarSignal.SOLAR_PANEL_OFF
        self._operation_mode = const.OperatingMode.INVALID
        self._min_temp_ts: float = 0.0
        self._max_temp_ts: float = 0.0
        self._temp_t5l: float = 0.0
        self._temp_t5u: float = 0.0
        self._temp_t3: float = 0.0
        self._temp_t4: float = 0.0
        self._temp_tp: float = 0.0
        self._temp_th: float = 0.0
        self._temp_tx: float = 0.0
        self._compressor_time: int = 0
        self._compressor_current: int = 0
        self._wifi_status = const.WifiStatus.NOT_CONNECT
        self._defrost = const.DefrostMode.OFF
        self._solar_kit = const.SolarKitMode.OFF
        self._vacation = const.VacationMode.NOT_ACTIVE
        self._alarm = const.AlarmStatus.OFF
        self._solar_pump = const.SolarPanelWaterPumpStatus.OFF
        self._compressor = const.CompressorStatus.OFF
        self._elecheater = const.ElectricHeaterStatus.OFF
        self._fourwayvalve = const.FourWayValveStatus.OFF
        self._fan_speed: str = "OFF"
        self._err_code:str = ""

        _LOGGER.debug("Operational states initialized")

    async def async_connect(self) -> bool:
        ''' connect to the modbus serial server '''
        ret = True
        await self._client.async_connect()
        if not self.connected():
            ret = False
            raise ClientNotConnectedError("Client Modbus connexion error")
        return ret

    def connected(self) -> bool:
        ''' get modbus client status '''
        return self._client.connected

    def disconnect(self) -> None:
        ''' close the underlying socket connection '''
        self._client.disconnect()

    async def async_update(self) -> dict:
        ''' initial update Modbus values '''
        _ret:bool = True
        _vals:dict = {}
        _LOGGER.debug("Update Modbus values")
        _ret, _vals = await self._client.async_get_cmd_values()
        if not _ret:
            _LOGGER.error("Error retreiving modbus values")
            return {}
        
        self._power = _vals['power']
        #_vals['setting_mode']
        self._solar = _vals['solar']
        self._evu = _vals['evu']
        self._sg = _vals['sg']
        self._remoter_signal = _vals['remoterSignal']
        self._remoter_mode = _vals['remoterMode']
        self._desinfect = _vals['desinfect']
        self._unit_mode = _vals['unit']
        self._target_temp = _vals['target_temp']
        self._operation_mode = _vals['ope']
        self._temp_t5u = _vals['T5U']
        self._temp_t5l = _vals['T5L']
        self._temp_t3 = _vals['T3']
        self._temp_t4 = _vals['T4']
        self._temp_tp = _vals['TP']
        self._temp_th = _vals['TH']
        #_vals['PMV']
        self._compressor_current = _vals['comp_current']
        self._compressor = _vals['compressor']
        self._elecheater = _vals['elecHeater']
        self._fourwayvalve = _vals['valve']
        if _vals['fanLow'] == const.FanSpeedLowStatus.ON:
            self._fan_speed = 'LOW'
            _vals['fan_speed'] = 'LOW'
        elif _vals['fanMed'] == const.FanSpeedMediumStatus.ON:
            self._fan_speed = 'MEDIUM'
            _vals['fan_speed'] = 'MEDIUM'
        elif _vals['fanHigh'] == const.FanSpeedHighStatus.ON:
            self._fan_speed = 'HIGH'
            _vals['fan_speed'] = 'HIGH'
        else:
            self._fan_speed = 'OFF'
            _vals['fan_speed'] = 'OFF'
        self._solar_pump = _vals['solarPump']
        self._alarm = _vals['alarm']
        self._err_code = _vals['err_code']
        self._max_temp_ts = _vals['max_ts']
        self._min_temp_ts = _vals['min_ts']
        self._temp_tx = _vals['TX']
        self._vacation = _vals['vacation']
        self._solar_kit = _vals['solar_kit']
        self._defrost = _vals['defrost']
        self._wifi_status = _vals['wifi']
        self._compressor_time = _vals['comp_time']
        self._model = _vals['model']
        self._firm_vers = _vals['pcb_firm']
        self._wire_controller_vers = _vals['wire_firm']

        _LOGGER.debug("Update current temperature")
        _ret, _vals['cur_temp'] = await self.async_get_current_temp()
        if not _ret:
            _LOGGER.error("Error retreiving current temperature")
            return {}
        return _vals

    @property
    def device_info(self) -> DeviceInfo:
        """ Return a device description for device registry """
        return {
            "name": self._name,
            "manufacturer": "Clivet",
            "identifiers": {(DOMAIN, "{}-{}".format("Clivet", self._name))},
        }

    @property
    def name(self) -> str:
        ''' return name '''
        return self._name

    @property
    def debug(self) -> bool:
        ''' return Debug mode '''
        return self._debug

    @property
    def unit_mode(self) -> const.UnitMode:
        ''' return Unit mode '''
        return self._unit_mode

    @property
    def disinfect(self) -> const.DisinfectFunc:
        ''' return desinfect '''
        return self._desinfect

    @property
    def remoter(self) -> const.RemoterMode:
        ''' return remoter mode '''
        return self._remoter_mode
    
    @property
    def remoter_signal(self) -> const.RemoterSignal:
        ''' return remoter signal '''
        return self._remoter_signal

    @property
    def smart_grid(self) -> const.SGCmd:
        ''' return smart grid '''
        return self._sg

    @property
    def evu(self) -> const.EVUCmd:
        ''' return EVU '''
        return self._evu

    @property
    def solar_signal(self) -> const.SolarSignal:
        ''' return Solar signal '''
        return self._solar

    @property
    def err_code(self) -> str:
        ''' return last error code '''
        return self._err_code

    async def async_get_command_func(self) -> (bool, dict):
        ''' retreive command functions '''
        _cmd:dict = {}
        _ret:bool = False
        _ret, _cmd = await self._client.async_get_command_func()
        if not _ret:
            _LOGGER.error('Error retreiving command functions')
            return _ret, {}

        self._unit_mode = _cmd['unit']
        self._desinfect = _cmd['desinfect']
        self._remoter_mode = _cmd['remoterMode']
        self._remoter_signal = _cmd['remoterSignal']
        self._sg = _cmd['sg']
        self._evu = _cmd['evu']
        self._solar = _cmd['solar']

        return _ret, _cmd

    async def async_set_unit(self, unit:str) -> bool:
        ''' Set unit mode '''
        _ret:bool = False
        _new_unit:const.UnitMode = const.UnitMode.CELCIUS
        if not isinstance(unit, str):
            raise AssertionError('Input variable must be a string')
        if unit == 'fahrenheit':
            _ret = await self._client.async_set_unit(const.UnitMode.FAHRENHEIT)
            _new_unit = const.UnitMode.FAHRENHEIT
        elif unit == 'celcius':
            _ret = await self._client.async_set_unit(const.UnitMode.CELCIUS)
        else:
            raise AssertionError('unit must be "fahrenheit" or "celcius"')
        if not _ret:
            _LOGGER.error("Error setting {}".format(unit))
            raise UpdateValueError('Error setting/reseting unit mode') 
        self._unit_mode = _new_unit

        return _ret

    async def async_set_disinfect(self, state:const.DisinfectFunc) -> bool:
        ''' Set disinfect function '''
        _ret:bool = False
        if not isinstance(state, const.DisinfectFunc):
            raise AssertionError('Input variable must be a const.DisinfectFunc')
        _ret = await self._client.async_set_disinfect(state)
        if not _ret:
            _LOGGER.error("Error setting/reseting {}".format(state))
            raise UpdateValueError('Error setting/reseting disinfection') 
        self._desinfect = state

        return _ret

    async def async_set_smart_grid(self, state:const.SGCmd) -> bool:
        ''' Set SG function '''
        _ret:bool = False
        if not isinstance(state, const.SGCmd):
            raise AssertionError('Input variable must be a const.SGCmd')
        _ret = await self._client.async_set_smart_grid(state)
        if not _ret:
            _LOGGER.error("Error setting/reseting {}".format(state))
            raise UpdateValueError('Error setting/reseting smart grid') 
        self._sg = state

        return _ret

    async def async_set_solar_signal_evu(self, state:const.EVUCmd) -> bool:
        ''' Set EVU function '''
        _ret:bool = False
        if not isinstance(state, const.EVUCmd):
            raise AssertionError('Input variable must be a const.EVUCmd')
        _ret = await self._client.async_set_solar_signal_evu(state)
        if not _ret:
            _LOGGER.error("Error setting/reseting {}".format(state))
            raise UpdateValueError('Error setting/reseting solar signal EVU') 
        self._evu = state

        return _ret

    async def async_set_remoter(self, state:const.RemoterMode) -> bool:
        ''' Set Remoter mode function '''
        _ret:bool = False
        if not isinstance(state, const.RemoterMode):
            raise AssertionError('Input variable must be a const.RemoterMode')
        _ret = await self._client.async_set_remoter(state)
        if not _ret:
            _LOGGER.error("Error setting/reseting {}".format(state))
            raise UpdateValueError('Error setting/reseting remoter mode function') 
        self._remoter_mode = state

        return _ret

    @property
    def model(self) -> const.Model:
        ''' return model '''
        return self._model

    @property
    def firm_vers(self) -> int:
        ''' return main PCB firmware version '''
        return self._firm_vers

    @property
    def wire_vers(self) -> int:
        ''' return wire controller firmware version '''
        return self._wire_controller_vers

    @property
    def compressor_time(self) -> int:
        ''' return compressor running time '''
        return self._compressor_time

    async def async_set_debug(self,
                                val:bool,
                                ) -> None:
        ''' Set Debug mode '''
        if not isinstance(val, bool):
            raise AssertionError('Input variable must be a boolean')
        _LOGGER.debug("set debug mode : {}".format(val))
        ret = await self._client.async_set_debug(val)
        if not ret:
            _LOGGER.error("[DEBUG] Error setting/reseting {}".format(val))
            raise UpdateValueError('Error setting/reseting debug mode') 
        self._debug = val

    @property
    def wifi_status(self) -> const.WifiStatus:
        ''' return wifi connection status '''
        return self._wifi_status

    @property
    def defrost_status(self) -> const.DefrostMode:
        ''' return defrost status '''
        return self._defrost

    @property
    def solar_kit_status(self) -> const.SolarKitMode:
        ''' return solar kit status '''
        return self._solar_kit

    @property
    def vacation_status(self) -> const.VacationMode:
        ''' return vacation mode '''
        return self._vacation

    async def async_get_misc(self) -> (bool, dict):
        ''' Get auxiliary status '''
        misc_dict:dict = {}
        ret, misc_dict = await self._client.async_get_misc()
        if not ret:
            _LOGGER.error("Error retreiving misc registers")
            return False, misc_dict
        self._model = misc_dict['model']
        self._firm_vers = misc_dict['pcb_firm']
        self._wire_controller_vers = misc_dict['wire_firm']
        self._compressor_time = misc_dict['comp_time']
        self._wifi_status = misc_dict['wifi']
        self._defrost = misc_dict['defrost']
        self._solar_kit = misc_dict['solar_kit']
        self._vacation = misc_dict['vacation']
        return True, misc_dict

    @property
    def alarm(self) -> const.AlarmStatus:
        ''' return alarm '''
        return self._alarm

    @property
    def solar_pump(self) -> const.SolarPanelWaterPumpStatus:
        ''' return solar panel water pump '''
        return self._solar_pump

    @property
    def compressor(self) -> const.CompressorStatus:
        ''' return compressor '''
        return self._compressor

    @property
    def elecheater(self) -> const.ElectricHeaterStatus:
        ''' return electric heater '''
        return self._elecheater

    @property
    def fourwayvalve(self) -> const.FourWayValveStatus:
        ''' return 4 way valve '''
        return self._fourwayvalve

    @property
    def fan_speed(self) -> str:
        ''' return fan speed '''
        return self._fan_speed

    async def async_get_load_output(self) -> (bool, dict):
        ''' Get load output '''
        load_dict:dict = {}
        ret, load_dict = await self._client.async_get_load_output()
        if not ret:
            _LOGGER.error("Error retreiving load output register")
            return False, load_dict

        self._compressor = load_dict['compressor']
        self._elecheater = load_dict['elecHeater']
        self._fourwayvalve = load_dict['valve']
        if load_dict['fanLow'] == const.FanSpeedLowStatus.ON:
            self._fan_speed = 'LOW'
            load_dict['fan_speed'] = 'LOW'
        elif load_dict['fanMed'] == const.FanSpeedMediumStatus.ON:
            self._fan_speed = 'MEDIUM'
            load_dict['fan_speed'] = 'MEDIUM'
        elif load_dict['fanHigh'] == const.FanSpeedHighStatus.ON:
            self._fan_speed = 'HIGH'
            load_dict['fan_speed'] = 'HIGH'
        else:
            self._fan_speed = 'OFF'
            load_dict['fan_speed'] = 'OFF'
        self._solar_pump = load_dict['solarPump']
        self._alarm = load_dict['alarm']
        return True, load_dict

    @property
    def current_temp(self) -> float:
        ''' Get current temp '''
        return self._current_temp

    async def async_get_current_temp(self) -> (bool, float):
        """ get current temp (T5U and T5L) """
        _ret:bool = False
        # Retreive temp value
        _ret, self._current_temp = await self._client.async_get_current_temp(unit = self._unit_mode, choice = self._choice)
        if not _ret:
            _LOGGER.error("[GET CURRENT TEMP] Error reading current temp")
            return _ret, 0.0

        _LOGGER.debug("[GET CURRENT TEMP] Temp:{} (Unit Mode: {})".format(self._current_temp, self._unit_mode))
        return _ret, self._current_temp

    @property
    def target_temp(self) -> float:
        ''' Get target temp Ts '''
        return self._target_temp

    async def async_get_target_temp(self) -> (bool, float):
        """ get target temp Ts """
        ret, self._target_temp = await self._client.async_get_target_temp(unit = self._unit_mode)
        if not ret:
            _LOGGER.error("Error reading target temp")
            return ret, 0.0

        _LOGGER.debug("[GET TARGET TEMP] Temp:{} (Unit Mode: {})".format(self._target_temp, self._unit_mode))
        return ret, self._target_temp

    async def async_set_target_temp(self,
                                    temp:float,
                                    ) -> bool:
        """ set target temp for water heater """
        _ret:bool = False
        _ret = await self._client.async_set_target_temp(unit = self._unit_mode, val = temp)
        if not _ret:
            _LOGGER.error("Error writing target temp ({})".format(temp))
            return _ret
        self._target_temp = temp
        return _ret

    @property
    def power(self) -> const.PowerState:
        """ Return power state """
        return self._power

    async def async_set_off(self) -> bool:
        """ set system off """
        ret = await self._client.async_set_power_status(opt = const.PowerState.STATE_OFF)
        if not ret:
            _LOGGER.error("Error writing area state (STATE_OFF)")
            return False
        self._power = const.PowerState.STATE_OFF
        return True
    
    async def async_set_on(self) -> bool:
        """ set system on """
        ret = await self._client.async_set_power_status(opt = const.PowerState.STATE_ON)
        if not ret:
            _LOGGER.error("Error writing area state (STATE_ON)")
            return False
        self._power = const.PowerState.STATE_ON
        return True

    @property
    def operation_mode(self) -> const.OperatingMode:
        """ get operation mode """
        return self._operation_mode

    async def async_get_operation_mode(self) -> (bool, const.OperatingMode):
        """ get operation mode """
        ret, self._operation_mode = await self._client.async_get_operating_mode()
        if not ret:
            _LOGGER.error("Error retreiving operation mode")
            return False, self._operation_mode
        return True, self._operation_mode

    async def async_set_setting_mode(self,
                                    mode:const.OperatingMode,
                                    ) -> bool:
        """ set operation mode """
        ret = await self._client.async_set_setting_mode(opt = mode)
        if not ret:
            _LOGGER.error("Error setting operation mode")
            return False
        self._operation_mode = mode
        return True

    @property
    def min_temp_ts(self) -> float:
        """ return minimum of Ts """
        return self._min_temp_ts

    async def async_get_min_temp_ts(self) -> (bool, float):
        """ get minimum of Ts """
        ret, self._min_temp_ts = await self._client.async_get_min_ts_temp(unit = self._unit_mode)
        if not ret:
            _LOGGER.error("Error retreiving minimum temperature of Ts")
            return False, 0.0
        _LOGGER.debug("[GET MIN TEMP TS] val: {}".format(self._min_temp_ts))
        return True, self._min_temp_ts

    @property
    def max_temp_ts(self) -> float:
        """ return maximum of Ts """
        return self._max_temp_ts

    async def async_get_max_temp_ts(self) -> (bool, float):
        """ get maximum of Ts """
        ret, self._max_temp_ts = await self._client.async_get_max_ts_temp(unit = self._unit_mode)
        if not ret:
            _LOGGER.error("Error retreiving maximum temperature of Ts")
            return False, 0.0
        _LOGGER.debug("[GET MAX TEMP TS] val: {}".format(self._max_temp_ts))
        return True, self._max_temp_ts

    async def async_get_min_max_temps_ts(self) -> (bool, float, float):
        """ get minimum of Ts """
        ret, self._min_temp_ts, self._max_temp_ts = await self._client.async_get_min_max_ts_temps()
        if not ret:
            _LOGGER.error("Error retreiving minimum and maximum temperatures of Ts")
            return False, 0.0, 0.0
        return True, self._min_temp_ts, self._max_temp_ts

    @property
    def temp_t5u(self) -> float:
        """ return water temperature in upper position of water tank """
        return self._temp_t5u

    @property
    def temp_t5l(self) -> float:
        """ return water temperature in lower position of water tank """
        return self._temp_t5l

    @property
    def temp_t3(self) -> float:
        """ return condenser temperature """
        return self._temp_t3

    @property
    def temp_t4(self) -> float:
        """ return outdoor ambient temperature """
        return self._temp_t4

    @property
    def temp_tp(self) -> float:
        """ return compressor exhaust temperature """
        return self._temp_tp

    @property
    def temp_th(self) -> float:
        """ return suction temperature """
        return self._temp_th

    async def async_get_temps(self) -> (bool, dict):
        """ get temperatures T5U, T5L, T3, T4, TP and TH """
        temps:dict = {}
        ret, temps = await self._client.async_get_temps(unit = self._unit_mode)
        if not ret:
            _LOGGER.error("Error retreiving temps")
            return False, {}
        _LOGGER.debug("[GET TEMPS] vals:{}".format(temps))
        self._temp_t5u = temps['T5U']
        self._temp_t5l = temps['T5L']
        self._temp_t3 = temps['T3']
        self._temp_t4 = temps['T4']
        self._temp_tp = temps['TP']
        self._temp_th = temps['TH']
        return True, temps

    @property
    def temp_tx(self) -> float:
        """ return display temperature """
        return self._temp_th

    async def async_get_tx_temp(self) -> (bool, float):
        """ get display temperture """
        ret, self._temp_tx = await self._client.async_get_display_temp(unit = self._unit_mode)
        if not ret:
            _LOGGER.error("Error retreiving display temperature")
            return False, 0.0
        _LOGGER.debug("[GET DISPLAY TEMP] val: {}".format(self._temp_tx))
        return True, self._temp_tx

    @property
    def comp_current(self) -> int:
        """ return compressor current """
        return self._compressor_current

    async def async_get_compressor_current(self) -> (bool, int):
        """ get compressor current """
        ret, self._compressor_current = await self._client.async_get_compressor_current()
        if not ret:
            _LOGGER.error("Error retreiving compressor current")
            return False, 0
        _LOGGER.debug("[GET COMP CURRENT] val: {}".format(self._compressor_current))
        return True, self._compressor_current

    def __repr__(self) -> str:
        ''' repr method '''
        return repr('System()')
#        return repr('System(Global Mode:{}, Efficiency:{}, State:{})'.format(
#                        self._global_mode,
#                        self._efficiency,
#                        self._sys_state))

class NumUnitError(Exception):
    ''' user defined exception '''

    def __init__(self,
                    msg:str = "") -> None:
        ''' Class Constructor '''
        self._msg = msg

    def __str__(self):
        ''' print the message '''
        return self._msg

class OrderTempError(Exception):
    ''' user defined exception '''

    def __init__(self,
                    msg:str = "") -> None:
        ''' Class Constructor '''
        self._msg = msg

    def __str__(self):
        ''' print the message '''
        return self._msg

class ClientNotConnectedError(Exception):
    ''' user defined exception '''

    def __init__(self,
                    msg:str = "") -> None:
        ''' Class Constructor '''
        self._msg = msg

    def __str__(self):
        ''' print the message '''
        return self._msg

class UpdateValueError(Exception):
    ''' user defined exception '''

    def __init__(self,
                    msg:str = "") -> None:
        ''' Class Constructor '''
        self._msg = msg

    def __str__(self):
        ''' print the message '''
        return self._msg

class InitialisationError(Exception):
    ''' user defined exception '''

    def __init__(self,
                    msg:str = "") -> None:
        ''' Class Constructor '''
        self._msg = msg

    def __str__(self):
        ''' print the message '''
        return self._msg
