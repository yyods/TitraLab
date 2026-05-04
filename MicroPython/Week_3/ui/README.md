# UI Layer (Layer 4)
# ชั้น User Interface

---

## ภาพรวม (Overview)

โฟลเดอร์ `ui/` คือชั้นบนสุดของสถาปัตยกรรม TitraLab ทำหน้าที่จัดการ **ส่วนติดต่อผู้ใช้** และ **State Machine** สำหรับนำทางระหว่างโหมดต่างๆ

The `ui/` folder is the top layer of the TitraLab architecture. It handles **User Interface** and **State Machine** for navigation between modes.

### หลักการสำคัญ (Key Principles)

1. **State Machine Pattern**: จัดการสถานะของแอปพลิเคชันอย่างเป็นระบบ
2. **Separation of UI Logic**: แยก UI logic ออกจาก business logic
3. **Event-Driven**: ตอบสนองต่อ button events

---

## โครงสร้างไฟล์ (File Structure)

```
ui/
├── __init__.py    # Package initialization
├── menu.py        # State Machine และการจัดการเมนู
└── screens.py     # คลาสสำหรับแสดงหน้าจอต่างๆ
```

---

## menu.py - ระบบเมนูและ State Machine

### MenuState - สถานะของเมนู

```python
class MenuState:
    MAIN_MENU = 0       # แสดงเมนูหลัก
    MODE_RUNNING = 1    # กำลังทำงานในโหมดที่เลือก
    RESULT_DISPLAY = 2  # แสดงผลลัพธ์
```

### State Machine Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          STATE MACHINE                                   │
│                                                                          │
│   ┌─────────────┐                                                       │
│   │ MAIN_MENU   │ ◄────────────────────────────────────────────┐       │
│   │             │                                               │       │
│   │  เลือกโหมด   │                                               │       │
│   └──────┬──────┘                                               │       │
│          │                                                       │       │
│          │ SELECT pressed                                        │       │
│          │ (เลือกโหมด)                                           │       │
│          ▼                                                       │       │
│   ┌─────────────┐                                               │       │
│   │MODE_RUNNING │ ─────────────────────────────────────────────►│       │
│   │             │  is_complete() = True                          │       │
│   │  รันโหมด     │  หรือ long press DOWN (ยกเลิก)                 │       │
│   └──────┬──────┘                                               │       │
│          │                                                       │       │
│          │ Mode complete                                         │       │
│          │ (โหมดเสร็จสิ้น)                                        │       │
│          ▼                                                       │       │
│   ┌─────────────┐                                               │       │
│   │RESULT_DISP  │                                               │       │
│   │             │ ──────────────────────────────────────────────┘       │
│   │ แสดงผลลัพธ์   │  SELECT pressed (กลับเมนู)                           │
│   └─────────────┘                                                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### ButtonHandler - จัดการปุ่มกด

```python
from ui.menu import ButtonHandler

buttons = ButtonHandler()

# ตรวจสอบการกดปุ่ม (พร้อม debounce)
if buttons.is_pressed('select'):
    print("Select pressed!")

if buttons.is_pressed('up'):
    print("Up pressed!")

if buttons.is_pressed('down'):
    print("Down pressed!")

# ตรวจสอบการกดค้าง
if buttons.is_long_pressed('down', duration_ms=3000):
    print("Long press detected!")

# รอจนกว่าปุ่มจะถูกปล่อย
buttons.wait_release('select')
```

### MenuSystem - ระบบเมนูหลัก

```python
from ui.menu import MenuSystem, MenuState

# สร้าง MenuSystem
menu = MenuSystem(
    display=display,
    screen_main_menu=main_menu_screen,
    modes=[mode1, mode2, mode3, ...],
    buzzer=buzzer
)

# เริ่มทำงาน (main loop)
menu.run()

# หรือจัดการเองทีละ state
menu.set_state(MenuState.MAIN_MENU)
while True:
    if menu.state == MenuState.MAIN_MENU:
        menu.handle_main_menu()
    elif menu.state == MenuState.MODE_RUNNING:
        menu.handle_mode_running()
    elif menu.state == MenuState.RESULT_DISPLAY:
        menu.handle_result_display()
```

---

## screens.py - คลาสหน้าจอ

### BaseScreen - คลาสพื้นฐาน

```python
class BaseScreen:
    """คลาสพื้นฐานสำหรับทุกหน้าจอ"""

    def __init__(self, display, colors):
        self.display = display
        self.colors = colors

    def render(self):
        """แสดงหน้าจอ - ต้อง override"""
        raise NotImplementedError

    def update(self, **kwargs):
        """อัปเดตข้อมูลบนหน้าจอ"""
        pass
```

### MainMenuScreen - หน้าจอเมนูหลัก

```python
from ui.screens import MainMenuScreen

# สร้างหน้าจอเมนูหลัก
menu_items = [
    "1. Calibrate pH Sensor",
    "2. pH Sensor Test",
    "3. Calibrate Flow Rate",
    "4. Flow Rate Test",
    "5. Purge",
    "6. Full Auto Titration"
]

main_screen = MainMenuScreen(display, colors, menu_items)

# แสดงหน้าจอ
main_screen.render()

# เลื่อนตัวเลือก
main_screen.select_next()     # เลื่อนลง
main_screen.select_previous() # เลื่อนขึ้น

# รับตัวเลือกที่เลือก
selected = main_screen.get_selected()  # 0-5
```

