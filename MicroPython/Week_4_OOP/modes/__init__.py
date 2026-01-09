# ==============================================================================
# modes/__init__.py - แพ็กเกจโหมดการทำงาน (Operation Modes Package)
# ==============================================================================
# แพ็กเกจนี้รวบรวมโหมดการทำงานทั้งหมดของระบบไทเทรชัน
# This package contains all operation modes for the titration system
#
# โครงสร้างแพ็กเกจ (Package Structure):
# - base_mode.py: คลาสพื้นฐานสำหรับทุกโหมด (Base class for all modes)
# - mode_calibrate_ph.py: Mode 1 - สอบเทียบ pH (pH calibration)
# - mode_test_ph.py: Mode 2 - ทดสอบ pH (pH testing)
# - mode_calibrate_flow.py: Mode 3 - สอบเทียบอัตราการไหล (Flow calibration)
# - mode_test_flow.py: Mode 4 - ทดสอบอัตราการไหล (Flow testing)
# - mode_purge.py: Mode 5 - ล้างท่อ (Purge tubing)
# - mode_titration.py: Mode 6 - ไทเทรตอัตโนมัติ (Auto titration)
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
# 1. เรียนรู้ Abstract Base Class และ inheritance (ABC and inheritance)
# 2. เข้าใจ polymorphism ผ่าน interface ร่วม (Polymorphism via shared interface)
# 3. ฝึกการออกแบบระบบแบบ modular (Modular system design)
# ==============================================================================

# นำเข้าคลาสพื้นฐาน (Import base class)
from .base_mode import BaseMode

# นำเข้าโหมดทั้งหมด (Import all modes)
from .mode_calibrate_ph import CalibratePHMode
from .mode_test_ph import TestPHMode
from .mode_calibrate_flow import CalibrateFlowMode
from .mode_test_flow import TestFlowMode
from .mode_purge import PurgeMode
from .mode_titration import TitrationMode

# กำหนด public API ของ package (Define package public API)
__all__ = [
    'BaseMode',
    'CalibratePHMode',
    'TestPHMode',
    'CalibrateFlowMode',
    'TestFlowMode',
    'PurgeMode',
    'TitrationMode'
]

# ฟังก์ชันช่วยสร้างรายการโหมดทั้งหมด (Helper function to create all modes)
def create_all_modes(display, colors, ph_sensor, pump, temperature_sensor, buzzer=None):
    """
    สร้างออบเจ็กต์โหมดทั้งหมด (Create all mode objects)

    Args:
        display: ออบเจ็กต์ Display (Display object)
        colors: คลาส Colors (Colors class)
        ph_sensor: ออบเจ็กต์ pHSensor (pHSensor object)
        pump: ออบเจ็กต์ Pump (Pump object)
        temperature_sensor: ออบเจ็กต์ TemperatureSensor (TemperatureSensor object)
        buzzer: ออบเจ็กต์ Buzzer (optional) (Buzzer object)

    Returns:
        list: รายการออบเจ็กต์โหมดทั้งหมด (List of all mode objects)

    Example:
        modes = create_all_modes(display, colors, ph_sensor, pump, temp_sensor)
        menu_system = MenuSystem(display, main_menu_screen, modes)
    """
    return [
        CalibratePHMode(display, colors, ph_sensor, temperature_sensor, buzzer),
        TestPHMode(display, colors, ph_sensor, temperature_sensor, buzzer),
        CalibrateFlowMode(display, colors, pump, buzzer),
        TestFlowMode(display, colors, pump, buzzer),
        PurgeMode(display, colors, pump, buzzer),
        TitrationMode(display, colors, ph_sensor, pump, temperature_sensor, buzzer)
    ]

# ข้อมูล package (Package info)
__version__ = '1.0.0'
__author__ = 'TitraLab Team'
