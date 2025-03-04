""" consts for clivet BMS """

from datetime import timedelta

from homeassistant.const import (
    Platform,
    STATE_ON,
    STATE_OFF,
)
from homeassistant.components.water_heater.const import (
    STATE_ECO,
    STATE_ELECTRIC,
    STATE_PERFORMANCE,
    STATE_HIGH_DEMAND,
    STATE_HEAT_PUMP,
)
from .clivet.const import (
    PowerState,
    SettingMode,
    UnitMode,
    DisinfectFunc,
    RemoterMode,
    RemoterSignal,
    SolarSignal,
    OperatingMode,
    Model,
    WifiStatus,
    DefrostMode,
    SolarKitMode,
    AlarmStatus,
    CompressorStatus,
    ElectricHeaterStatus,
    FourWayValveStatus,
    SolarPanelWaterPumpStatus,
    FourWayValveStatus,
    SolarPanelWaterPumpStatus,
    SGCmd,
    EVUCmd,
)

DOMAIN = "clivet_bms"
PLATFORMS: list[Platform] = [Platform.WATER_HEATER,
                            Platform.SENSOR,
                            Platform.SWITCH,
                            Platform.BINARY_SENSOR]

CONF_NAME = "clivet-BMS-Integration"
CONF_DEVICE_ID = "device_id"

DEVICE_MANUFACTURER = "clivet"

OPE_INVALID = "Invalid"
OPE_VACATION = "Vacation"

OPE_TRANSLATION = {
    int(OperatingMode.INVALID): OPE_INVALID,
    int(OperatingMode.HYBRID): STATE_PERFORMANCE,
    int(OperatingMode.E_HEATER): STATE_ELECTRIC,
    int(OperatingMode.VACATION): OPE_VACATION,
}

SUPPORTED_OPE_LIST = [
    STATE_PERFORMANCE,
    STATE_ELECTRIC,
]

MODEL_TRANSLATION = {
    int(Model.MODEL_190): "190",
    int(Model.MODEL_300): "300",
}

POWER_TRANSLATION = {
    int(PowerState.STATE_OFF): False,
    int(PowerState.STATE_ON): True,
}

WIFI_TRANSLATION = {
    int(WifiStatus.NOT_CONNECT): False,
    int(WifiStatus.CONNECT): True,
}

DEFROST_TRANSLATION = {
    int(DefrostMode.OFF): False,
    int(DefrostMode.ON): True,
}

SOLAR_TRANSLATION = {
    int(SolarKitMode.OFF): False,
    int(SolarKitMode.ON): True,
}

ALARM_TRANSLATION = {
    int(AlarmStatus.OFF): False,
    int(AlarmStatus.ON): True,
}

COMPRESSOR_TRANSLATION = {
    int(CompressorStatus.OFF): False,
    int(CompressorStatus.ON): True,
}

E_HEATER_TRANSLATION = {
    int(ElectricHeaterStatus.OFF): False,
    int(ElectricHeaterStatus.ON): True,
}

VALVE_TRANSLATION = {
    int(FourWayValveStatus.OFF): False,
    int(FourWayValveStatus.ON): True,
}

SOLAR_PUMP_TRANSLATION = {
    int(SolarPanelWaterPumpStatus.OFF): False,
    int(SolarPanelWaterPumpStatus.ON): True,
}

UNIT_TRANSLATION = {
    int(UnitMode.CELCIUS): False,
    int(UnitMode.FAHRENHEIT): True,
}

DISINFECT_TRANSLATION = {
    int(DisinfectFunc.OFF): False,
    int(DisinfectFunc.ON): True,
}

SG_TRANSLATION = {
    int(SGCmd.OFF): False,
    int(SGCmd.ON): True,
}

EVU_TRANSLATION = {
    int(EVUCmd.OFF): False,
    int(EVUCmd.ON): True,
}

REMOTER_TRANSLATION = {
    int(RemoterMode.OFF): False,
    int(RemoterMode.ON): True,
}