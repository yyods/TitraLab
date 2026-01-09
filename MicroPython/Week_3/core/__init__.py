# ==============================================================================
# core/__init__.py - แพ็คเกจ Core Logic สำหรับ TitraLab
# (Core Logic Package for TitraLab)
# ==============================================================================
# โมดูลนี้รวบรวม core logic classes สำหรับระบบไทเทรชัน
# This module contains core logic classes for the titration system
#
# โมดูลที่มี (Available Modules):
#   - math_utils: คลาส LinearRegression และฟังก์ชันคณิตศาสตร์
#   - data_manager: จัดการข้อมูลการสอบเทียบและไทเทรชัน
#   - calibrator: การสอบเทียบเซ็นเซอร์และปั๊ม
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจการแยก business logic ออกจาก hardware
#   2. เรียนรู้ pattern สำหรับ modular architecture
#   3. ประยุกต์ใช้ dependency injection
#
# การใช้งาน (Usage):
#   from core import LinearRegression, DataManager, Calibrator
#
#   lr = LinearRegression()
#   dm = DataManager()
#   cal = Calibrator(dm)
#
# ==============================================================================

__version__ = '2.0.0'
__author__ = 'TitraLab Team'

# นำเข้าคลาสจากโมดูลย่อย (Import classes from submodules)
from .math_utils import LinearRegression, calculate_linear_regression, calculate_mean, calculate_std
from .data_manager import DataManager
from .calibrator import Calibrator
from .titration import TitrationController

# กำหนดสิ่งที่ export เมื่อใช้ from core import *
# Define what to export when using from core import *
__all__ = [
    'LinearRegression',
    'calculate_linear_regression',
    'calculate_mean',
    'calculate_std',
    'DataManager',
    'Calibrator',
    'TitrationController'
]


# ==============================================================================
# ตัวอย่างการใช้งาน (Usage Example)
# ==============================================================================
if __name__ == "__main__":
    print("=" * 50)
    print("ทดสอบ core package (Testing core package)")
    print("=" * 50)
    print(f"Version: {__version__}")
    print(f"Author: {__author__}")
    print(f"\nAvailable classes: {__all__}")

    # ทดสอบ import
    print("\n--- ทดสอบ import ---")
    print(f"LinearRegression: {LinearRegression}")
    print(f"DataManager: {DataManager}")
    print(f"Calibrator: {Calibrator}")

    print("\ncore package พร้อมใช้งาน (core package ready)")
