# ==============================================================================
# __init__.py - Week 2 Library Initialization
# ==============================================================================
# โมดูลนี้ทำให้ import คลาสจาก lib folder ได้ง่าย
# This module makes importing classes from lib folder easier
#
# การใช้งาน (Usage):
#   from lib import BaseSensor, PHSensor, TempSensor, Pump, Buzzer
#   หรือ (or)
#   from lib.ph_sensor import PHSensor
#
# ==============================================================================

# นำเข้าคลาสทั้งหมดเพื่อให้ import ง่าย
# Import all classes for easy importing

from lib.base_sensor import BaseSensor
from lib.ph_sensor import PHSensor
from lib.temp_sensor import TempSensor
from lib.pump import Pump
from lib.buzzer import Buzzer

# กำหนด __all__ เพื่อระบุว่า export อะไรบ้าง
# Define __all__ to specify what to export
__all__ = [
    'BaseSensor',
    'PHSensor',
    'TempSensor',
    'Pump',
    'Buzzer'
]

# Version information
__version__ = '2.0.0'
__author__ = 'TitraLab Team'
