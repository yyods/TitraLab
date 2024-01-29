import os
from machine import Pin, SoftSPI
from sdcard import SDCard

# Pin assignment for TitraLab:

# MISO -> GPIO 19
# MOSI -> GPIO 23
# SCK  -> GPIO 18
# CS   -> GPIO 5

spisd = SoftSPI(-1, miso=Pin(19), mosi=Pin(23), sck=Pin(18))

sd = SDCard(spisd, Pin(5))



print('Root directory:{}'.format(os.listdir()))

vfs = os.VfsFat(sd)

os.mount(vfs, '/sd')

print('Root directory:{}'.format(os.listdir()))

os.chdir('sd')

print('SD Card contains:{}'.format(os.listdir()))

filename = 'test.txt'

with open(filename, "a") as f:
    f.write('File created by MicroPython!!\n')

with open(filename, "r") as f:
    print(f.read())

# os.remove(filename)

# os.umount("/sd")

