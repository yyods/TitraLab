import time
import machine
import onewire
import ds18x20

#DS18B20 data line connected to pin P10
dat = machine.Pin(4)
ds = ds18x20.DS18X20(onewire.OneWire(dat))

sensors = ds.scan()
print('Found DS18B20 sensors:', sensors)

ds.convert_temp()
time.sleep_ms(750)
for sensor in sensors:
    print('Temperatre:', ds.read_temp(sensor))