### CalibrationScreen - หน้าจอสอบเทียบ

```python
from ui.screens import CalibrationScreen

calib_screen = CalibrationScreen(display, colors)

# แสดงขั้นตอนการสอบเทียบ
calib_screen.show_step(1, "Buffer pH 4.00", voltage=1.523)
calib_screen.show_step(2, "Buffer pH 7.00", voltage=2.012)
calib_screen.show_step(3, "Buffer pH 10.00", voltage=2.498)

# แสดงผลลัพธ์
calib_screen.show_result(slope=-5.79, intercept=16.77, r_squared=0.9998)
```

### TitrationScreen - หน้าจอไทเทรชัน

```python
from ui.screens import TitrationScreen

titration_screen = TitrationScreen(display, colors)

# อัปเดตค่า (Update values)
titration_screen.update(
    volume=15.4,
    ph=6.23,
    temperature=25.1,
    phase="dosing"        # เฟส: dosing / stabilizing / reading / endpoint
)

# แสดงจุดสมมูล
titration_screen.show_equivalence_point(volume=25.3, ph=7.02)
```

### ResultScreen - หน้าจอผลลัพธ์

```python
from ui.screens import ResultScreen

result_screen = ResultScreen(display, colors)

# แสดงผลลัพธ์
result_screen.show(
    title="Titration Complete",
    results={
        'Eq. Volume': '25.3 mL',
        'Eq. pH': '7.02',
        'Total Time': '5:12'
    }
)
```

---

## การไหลของ Event (Event Flow)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            EVENT FLOW                                    │
│                                                                          │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐              │
│   │   Buttons   │ ──► │ ButtonHandler│ ──► │ MenuSystem  │              │
│   │  (GPIO)     │     │  (Debounce) │     │  (State)    │              │
│   └─────────────┘     └─────────────┘     └──────┬──────┘              │
│                                                   │                      │
│                                                   │ เปลี่ยน state        │
│                                                   │ หรือ เรียก mode      │
│                                                   ▼                      │
│                                            ┌─────────────┐              │
│                                            │   Screens   │              │
│                                            │  (Display)  │              │
│                                            └─────────────┘              │
│                                                   │                      │
│                                                   │ render()             │
│                                                   ▼                      │
│                                            ┌─────────────┐              │
│                                            │   Display   │              │
│                                            │  (TFT)      │              │
│                                            └─────────────┘              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Button Mapping (การกำหนดปุ่ม)

| ปุ่ม | GPIO | หน้าที่ใน MAIN_MENU | หน้าที่ใน MODE_RUNNING |
|------|------|---------------------|------------------------|
| SELECT (Button 1) | 34 | เลือกเมนู | ยืนยัน/ดำเนินการต่อ |
| UP (Button 2) | 35 | เลื่อนขึ้น | - |
| DOWN (Button 3) | 39 | เลื่อนลง / กดค้าง 3s = ออก | ยกเลิก (กดค้าง 3s) |

---

## ตัวอย่างการใช้งาน (Usage Example)

```python
# main.py - ตัวอย่างการใช้ UI Layer
from ui.menu import MenuSystem
from ui.screens import MainMenuScreen
from hardware import HardwareHub
from modes import create_all_modes

# สร้าง hardware
hw = HardwareHub()

# สร้าง modes
modes = create_all_modes(
    display=hw.display,
    colors=Colors,
    ph_sensor=hw.ph_sensor,
    pump=hw.pump,
    temperature_sensor=hw.temp_sensor,
    buzzer=hw.buzzer
)

# สร้างหน้าจอเมนู
menu_items = [m.name for m in modes]
main_screen = MainMenuScreen(hw.display, Colors, menu_items)

# สร้าง MenuSystem
menu = MenuSystem(
    display=hw.display,
    screen_main_menu=main_screen,
    modes=modes,
    buzzer=hw.buzzer
)

# เริ่มทำงาน
try:
    menu.run()
finally:
    hw.deinit()
```

---

## วัตถุประสงค์การเรียนรู้ (Learning Objectives)

หลังจากศึกษาโฟลเดอร์นี้ นักศึกษาจะสามารถ:

1. **เข้าใจ State Machine Pattern**: การจัดการสถานะของแอปพลิเคชัน
2. **ออกแบบ Event-Driven System**: ตอบสนองต่อ input จากผู้ใช้
3. **แยก UI Logic ออกจาก Business Logic**: ความเป็นระเบียบของโค้ด
4. **ใช้ Debounce**: ป้องกันการกดปุ่มซ้ำ

---

## ลำดับการศึกษาแนะนำ (Recommended Study Order)

1. `menu.py` - เริ่มจาก MenuState และ ButtonHandler
2. `menu.py` - ศึกษา MenuSystem และ state transitions
3. `screens.py` - ดูโครงสร้าง BaseScreen
4. `screens.py` - ศึกษา MainMenuScreen และ screen อื่นๆ

---

*TitraLab Week 3 - User Interface Layer*
