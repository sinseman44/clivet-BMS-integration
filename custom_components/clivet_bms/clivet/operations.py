""" local API to communicate with Water Heater Modbus RTU/TCP client """

import re, sys, os
import logging as log

import asyncio

from pymodbus import pymodbus_apply_logging_config
from pymodbus.client import AsyncModbusSerialClient as ModbusClient
from pymodbus.client import AsyncModbusTcpClient as ModbusTcpClient
from pymodbus.exceptions import ModbusException
from pymodbus.pdu import ExceptionResponse
from pymodbus.framer.rtu import FramerRTU

from . import const

_LOGGER = log.getLogger(__name__)

class Operations:
    ''' Water Heater Modbus operations class '''

    _rtu_port:str = ""
    _rtu_addr:int = const.DEFAULT_ADDR
    _rtu_baudrate = const.DEFAULT_BAUDRATE
    _rtu_parity = const.DEFAULT_PARITY
    _rtu_bytesize = const.DEFAULT_BYTESIZE
    _rtu_stopbits = const.DEFAULT_STOPBITS
    _tcp_port:int = const.DEFAULT_TCP_PORT
    _tcp_addr:str = const.DEFAULT_TCP_ADDR
    _tcp_modbus:int=const.DEFAULT_ADDR
    _tcp_retries:int=const.DEFAULT_TCP_RETRIES
    _tcp_reco_delay_min:float=const.DEFAULT_TCP_RECO_DELAY
    _tcp_reco_delay_max:float=const.DEFAULT_TCP_RECO_DELAY_MAX
    _lock = asyncio.Lock()

    def __init__(self, mode:str, timeout:int, debug:bool=False, **kwargs) -> None:
        ''' Class constructor '''
        self._mode = mode
        self._timeout = timeout
        self._debug = debug
        self.__dict__.update(kwargs)
        _LOGGER.debug("[OPERATION] dict: {}".format(self.__dict__))
        if self._mode == 'Modbus RTU':
            self._addr = kwargs.get('addr', const.DEFAULT_ADDR)
            self._rtu_port = kwargs.get('port', "")
            self._rtu_baudrate = kwargs.get('baudrate', const.DEFAULT_BAUDRATE)
            self._rtu_parity = kwargs.get('parity', const.DEFAULT_PARITY)
            self._rtu_bytesize = kwargs.get('bytesize', const.DEFAULT_BYTESIZE)
            self._rtu_stopbits = kwargs.get('stopbits', const.DEFAULT_STOPBITS)
            self._client = ModbusClient(port=self._rtu_port,
                                        baudrate=self._rtu_baudrate,
                                        parity=self._rtu_parity,
                                        stopbits=self._rtu_stopbits,
                                        bytesize=self._rtu_bytesize,
                                        timeout=self._timeout)
        elif self._mode == 'Modbus TCP':
            self._tcp_port = kwargs.get('port',const.DEFAULT_TCP_PORT)
            self._tcp_addr = kwargs.get('addr',const.DEFAULT_TCP_ADDR)
            self._addr = kwargs.get('modbus',const.DEFAULT_ADDR) # Modbus slave ID for the operations
            self._tcp_retries = kwargs.get('retries',const.DEFAULT_TCP_RETRIES)
            self._tcp_reco_delay_min = kwargs.get('reco_delay_min',const.DEFAULT_TCP_RECO_DELAY)
            self._tcp_reco_delay_max = kwargs.get('reco_delay_max',const.DEFAULT_TCP_RECO_DELAY_MAX)
            self._client = ModbusTcpClient(host=self._tcp_addr,
                                            port=self._tcp_port,
                                            name="ModbusTCP",
                                            retries=self._tcp_retries,
                                            reconnect_delay=self._tcp_reco_delay_min,
                                            reconnect_delay_max=self._tcp_reco_delay_max,
                                            timeout=self._timeout)
        else:
            raise InitialisationError('Mode ({}) not defined'.format(self._mode))
        if self._debug:
            pymodbus_apply_logging_config("DEBUG")

    async def __async_read_register(self, reg:int) -> (int, bool):
        ''' Read one holding register (code 0x03) '''
        async with Operations._lock:
            rr = None
            if not self._client.connected:
                raise ModbusConnexionError('Client Modbus not connected')
            try:
                await asyncio.sleep(0.3)
                _LOGGER.debug("reading holding register: {} - Slave: {}".format(hex(reg), self._addr))
                rr = await self._client.read_holding_registers(address=reg, count=1, slave=self._addr)
                if rr.isError():
                    _LOGGER.error("reading holding register error")
                    return None, False
            except Exception as e:
                _LOGGER.error("Modbus Error: {}".format(e))
                return None, False

            if isinstance(rr, ExceptionResponse):
                _LOGGER.error("Received modbus exception ({})".format(rr))
                return None, False
            elif not rr:
                _LOGGER.error("Response Null")
                return None, False
            return rr.registers[0], True

    async def __async_read_registers(self, start_reg:int, count:int) -> (list, bool):
        ''' Read holding registers (code 0x03) '''
        async with Operations._lock:
            rr = None
            if not self._client.connected:
                raise ModbusConnexionError('Client Modbus not connected')
            try:
                await asyncio.sleep(0.3)
                _LOGGER.debug("reading holding registers: {} - count: {} - Slave: {}".format(hex(start_reg), count, self._addr))
                rr = await self._client.read_holding_registers(address=start_reg, count=count, slave=self._addr)
                if rr.isError():
                    _LOGGER.error("reading holding registers error")
                    return None, False
            except Exception as e:
                _LOGGER.error("{}".format(e))
                return None, False

            if isinstance(rr, ExceptionResponse):
                _LOGGER.error("Received modbus exception ({})".format(rr))
                return None, False
            elif not rr:
                _LOGGER.error("Response Null")
                return None, False
            return rr.registers, True

    async def __async_write_register(self, reg:int, val:int) -> bool:
        ''' Write one register (code 0x06) '''
        async with Operations._lock:
            rq = None
            ret = True
            if not self._client.connected:
                raise ModbusConnexionError('Client Modbus not connected')
            try:
                await asyncio.sleep(0.3)
                _LOGGER.debug("writing single register: {} - Slave: {} - Val: {}".format(hex(reg), self._addr, hex(val)))
                rq = await self._client.write_register(address=reg, value=val, slave=self._addr)
                if rq.isError():
                    _LOGGER.error("writing register error")
                    return False
            except Exception as e:
                _LOGGER.error("{}".format(e))
                return False

            if isinstance(rq, ExceptionResponse):
                _LOGGER.error("Received modbus exception ({})".format(rr))
                return False
            return ret 

    async def async_connect(self) -> None:
        ''' connect to the modbus serial server '''
        async with Operations._lock:
            await self._client.connect()

    def connected(self) -> bool:
        ''' get modbus client status '''
        return self._client.connected

    def disconnect(self) -> None:
        ''' close the underlying socket connection '''
        if self._client.connected:
            self._client.close()

    async def async_set_debug(self, val:bool) -> bool:
        ''' Set/Reset Debug Mode '''
        if val:
            pymodbus_apply_logging_config("DEBUG")
        else:
            pymodbus_apply_logging_config("INFO")
        return True

    def __transform_unit(self, 
                            unit:const.UnitMode,
                            val:int,
                        ) -> float:
        ''' transform temperature from unit '''
        if unit == const.UnitMode.CELCIUS:
            # if unit is Celcius, send value = actual value * 2 + 30
            return ((val - 30) / 2)
        else:
            return val

    def __get_err_code(self,
                        val:int) -> str:
        ''' transform int value to Error code '''
        err_code = {
            **{str(i): f"E{chr(48 + i - 1)}" for i in range(1, 10)},  # 'E0' to 'E8'
            "10": "E9", "11": "EA", "12": "EB", "13": "EC", "14": "ED", "15": "EE", "16": "EF",
            "17": "EH", "18": "EL", "19": "EP",

            **{str(i): f"P{chr(48 + i - 20)}" for i in range(20, 29)},  # 'P0' to 'P8'
            "29": "P9", "30": "PA", "31": "PB", "32": "PC", "33": "PD", "34": "PE", "35": "PF",
            "36": "PH", "37": "PL", "38": "PP",

            **{str(i): f"H{chr(48 + i - 39)}" for i in range(39, 48)},  # 'H0' to 'H8'
            "48": "H9", "49": "HA", "50": "HB", "51": "HC", "52": "HD", "53": "HE", "54": "HF",
            "55": "HH", "56": "HL", "57": "HP",

            **{str(i): f"C{chr(48 + i - 58)}" for i in range(58, 67)},  # 'C0' to 'C8'
            "67": "C9", "68": "CA", "69": "CB", "70": "CC", "71": "CD", "72": "CE", "73": "CF",
            "74": "CH", "75": "CL", "76": "CP",

            **{str(i): f"L{chr(48 + i - 77)}" for i in range(77, 86)},  # 'L0' to 'L8'
            "86": "L9", "87": "LA", "88": "LB", "89": "LC", "90": "LD", "91": "LE", "92": "LF",
            "93": "LH", "94": "LL", "95": "LP",

            **{str(i): f"B{chr(48 + i - 96)}" for i in range(96, 105)},  # 'B0' to 'B8'
            "105": "B9", "106": "BA", "107": "BB", "108": "BC", "109": "BD", "110": "BE", "111": "BF",
            "112": "BH", "113": "BL", "114": "BP"
        }
        return err_code.get(str(val), "None")

    async def async_get_cmd_values(self) -> (bool, dict):
        ''' get values from register 0 (Power on/off) to 3 (command functions)
            and get values from register 100 (Operating mode) to 119 (wire controller firmware)
        '''
        _num_regs:int = 4
        _regs:list = ()
        _ret:bool = False
        _cmd_values = {}

        # read registers 0 to 3
        _regs, _ret = await self.__async_read_registers(start_reg = const.REG_POWER_STATE, count = _num_regs)
        if not _ret:
            _LOGGER.error('Error getting command values 0 to 3')
            return _ret, _cmd_values

        _cmd_values['power'] = const.PowerState(_regs[0])
        _cmd_values['setting_mode'] = const.SettingMode(_regs[1])
        _cmd_values['solar'] = const.SolarSignal(_regs[3] & 0b01)
        _cmd_values['evu'] = const.ElectricHeaterStatus((_regs[3] >> 1) & 0b01)
        _cmd_values['sg'] = const.FourWayValveStatus((_regs[3] >> 2) & 0b01)
        _cmd_values['remoterSignal'] = const.RemoterSignal((_regs[3] >> 3) & 0b01)
        _cmd_values['remoterMode'] = const.RemoterMode((_regs[3] >> 4) & 0b01)
        _cmd_values['desinfect'] = const.DisinfectFunc((_regs[3] >> 5) & 0b01)
        _cmd_values['unit'] = const.UnitMode((_regs[3] >> 6) & 0b01)
        _cmd_values['target_temp'] = self.__transform_unit(_cmd_values['unit'], _regs[2])

        # read registers 100 to 119
        _num_regs = 20
        _regs, _ret = await self.__async_read_registers(start_reg = const.REG_OPERATING_MODE, count = _num_regs)
        if not _ret:
            _LOGGER.error('Error getting command values 100 to 119')
            return _ret, {}

        _LOGGER.debug("[DEBUG] OPE:{}".format(_regs[0]))
        _cmd_values['ope'] = const.OperatingMode(_regs[0])
        _cmd_values['T5U'] = self.__transform_unit(_cmd_values['unit'], _regs[1])
        _cmd_values['T5L'] = self.__transform_unit(_cmd_values['unit'], _regs[2])
        _cmd_values['T3'] = self.__transform_unit(_cmd_values['unit'], _regs[3])
        _cmd_values['T4'] = self.__transform_unit(_cmd_values['unit'], _regs[4])
        _cmd_values['TP'] = self.__transform_unit(_cmd_values['unit'], _regs[5])
        _cmd_values['TH'] = self.__transform_unit(_cmd_values['unit'], _regs[6])
        _cmd_values['PMV'] = _regs[7]
        _cmd_values['comp_current'] = _regs[8]
        _cmd_values['compressor'] = const.CompressorStatus(_regs[9] & 0b01)
        _cmd_values['elecHeater'] = const.ElectricHeaterStatus((_regs[9] >> 1) & 0b01)
        _cmd_values['valve'] = const.FourWayValveStatus((_regs[9] >> 2) & 0b01)
        _cmd_values['fanLow'] = const.FanSpeedLowStatus((_regs[9] >> 3) & 0b01)
        _cmd_values['fanMed'] = const.FanSpeedMediumStatus((_regs[9] >> 4) & 0b01)
        _cmd_values['fanHigh'] = const.FanSpeedHighStatus((_regs[9] >> 5) & 0b01)
        _cmd_values['solarPump'] = const.SolarPanelWaterPumpStatus((_regs[9] >> 6) & 0b01)
        _cmd_values['alarm'] = const.AlarmStatus((_regs[9] >> 7) & 0b01)
        _cmd_values['err_code'] = self.__get_err_code(_regs[10])
        _cmd_values['max_ts'] = _regs[11]
        _cmd_values['min_ts'] = _regs[12]
        _cmd_values['TX'] = self.__transform_unit(_cmd_values['unit'], _regs[13])
        _cmd_values['vacation'] = const.VacationMode(_regs[15] & 0b01)
        _cmd_values['solar_kit'] = const.SolarKitMode((_regs[15] >> 1) & 0b01)
        _cmd_values['defrost'] = const.DefrostMode((_regs[15] >> 2) & 0b01)
        _cmd_values['wifi'] = const.WifiStatus((_regs[15] >> 3) & 0b01)
        _cmd_values['comp_time'] = _regs[16]
        _cmd_values['model'] = const.Model(_regs[17])
        _cmd_values['pcb_firm'] = _regs[18]
        _cmd_values['wire_firm'] = _regs[19]
        return _ret, _cmd_values

    async def async_get_power_status(self) -> (bool, const.PowerState):
        ''' Read power status register '''
        reg, ret = await self.__async_read_register(const.REG_POWER_STATE)
        if not ret:
            _LOGGER.error('Error retreive power status')
            reg = 0
        return ret, const.PowerState(reg)

    async def async_set_power_status(self,
                                    opt:const.PowerState,
                                    ) -> bool:
        ''' Write system status '''
        ret = await self.__async_write_register(reg = const.REG_POWER_STATE, val = int(opt))
        if not ret:
            _LOGGER.error('Error writing power status')
        return ret

    async def async_get_setting_mode(self) -> (bool, const.SettingMode):
        ''' Read setting mode '''
        reg, ret = await self.__async_read_register(const.REG_SETTING_MODE)
        if not ret:
            _LOGGER.error('Error retreive setting mode')
            reg = 1
        return ret, const.SettingMode(reg)

    async def async_set_setting_mode(self,
                                    opt:const.OperatingMode,
                                    ) -> bool:
        ''' Write setting mode '''
        ret = await self.__async_write_register(reg = const.REG_SETTING_MODE, val = int(opt))
        if not ret:
            _LOGGER.error('Error writing setting mode')
        return ret

    async def async_get_target_temp(self,
                                    unit:const.UnitMode,
                                    ) -> (bool, float):
        """ get target Ts temperature """
        reg, ret = await self.__async_read_register(reg = const.REG_SETTING_TEMP_TS)
        if not ret:
            _LOGGER.error('Error retreive temperature Ts')
            reg = 0
            return ret, reg
        
        if unit == const.UnitMode.CELCIUS:
            # if unit is Celcius, send value = actual value * 2 + 30
            reg = (reg - 30) / 2 

        return ret, reg

    async def async_set_target_temp(self,
                                    unit:const.UnitMode,
                                    val:float = 0.0,
                                    ) -> bool:
        ''' Set target Ts temperature '''

        if unit == const.UnitMode.CELCIUS:
            if val < const.MIN_C_TEMP or val > const.MAX_C_TEMP:
                _LOGGER.error('target Ts Temperature must be between {}°C and {}°C'.format(const.MIN_C_TEMP, const.MAX_C_TEMP))
                return False
            # if unit is Celcius, send value = actual value * 2 + 30
            val = int(val * 2) + 30
        elif unit == const.UnitMode.FAHRENHEIT:
            if val < const.MIN_F_TEMP or val > const.MAX_F_TEMP:
                _LOGGER.error('target Ts Temperature must be between {}°F and {}°F'.format(const.MIN_F_TEMP, const.MAX_F_TEMP))
                return False
            val = int(val)
        else:
            _LOGGER.error('Unit unknown')
            return False
        ret = await self.__async_write_register(reg = const.REG_SETTING_TEMP_TS, val = val)
        if not ret:
            _LOGGER.error('Error writing target Ts temperature')

        return ret

    async def async_set_unit(self,
                            unit:const.UnitMode,
                            ) -> bool:
        ''' set unit (Fahrenheit or Celcius) '''
        # retreive command functions register
        _ret:bool = False
        _cmd_dict:dict = {}
        _ret, _cmd_dict = await self.async_get_command_func()
        if not _ret:
            _LOGGER.error('Error retreiving command functions register')
            return _ret

        # set new unit mode
        _cmd_dict['unit'] = unit
        _ret = await self.__async_set_command_func(_cmd_dict)
        if not _ret:
            _LOGGER.error('Error setting unit mode')
        return _ret

    async def async_set_disinfect(self,
                                    state:const.DisinfectFunc,
                                    ) -> bool:
        ''' set/reset disinfection '''
        # retreive command functions register
        _ret:bool = False
        _cmd_dict:dict = {}
        _ret, _cmd_dict = await self.async_get_command_func()
        if not _ret:
            _LOGGER.error('Error retreiving command functions register')
            return _ret

        # set new disinfect func
        _cmd_dict['desinfect'] = state
        _ret = await self.__async_set_command_func(_cmd_dict)
        if not _ret:
            _LOGGER.error('Error setting/reseting disinfect func')
        return _ret

    async def async_set_smart_grid(self,
                                    state:const.SGCmd,
                                    ) -> bool:
        ''' set/reset smart grid '''
        # retreive command functions register
        _ret:bool = False
        _cmd_dict:dict = {}
        _ret, _cmd_dict = await self.async_get_command_func()
        if not _ret:
            _LOGGER.error('Error retreiving command functions register')
            return _ret

        # set new SG func
        _cmd_dict['sg'] = state
        _ret = await self.__async_set_command_func(_cmd_dict)
        if not _ret:
            _LOGGER.error('Error setting/reseting smart grid func')
        return _ret

    async def async_set_solar_signal_evu(self,
                                        state:const.EVUCmd,
                                        ) -> bool:
        ''' set/reset solar signal EVU '''
        # retreive command functions register
        _ret:bool = False
        _cmd_dict:dict = {}
        _ret, _cmd_dict = await self.async_get_command_func()
        if not _ret:
            _LOGGER.error('Error retreiving command functions register')
            return _ret

        # set new EVU func
        _cmd_dict['evu'] = state
        _ret = await self.__async_set_command_func(_cmd_dict)
        if not _ret:
            _LOGGER.error('Error setting/reseting solar signal (EVU) func')
        return _ret

    async def async_set_remoter(self,
                                state:const.RemoterMode,
                                ) -> bool:
        ''' set/reset solar signal EVU '''
        # retreive command functions register
        _ret:bool = False
        _cmd_dict:dict = {}
        _ret, _cmd_dict = await self.async_get_command_func()
        if not _ret:
            _LOGGER.error('Error retreiving command functions register')
            return _ret

        # set new remoter func
        _cmd_dict['remoterMode'] = state
        _ret = await self.__async_set_command_func(_cmd_dict)
        if not _ret:
            _LOGGER.error('Error setting/reseting remoter func')
        return _ret

    async def __async_set_command_func(self,
                                        cmd_funcs:dict
                                        ) -> bool:
        ''' Set command functions '''
        _ret:bool = False
        _reg:int = 0
        
        # construct reg value
        _reg |= (int(cmd_funcs['solar']) & 0b1) << 0
        _reg |= (int(cmd_funcs['evu']) & 0b1) << 1
        _reg |= (int(cmd_funcs['sg']) & 0b1) << 2
        _reg |= (int(cmd_funcs['remoterSignal']) & 0b1) << 3
        _reg |= (int(cmd_funcs['remoterMode']) & 0b1) << 4
        _reg |= (int(cmd_funcs['desinfect']) & 0b1) << 5
        _reg |= (int(cmd_funcs['unit']) & 0b1) << 6
        
        _ret = await self.__async_write_register(reg = const.REG_CMD_FUNCS, val = _reg)
        if not _ret:
            _LOGGER.error('Error writing command functions')

        return _ret

    async def async_get_command_func(self) -> (bool, dict):
        ''' Get command functions '''
        _cmd_dict:dict = {}
        reg, ret = await self.__async_read_register(reg = const.REG_CMD_FUNCS)
        if not ret:
            _LOGGER.error('Error get load output')
            reg = 0

        _cmd_dict['solar'] = const.SolarSignal(reg & 0b01)
        _cmd_dict['evu'] = const.ElectricHeaterStatus((reg >> 1) & 0b01)
        _cmd_dict['sg'] = const.FourWayValveStatus((reg >> 2) & 0b01)
        _cmd_dict['remoterSignal'] = const.RemoterSignal((reg >> 3) & 0b01)
        _cmd_dict['remoterMode'] = const.RemoterMode((reg >> 4) & 0b01)
        _cmd_dict['desinfect'] = const.DisinfectFunc((reg >> 5) & 0b01)
        _cmd_dict['unit'] = const.UnitMode((reg >> 6) & 0b01)
        
        return ret, _cmd_dict

    async def async_get_hour(self) -> (bool, int):
        ''' Get hour '''
        reg, ret = await self.__async_read_register(reg = const.REG_HOUR)
        if not ret:
            _LOGGER.error('Error get hour')
            reg = 0
            return ret, reg

        return ret, reg

    async def async_get_minute(self) -> (bool, int):
        ''' Get minute '''
        reg, ret = await self.__async_read_register(reg = const.REG_MINUTE)
        if not ret:
            _LOGGER.error('Error get minute')
            reg = 0
            return ret, reg

        return ret, reg

    async def async_get_operating_mode(self) -> (bool, const.OperatingMode):
        ''' Get operating mode '''
        reg, ret = await self.__async_read_register(reg = const.REG_OPERATING_MODE)
        if not ret:
            _LOGGER.error('Error get operating mode')
            reg = 0
            return ret, reg

        return ret, const.OperatingMode(reg)

    async def async_get_temps(self, 
                                unit:const.UnitMode
                                ) -> (bool, dict):
        ''' get temperatures T5U, T5L, T3, T4, TP and TH '''
        temps:dict = {'T5U':0.0, 'T5L':0.0, 'T3':0.0, 'T4':0.0, 'TP':0.0, 'TH':0.0}
        _num_regs:int = 6
        regs, ret = await self.__async_read_registers(start_reg = const.REG_TEMP_T5U, count = _num_regs)
        if not ret:
            _LOGGER.error('Error getting temperatures')
            return ret, temps
        
        for idx, reg in enumerate(regs):
            if unit == const.UnitMode.CELCIUS:
                reg = (reg - 30) / 2
            _LOGGER.debug("[GET TEMP] reg[{}]: {}".format(idx, reg))
            temps[list(temps.keys())[idx]] = reg
        return ret, temps

    async def async_get_t5u_temp(self,
                                unit:const.UnitMode,
                                ) -> (bool, float):
        ''' get T5U temperature '''
        reg, ret = await self.__async_read_register(reg = const.REG_TEMP_T5U)
        if not ret:
            _LOGGER.error('Error get T5U temperature')
            reg = 0
            return ret, reg

        _LOGGER.debug("[OPERATIONS] T5U: {}".format(reg))
        if unit == const.UnitMode.CELCIUS:
            # if unit is Celcius, send value = actual value * 2 + 30
            reg = (reg - 30) / 2

        return ret, reg

    async def async_get_t5l_temp(self,
                                unit:const.UnitMode,
                                ) -> (bool, float):
        ''' get T5L temperature '''
        reg, ret = await self.__async_read_register(reg = const.REG_TEMP_T5L)
        if not ret:
            _LOGGER.error('Error get T5L temperature')
            reg = 0
            return ret, reg
        
        _LOGGER.debug("[OPERATIONS] T5L: {}".format(reg))
        if unit == const.UnitMode.CELCIUS:
            # if unit is Celcius, send value = actual value * 2 + 30
            reg = (reg - 30) / 2

        return ret, reg

    async def async_get_current_temp(self, 
                                    unit:const.UnitMode,
                                    choice:str,
                                    ) -> (bool, float):
        ''' get current temperature '''
        _temp:float = 0.0
        _ret:bool = False
        _num_regs:int = 2
        # read Modbus registers
        regs, _ret = await self.__async_read_registers(start_reg = const.REG_TEMP_T5U, count = _num_regs)
        if not _ret:
            _LOGGER.error('Error get T5U & T5L temperatures')
            return _ret, _temp
        
        if choice == "Maximum":
            _temp = max(regs)
        elif choice == "Minimum":
            _temp = min(regs)
        else: # Average
            for idx, reg in enumerate(regs):
                _LOGGER.debug("[GET CURRENT TEMP] reg[{}]: {}".format(idx, reg))
                _temp += reg
            # average of high (T5U) and low (T5L) temperatures
            _temp = _temp / _num_regs
        if unit == const.UnitMode.CELCIUS:
            _temp = (_temp - 30) / 2
        return _ret, _temp


    async def async_get_t3_temp(self,
                                unit:const.UnitMode,
                                ) -> (bool, float):
        ''' get T3 temperature '''
        reg, ret = await self.__async_read_register(reg = const.REG_TEMP_T3)
        if not ret:
            _LOGGER.error('Error get T3 temperature')
            reg = 0
            return ret, reg
        
        if unit == const.UnitMode.CELCIUS:
            # if unit is Celcius, send value = actual value * 2 + 30
            reg = (reg - 30) / 2

        return ret, reg

    async def async_get_t4_temp(self,
                                unit:const.UnitMode,
                                ) -> (bool, float):
        ''' get T4 temperature '''
        reg, ret = await self.__async_read_register(reg = const.REG_TEMP_T4)
        if not ret:
            _LOGGER.error('Error get T4 temperature')
            reg = 0
            return ret, reg
        
        if unit == const.UnitMode.CELCIUS:
            # if unit is Celcius, send value = actual value * 2 + 30
            reg = (reg - 30) / 2

        return ret, reg

    async def async_get_tp_exhaust_gas_temp(self,
                                            unit:const.UnitMode,
                                            ) -> (bool, float):
        ''' get Tp exhaust gas temperature '''
        reg, ret = await self.__async_read_register(reg = const.REG_TEMP_EXHAUST_GAS)
        if not ret:
            _LOGGER.error('Error get Tp exhaust gas temperature')
            reg = 0
            return ret, reg
        
        if unit == const.UnitMode.CELCIUS:
            # if unit is Celcius, send value = actual value * 2 + 30
            reg = (reg - 30) / 2

        return ret, reg

    async def async_get_th_temp(self,
                                unit:const.UnitMode,
                                ) -> (bool, float):
        ''' get Th temperature '''
        reg, ret = await self.__async_read_register(reg = const.REG_TEMP_TH)
        if not ret:
            _LOGGER.error('Error get Th temperature')
            reg = 0
            return ret, reg
        
        if unit == const.UnitMode.CELCIUS:
            # if unit is Celcius, send value = actual value * 2 + 30
            reg = (reg - 30) / 2

        return ret, reg

    async def async_get_pmv_opening_value(self) -> (bool, int):
        ''' Get PMV opening value (in Step)'''
        reg, ret = await self.__async_read_register(reg = const.REG_PMV_OPENING_VALUE)
        if not ret:
            _LOGGER.error('Error get PMV opening value')
            reg = 0
        
        return ret, reg


    async def async_get_compressor_current(self) -> (bool, int):
        ''' Get compressor current (in Ampere)'''
        reg, ret = await self.__async_read_register(reg = const.REG_COMPRESSOR_CURRENT)
        if not ret:
            _LOGGER.error('Error get compressor current')
            reg = 0
        
        return ret, reg

    async def async_get_load_output(self) -> (bool, dict):
        ''' Get load output '''
        _load_dict:dict = {}
        reg, ret = await self.__async_read_register(reg = const.REG_LOAD_OUTPUT)
        if not ret:
            _LOGGER.error('Error get load output')
            reg = 0

        _load_dict['compressor'] = const.CompressorStatus(reg & 0b01)
        _load_dict['elecHeater'] = const.ElectricHeaterStatus((reg >> 1) & 0b01)
        _load_dict['valve'] = const.FourWayValveStatus((reg >> 2) & 0b01)
        _load_dict['fanLow'] = const.FanSpeedLowStatus((reg >> 3) & 0b01)
        _load_dict['fanMed'] = const.FanSpeedMediumStatus((reg >> 4) & 0b01)
        _load_dict['fanHigh'] = const.FanSpeedHighStatus((reg >> 5) & 0b01)
        _load_dict['solarPump'] = const.SolarPanelWaterPumpStatus((reg >> 6) & 0b01)
        _load_dict['alarm'] = const.AlarmStatus((reg >> 7) & 0b01)
        _LOGGER.debug("[LOAD OUTPUT]: reg: {}".format(_load_dict))
        return ret, _load_dict

    async def async_get_error_protect_code(self) -> (bool, str):
        ''' get error protect code 
            01 - 19  : E0-E9, EA, EB, EC, ED, EE, EF, EH, EL, EP
            20 - 38  : P0-P9, PA, PB, PC, PD, PE, PF, PH, PL, PP
            39 - 57  : H0-H9, HA, HB, HC, HD, HE, HF, HH, HL, HP
            58 - 76  : C0-C9, CA, CB, CC, CD, CE, CF, CH, CL, CP
            77 - 95  : L0-L9, LA, LB, LC, LD, LE, LF, LH, LL, LP
            96 - 114 : B0-B9, BA, BB, BC, BD, BE, BF, BH, BL, BP
        '''
        err_code = {
            **{str(i): f"E{chr(48 + i - 1)}" for i in range(1, 10)},  # 'E0' to 'E8'
            "10": "E9", "11": "EA", "12": "EB", "13": "EC", "14": "ED", "15": "EE", "16": "EF",
            "17": "EH", "18": "EL", "19": "EP",

            **{str(i): f"P{chr(48 + i - 20)}" for i in range(20, 29)},  # 'P0' to 'P8'
            "29": "P9", "30": "PA", "31": "PB", "32": "PC", "33": "PD", "34": "PE", "35": "PF",
            "36": "PH", "37": "PL", "38": "PP",

            **{str(i): f"H{chr(48 + i - 39)}" for i in range(39, 48)},  # 'H0' to 'H8'
            "48": "H9", "49": "HA", "50": "HB", "51": "HC", "52": "HD", "53": "HE", "54": "HF",
            "55": "HH", "56": "HL", "57": "HP",

            **{str(i): f"C{chr(48 + i - 58)}" for i in range(58, 67)},  # 'C0' to 'C8'
            "67": "C9", "68": "CA", "69": "CB", "70": "CC", "71": "CD", "72": "CE", "73": "CF",
            "74": "CH", "75": "CL", "76": "CP",

            **{str(i): f"L{chr(48 + i - 77)}" for i in range(77, 86)},  # 'L0' to 'L8'
            "86": "L9", "87": "LA", "88": "LB", "89": "LC", "90": "LD", "91": "LE", "92": "LF",
            "93": "LH", "94": "LL", "95": "LP",

            **{str(i): f"B{chr(48 + i - 96)}" for i in range(96, 105)},  # 'B0' to 'B8'
            "105": "B9", "106": "BA", "107": "BB", "108": "BC", "109": "BD", "110": "BE", "111": "BF",
            "112": "BH", "113": "BL", "114": "BP"
        }

        reg, ret = await self.__async_read_register(reg = const.REG_ERR_PROTECT_CODE)
        if not ret:
            _LOGGER.error('Error get protect code')
            return False, 'None'
        
        return ret, err_code.get(str(reg), "None")

    async def async_get_min_max_ts_temps(self) -> (bool, float, float):
        ''' get minimum and maximum Ts temperatures '''
        temp_min:float = 0.0
        temp_max:float = 0.0
        regs, ret = await self.__async_read_registers(start_reg = const.REG_MAX_TEMP_TS, count = 2)
        if not ret:
            _LOGGER.error('Error get T5U & T5L temperatures')
            return ret, temp_min, temp_max
        
        for idx, reg in enumerate(regs):
            if idx == 0:
                _LOGGER.debug("[GET MAX TS TEMP] reg[{}]: {}".format(idx, reg))
                temp_max = reg
            elif idx == 1:
                _LOGGER.debug("[GET MIN TS TEMP] reg[{}]: {}".format(idx, reg))
                temp_min = reg
            else:
                _LOGGER.exception("more reg than expected ....")
        return ret, temp_min, temp_max

    async def async_get_max_ts_temp(self,
                                    unit:const.UnitMode,
                                    ) -> (bool, float):
        ''' get maximum Ts temperature '''
        reg, ret = await self.__async_read_register(reg = const.REG_MAX_TEMP_TS)
        if not ret:
            _LOGGER.error('Error get max Ts temperature')
            reg = 0
        return ret, reg

    async def async_get_min_ts_temp(self,
                                    unit:const.UnitMode,
                                    ) -> (bool, float):
        ''' get minimum Ts temperature '''
        reg, ret = await self.__async_read_register(reg = const.REG_MIN_TEMP_TS)
        if not ret:
            _LOGGER.error('Error get min Ts temperature')
            reg = 0
        return ret, reg

    async def async_get_display_temp(self,
                                        unit:const.UnitMode,
                                        ) -> (bool, float):
        ''' get target display temperature '''
        reg, ret = await self.__async_read_register(reg = const.REG_TEMP_DISPLAY)
        if not ret:
            _LOGGER.error('Error get display temperature')
            reg = 0
            return ret, reg
        
        if unit == const.UnitMode.CELCIUS:
            # if unit is Celcius, send value = actual value * 2 + 30
            reg = (reg - 30) / 2

        return ret, reg

    async def async_get_misc(self) -> (bool, dict):
        ''' Get misc registers :
            - Auxiliary Status (115)
            - Compressor running time (116)
            - Model (117)
            - Main PCB firmware version (118)
            - Wire controller firmware version (119)
        '''
        _misc_dict:dict = {}
        regs, ret = await self.__async_read_registers(start_reg = const.REG_AUX_STATUS, count = 5)
        if not ret:
            _LOGGER.error('Error getting misc values')
            return ret, _misc_dict
        
        for idx, reg in enumerate(regs):
            if idx == 0: # aux status
                _misc_dict['vacation'] = const.VacationMode(reg & 0b01)
                _misc_dict['solar_kit'] = const.SolarKitMode((reg >> 1) & 0b01)
                _misc_dict['defrost'] = const.DefrostMode((reg >> 2) & 0b01)
                _misc_dict['wifi'] = const.WifiStatus((reg >> 3) & 0b01)
            elif idx == 1: # compressor running time
                _misc_dict['comp_time'] = reg
            elif idx == 2: # model
                _misc_dict['model'] = const.Model(reg)
            elif idx == 3: # main PCB firmware version
                _misc_dict['pcb_firm'] = reg
            else:
                _misc_dict['wire_firm'] = reg

        return ret, _misc_dict

    async def async_get_aux_status(self) -> (bool, dict):
        ''' Get auxiliary status '''
        _aux_dict:dict = {}
        reg, ret = await self.__async_read_register(reg = const.REG_AUX_STATUS)
        if not ret:
            _LOGGER.error('Error get auxiliary status')
            reg = 0

        _aux_dict['vacation'] = const.VacationMode(reg & 0b01)
        _aux_dict['solar_kit'] = const.SolarKitMode((reg >> 1) & 0b01)
        _aux_dict['defrost'] = const.DefrostMode((reg >> 2) & 0b01)
        _aux_dict['wifi'] = const.WifiStatus((reg >> 3) & 0b01)
        
        return ret, _aux_dict

    async def async_get_compressor_running_time(self) -> (bool, int):
        ''' Get compressor running time (in second)'''
        reg, ret = await self.__async_read_register(reg = const.REG_COMP_RUN_TIME)
        if not ret:
            _LOGGER.error('Error get model')
            reg = 0
        
        return ret, reg

    async def async_get_model(self) -> (bool, const.Model):
        ''' Get model '''
        reg, ret = await self.__async_read_register(reg = const.REG_MODEL)
        if not ret:
            _LOGGER.error('Error get model')
            reg = 0
            return ret, reg

        return ret, const.Model(reg)

    async def async_get_firmware_version(self) -> (bool, int):
        ''' Get main PCB firmware version '''
        reg, ret = await self.__async_read_register(reg = const.REG_VERSION_FIRMWARE)
        if not ret:
            _LOGGER.error('Error get main firmware version')
            reg = 0
            return ret, reg

        # Value must be between 1 and 99
        if reg < 1 or reg > 99:
            _LOGGER.warning('Value {} must be between 1 and 99'.format(reg))
        
        return ret, reg

    async def async_get_wire_controller_firmware_version(self) -> (bool, int):
        ''' Get wire controller firmware version '''
        reg, ret = await self.__async_read_register(reg = const.REG_VERSION_WIRE_CONTROLLER)
        if not ret:
            _LOGGER.error('Error get wire controller firmware version')
            reg = 0
            return ret, reg

        # Value must be between 1 and 99
        if reg < 1 or reg > 99:
            _LOGGER.warning('Value {} must be between 1 and 99'.format(reg))

        return ret, reg

class InitialisationError(Exception):
    ''' user defined exception '''

    def __init__(self,
                    msg:str = "") -> None:
        ''' Class Constructor '''
        self._msg = msg

    def __str__(self):
        ''' print the message '''
        return self._msg    

class ModbusConnexionError(Exception):
    ''' user defined exception '''

    def __init__(self,
                    msg:str = "") -> None:
        ''' Class Constructor '''
        self._msg = msg

    def __str__(self):
        ''' print the message '''
        return self._msg

class ReadRegistersError(Exception):
    ''' user defined exception '''

    def __init__(self,
                    msg:str = "") -> None:
        ''' Class Constructor '''
        self._msg = msg

    def __str__(self):
        ''' print the message '''
        return self._msg
