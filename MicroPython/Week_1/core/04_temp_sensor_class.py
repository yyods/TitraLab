# ==============================================================================
# 04_temp_sensor_class.py - Temperature Sensor Class for TitraLab
# ==============================================================================
# Week 1 Core: DS18B20 temperature sensor with Nernst equation connection
#
# Chemistry Context:
#   Temperature affects pH via Nernst equation: E = E0 - (RT/nF) * ln(Q)
#   At 25C: slope = 59.16 mV/pH
#   At 30C: slope = 60.15 mV/pH
#   Accurate pH requires temperature compensation!
# ==============================================================================

import time
import machine
import onewire
import ds18x20


class TemperatureSensor:
    """
    DS18B20 Temperature Sensor Class

    Example:
        sensor = TemperatureSensor(16)
        temp_c = sensor.read_celsius()
        temp_k = sensor.read_kelvin()  # For Nernst
    """

    R = 8.314   # Gas constant (J/mol*K)
    F = 96485   # Faraday constant (C/mol)

    def __init__(self, pin_number=16, name="TempSensor"):
        """
        สร้าง TemperatureSensor (Create sensor)

        Args:
            pin_number: GPIO pin (TitraLab uses GPIO16)
            name: sensor name
        """
        self.pin_number = pin_number
        self.name = name
        self._last_celsius = None

        self._pin = machine.Pin(pin_number)
        self._ow = onewire.OneWire(self._pin)
        self._ds = ds18x20.DS18X20(self._ow)

        sensors = self._ds.scan()
        if not sensors:
            raise RuntimeError(f"DS18B20 not found at GPIO{pin_number}")
        self._rom = sensors[0]
        print(f"TempSensor ready at GPIO{pin_number}")

    def read_celsius(self):
        """อ่านอุณหภูมิ (Read temperature in Celsius)"""
        try:
            self._ds.convert_temp()
            time.sleep_ms(750)
            temp = self._ds.read_temp(self._rom)
            self._last_celsius = temp
            return temp
        except Exception as e:
            print(f"Read error: {e}")
            return None

    def read_fahrenheit(self):
        """อ่านอุณหภูมิเป็นฟาเรนไฮต์"""
        c = self.read_celsius()
        return (c * 9/5) + 32 if c else None

    def read_kelvin(self):
        """อ่านอุณหภูมิเป็นเคลวิน (for Nernst equation)"""
        c = self.read_celsius()
        return c + 273.15 if c else None

    def get_nernst_slope(self, n=1):
        """
        คำนวณ Nernst slope: 2.303*R*T / (n*F)
        At 25C (298K), n=1: slope = 59.16 mV
        """
        k = self.read_kelvin()
        return (2.303 * self.R * k) / (n * self.F) if k else None


# ==============================================================================
# Test Code
# ==============================================================================

if __name__ == "__main__":
    print("=" * 40)
    print("Temperature Sensor Test")
    print("=" * 40)

    try:
        sensor = TemperatureSensor(16)

        print("\n--- Reading temperature ---")
        for i in range(3):
            temp = sensor.read_celsius()
            if temp:
                print(f"Read {i+1}: {temp:.2f} C = {temp+273.15:.2f} K")

        print("\n--- Nernst Application ---")
        slope = sensor.get_nernst_slope(n=1)
        if slope:
            print(f"Current slope: {slope*1000:.2f} mV/pH")
            print(f"Standard (25C): 59.16 mV/pH")

    except RuntimeError as e:
        print(f"Error: {e}")
