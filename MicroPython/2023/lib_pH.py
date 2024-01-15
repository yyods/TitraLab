import machine
from time import ticks_ms, sleep_ms
from ili9341 import Display, color565
from machine import Pin, ADC, PWM, SPI
from xglcd_font import XglcdFont
from onewire import OneWire
from ds18x20 import DS18X20

class pHProbeCalibration:
    def __init__(self, acid_voltage, neutral_voltage, basic_voltage):
        self._acidVoltage = acid_voltage
        self._neutralVoltage = neutral_voltage
        self._basicVoltage = basic_voltage
        self._phValue = 0.0

    def readPH(self, voltage, temperature):
        slope = (7.00 - 4.01) / ((self._neutralVoltage - 1500.0) / 3.0 - (self._acidVoltage - 1500.0) / 3.0)
        intercept = 7.00 - slope * (self._neutralVoltage - 1500.0) / 3.0
        self._phValue = slope * (voltage - 1500.0) / 3.0 + intercept
        return self._phValue

    def calibration(self, voltage, temperature, cmd):
        self._voltage = voltage
        self._temperature = temperature
        sCmd = cmd.upper()
        self.phCalibration(self.cmdParse(sCmd))

    def update_temperature(roms, ds):
        for rom in roms:
            ds.convert_temp()
            sleep_ms(750)
            temp = ds.read_temp(rom)
            temp_str = "{:.2f} C".format(temp)
            print("Temperature is:", temp_str)