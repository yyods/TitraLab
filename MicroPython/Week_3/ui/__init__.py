# ==============================================================================
# ui/__init__.py - แพ็กเกจ UI สำหรับระบบไทเทรชัน (UI Package for Titration System)
# ==============================================================================
# แพ็กเกจนี้รวบรวมคลาสสำหรับจัดการส่วนติดต่อผู้ใช้ (User Interface)
# This package contains classes for User Interface management
#
# โครงสร้างแพ็กเกจ (Package Structure):
# - screens.py: คลาสสำหรับแสดงหน้าจอต่างๆ (Screen rendering classes)
# - menu.py: คลาสจัดการเมนูและ state machine (Menu and state machine)
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
# 1. เรียนรู้การจัดโครงสร้างโค้ดเป็น package (Package organization)
# 2. เข้าใจการ import และ export module (Import/export modules)
# 3. ฝึกการออกแบบ UI แบบ modular (Modular UI design)
# ==============================================================================

# นำเข้าคลาสหลักเพื่อให้ใช้งานง่าย (Import main classes for easy access)
from .screens import (
    BaseScreen,
    MainMenuScreen,
    CalibrationScreen,
    TitrationScreen,
    ResultScreen
)
from .menu import MenuSystem, MenuState

# กำหนด public API ของ package (Define package public API)
__all__ = [
    'BaseScreen',
    'MainMenuScreen',
    'CalibrationScreen',
    'TitrationScreen',
    'ResultScreen',
    'MenuSystem',
    'MenuState'
]

# ข้อมูล package (Package info)
__version__ = '1.0.0'
__author__ = 'TitraLab Team'
