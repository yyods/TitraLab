# ==============================================================================
# async_support/__init__.py - โมดูล Asynchronous สำหรับ TitraLab
# ==============================================================================
# โมดูลนี้ให้การสนับสนุน asynchronous operations สำหรับการไทเทรชัน
# This module provides asynchronous operation support for titration
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
# 1. เรียนรู้การใช้ uasyncio สำหรับ non-blocking operations
# 2. เข้าใจ coroutines และ async/await pattern
# 3. จัดการ concurrent tasks บน MicroPython
#
# โมดูลที่มีให้ (Available Modules):
# - async_pump: ควบคุมปั๊มแบบ asynchronous
# - async_titration: ไทเทรชันแบบ asynchronous
# - scheduler: ตัวจัดการงาน concurrent
#
# ตัวอย่างการใช้งาน (Usage Example):
#   from async_support import AsyncPump, AsyncTitrationController, TaskScheduler
#
# หมายเหตุ (Note):
# โมดูลนี้เป็น optional - ระบบหลักทำงานได้โดยไม่ต้องใช้ async
# This module is optional - main system works without async
# ==============================================================================

# เวอร์ชัน (Version)
__version__ = '1.0.0'
__author__ = 'TitraLab Team'

# นำเข้า submodules (Import submodules)
try:
    from .async_pump import AsyncPump
    from .async_titration import AsyncTitrationController
    from .scheduler import TaskScheduler

    # รายการส่งออก (Export list)
    __all__ = [
        'AsyncPump',
        'AsyncTitrationController',
        'TaskScheduler'
    ]

    print("async_support โมดูลพร้อมใช้งาน (async_support module ready)")

except ImportError as e:
    # uasyncio อาจไม่มีในบาง firmware
    # uasyncio may not be available in some firmware
    print(f"คำเตือน: ไม่สามารถโหลด async_support ได้ (Warning: Cannot load async_support): {e}")
    __all__ = []
