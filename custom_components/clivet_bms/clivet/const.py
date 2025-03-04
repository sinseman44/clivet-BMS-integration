# Constants for Water Heater Modbus RTU/TCP
# d'après la documentation officielle

from enum import Enum

DEFAULT_MODE = 'Modbus RTU'
DEFAULT_TCP_ADDR = '0.0.0.0'
DEFAULT_TCP_PORT = 502
DEFAULT_TCP_RETRIES = 3
DEFAULT_TCP_RECO_DELAY = 0.1
DEFAULT_TCP_RECO_DELAY_MAX = 300.0
# La couche physique est Modbus RTU sur RS485 à 9600, avec 8 bits de données, sans parité
# ou même parité et un bit d'arrêt. Par défaut: 9600 8N1
# L'adresse Modbus par défaut est 0
DEFAULT_ADDR = 1
DEFAULT_BAUDRATE = 9600
DEFAULT_PARITY = 'N'
DEFAULT_STOPBITS = 1
DEFAULT_BYTESIZE = 8

# Power off/on
REG_POWER_STATE = 0

class PowerState(Enum):
    STATE_OFF = 0
    STATE_ON = 1

    def __int__(self):
        return self.value

# Setting Mode
REG_SETTING_MODE = 1

class SettingMode(Enum):
    INVALID = 1
    HYBRID = 2
    E_HEATER = 3
    VACATION = 4

    def __int__(self):
        return self.value

# Setting the temperature Ts
REG_SETTING_TEMP_TS = 2

# Range of temperature in Celcius
MIN_C_TEMP = 38
MAX_C_TEMP = 70

# Range of temperature in fahrenheit
MIN_F_TEMP = 100
MAX_F_TEMP = 158

# Command Functions
REG_CMD_FUNCS = 3

class UnitMode(Enum):
    CELCIUS = 0
    FAHRENHEIT = 1

    def __int__(self):
        return self.value

class DisinfectFunc(Enum):
    OFF = 0
    ON = 1

    def __int__(self):
        return self.value

class RemoterMode(Enum):
    OFF = 0
    ON = 1

    def __int__(self):
        return self.value

class RemoterSignal(Enum):
    PANEL_CAN_WORK = 0
    PANEL_CANNOT_WORK = 1

    def __int__(self):
        return self.value

class SGCmd(Enum):
    OFF = 0
    ON = 1

    def __int__(self):
        return self.value

class EVUCmd(Enum):
    OFF = 0
    ON = 1

    def __int__(self):
        return self.value

class SolarSignal(Enum):
    SOLAR_PANEL_ON = 0
    SOLAR_PANEL_OFF = 1

    def __int__(self):
        return self.value

# Hour
REG_HOUR = 4

# Minute
REG_MINUTE = 5

# Operating Mode
REG_OPERATING_MODE = 100

class OperatingMode(Enum):
    INVALID = 1
    HYBRID = 2
    E_HEATER = 3
    VACATION = 4

    def __int__(self):
        return self.value

# Water temperature in upper position of water tank
REG_TEMP_T5U = 101

# Water temperature in lower position of water tank
REG_TEMP_T5L = 102

# Condenser temperature
REG_TEMP_T3 = 103

# Outdor ambient temperature
REG_TEMP_T4 = 104

# Compressor exhaust temperature Tp
REG_TEMP_EXHAUST_GAS = 105

# Suction Temp Th
REG_TEMP_TH = 106

# External electronic expansion opening valve
REG_PMV_OPENING_VALUE = 107

# Input AC current
REG_COMPRESSOR_CURRENT = 108

# Load Output
REG_LOAD_OUTPUT = 109

class AlarmStatus(Enum):
    OFF = 0
    ON = 1

    def __int__(self):
        return self.value

class SolarPanelWaterPumpStatus(Enum):
    OFF = 0
    ON = 1

    def __int__(self):
        return self.value

class FanSpeedHighStatus(Enum):
    OFF = 0
    ON = 1

    def __int__(self):
        return self.value

class FanSpeedMediumStatus(Enum):
    OFF = 0
    ON = 1

    def __int__(self):
        return self.value

class FanSpeedLowStatus(Enum):
    OFF = 0
    ON = 1

    def __int__(self):
        return self.value

class FourWayValveStatus(Enum):
    OFF = 0
    ON = 1

    def __int__(self):
        return self.value

class ElectricHeaterStatus(Enum):
    OFF = 0
    ON = 1

    def __int__(self):
        return self.value

class CompressorStatus(Enum):
    OFF = 0
    ON = 1

    def __int__(self):
        return self.value

# Error Protect Code
REG_ERR_PROTECT_CODE = 110

# Maximum of Ts
REG_MAX_TEMP_TS = 111

# Minimum of Ts
REG_MIN_TEMP_TS = 112

# Display temperature Tx
REG_TEMP_DISPLAY = 113

# Auxiliary Status
REG_AUX_STATUS = 115

class WifiStatus(Enum):
    NOT_CONNECT = 0
    CONNECT = 1

    def __int__(self):
        return self.value

class DefrostMode(Enum):
    OFF = 0
    ON = 1

    def __int__(self):
        return self.value

class SolarKitMode(Enum):
    OFF = 0
    ON = 1

    def __int__(self):
        return self.value

class VacationMode(Enum):
    NOT_ACTIVE = 0
    ACTIVE = 1

    def __int__(self):
        return self.value

# Compressor running time
REG_COMP_RUN_TIME = 116

# Model
REG_MODEL = 117

class Model(Enum):
    MODEL_190 = 1
    MODEL_300 = 2

    def __int__(self):
        return self.value

# Main PCB firmware version
REG_VERSION_FIRMWARE = 118

# Wire Controller firmware version
REG_VERSION_WIRE_CONTROLLER = 119