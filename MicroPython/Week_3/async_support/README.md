# Async Support (Optional/Advanced)
# โมดูล Asynchronous สำหรับผู้เรียนขั้นสูง

---

> **หมายเหตุสำคัญ**: โฟลเดอร์นี้เป็น **เนื้อหาเสริมสำหรับผู้เรียนขั้นสูง** ระบบหลักของ TitraLab ทำงานได้ปกติโดยไม่จำเป็นต้องใช้ async
>
> **Important Note**: This folder contains **advanced optional content**. The main TitraLab system works without async.

---

## ภาพรวม (Overview)

โฟลเดอร์ `async_support/` มีคลาสและฟังก์ชันสำหรับการเขียนโปรแกรมแบบ **Asynchronous** บน MicroPython โดยใช้ `uasyncio` ซึ่งเป็น library สำหรับ non-blocking operations

The `async_support/` folder contains classes and functions for **Asynchronous** programming on MicroPython using `uasyncio` library for non-blocking operations.

### เมื่อไหร่ควรใช้ Async (When to Use Async)

| กรณี | แบบปกติ (Synchronous) | แบบ Async |
|------|----------------------|-----------|
| อ่าน pH ทุกวินาที | เหมาะสม | ไม่จำเป็น |
| อ่าน pH + อัปเดตจอ + ตรวจปุ่ม **พร้อมกัน** | ต้องจัดลำดับเอง | เหมาะสม |
| ต้องการ responsive UI ขณะไทเทรต | อาจกระตุก | เหมาะสม |

---

## โครงสร้างไฟล์ (File Structure)

```
async_support/
├── __init__.py          # Package initialization
├── async_pump.py        # คลาสปั๊มแบบ async
├── async_titration.py   # ไทเทรชันแบบ async
└── scheduler.py         # ตัวจัดการ concurrent tasks
```

---

## แนวคิด Async บน MicroPython (Async Concepts on MicroPython)

### พื้นฐาน uasyncio (uasyncio Basics)

```python
import uasyncio as asyncio

# Coroutine - ฟังก์ชันที่สามารถ "หยุดชั่วคราว" ได้
async def read_sensor():
    """อ่านเซ็นเซอร์แบบ async"""
    value = sensor.read()
    await asyncio.sleep_ms(100)  # รอ 100ms โดยไม่ block
    return value

# Task - Coroutine ที่กำลังทำงาน
async def main():
    # รัน coroutine เดียว
    value = await read_sensor()

    # รัน หลาย coroutines พร้อมกัน
    results = await asyncio.gather(
        read_ph(),
        read_temperature(),
        update_display()
    )

# เริ่มทำงาน
asyncio.run(main())
```

### เปรียบเทียบ Sync vs Async (Sync vs Async Comparison)

**แบบ Synchronous (ปกติ)**:
```python
# ต้องรอแต่ละงานเสร็จก่อน
while True:
    ph = read_ph()          # รอ ~100ms
    temp = read_temp()      # รอ ~750ms
    update_display()        # รอ ~50ms
    check_buttons()         # รอ ~10ms
    # รวม ~910ms ต่อ loop
```

**แบบ Asynchronous**:
```python
# ทำหลายงานพร้อมกัน
async def main_loop():
    while True:
        # ทั้ง 4 งานทำงานพร้อมกัน
        await asyncio.gather(
            read_ph_task(),
            read_temp_task(),
            display_task(),
            button_task()
        )
    # ใช้เวลารวมเท่ากับงานที่นานที่สุด (~750ms)
```

---

## คำอธิบายแต่ละไฟล์ (File Descriptions)

### async_pump.py - คลาสปั๊มแบบ Async

```python
from async_support.async_pump import AsyncPump

async def main():
    pump = AsyncPump()

    # สูบปริมาตรโดยไม่ block
    await pump.run_for_volume_async(volume_ml=5.0, duty_percent=100)

    # สูบพร้อมกับอ่านค่า pH
    await asyncio.gather(
        pump.run_for_volume_async(2.0),
        read_ph_continuously()
    )
```

### async_titration.py - ไทเทรชันแบบ Async

```python
from async_support.async_titration import AsyncTitrationController

async def main():
    controller = AsyncTitrationController(
        pump=pump,
        ph_sensor=ph_sensor,
        display=display
    )

    # ไทเทรตแบบ async
    result = await controller.run_titration_async()
```

### scheduler.py - ตัวจัดการ Task

```python
from async_support.scheduler import TaskScheduler, Task

# สร้าง scheduler
scheduler = TaskScheduler()

# เพิ่ม tasks
scheduler.add_task(Task(
    name="read_ph",
    coroutine=read_ph_task,
    interval_ms=1000
))

scheduler.add_task(Task(
    name="update_display",
    coroutine=update_display_task,
    interval_ms=100
))

# รัน scheduler
await scheduler.run()
```

---

## ตัวอย่างการใช้งาน (Usage Examples)

### ตัวอย่าง 1: อ่านค่าหลายเซ็นเซอร์พร้อมกัน

```python
import uasyncio as asyncio

async def read_ph():
    """อ่าน pH ทุก 1 วินาที"""
    while True:
        voltage, ph = ph_sensor.read()
        print(f"pH: {ph:.2f}")
        await asyncio.sleep_ms(1000)

async def read_temp():
    """อ่านอุณหภูมิทุก 2 วินาที"""
    while True:
        temp = temp_sensor.read()
        print(f"Temp: {temp:.1f} C")
        await asyncio.sleep_ms(2000)

async def main():
    # รันทั้งสอง task พร้อมกัน
    await asyncio.gather(read_ph(), read_temp())

asyncio.run(main())
```

### ตัวอย่าง 2: UI ที่ตอบสนองได้ขณะไทเทรต

```python
import uasyncio as asyncio

async def titration_task():
    """ควบคุมการไทเทรต"""
    while not endpoint_reached:
        pump.run()
        ph = ph_sensor.read_ph()
        check_endpoint(ph)
        await asyncio.sleep_ms(100)

async def display_task():
    """อัปเดตจอแสดงผลทุก 50ms"""
    while True:
        display.update(ph=current_ph, volume=current_volume)
        await asyncio.sleep_ms(50)

async def button_task():
    """ตรวจสอบปุ่มทุก 10ms"""
    while True:
        if buttons.is_pressed('down'):
            # ยกเลิกการไทเทรต
            cancel_event.set()
        await asyncio.sleep_ms(10)

async def main():
    await asyncio.gather(
        titration_task(),
        display_task(),
        button_task()
    )
```

---

## ข้อควรระวัง (Cautions)

### 1. Memory Limit

MicroPython บน ESP32 มีหน่วยความจำจำกัด การสร้าง tasks มากเกินไปอาจทำให้หน่วยความจำเต็ม

```python
# หลีกเลี่ยง: สร้าง tasks จำนวนมาก
for i in range(100):
    asyncio.create_task(some_task())  # อาจ memory error!

# แนะนำ: ใช้ asyncio.gather กับจำนวน tasks ที่จำกัด
await asyncio.gather(task1(), task2(), task3())
```

### 2. Blocking Operations

หลีกเลี่ยง blocking operations ใน async code

```python
# ไม่ดี: time.sleep() จะ block ทุกอย่าง
async def bad_task():
    time.sleep(1)  # BLOCK!

# ดี: ใช้ asyncio.sleep()
async def good_task():
    await asyncio.sleep(1)  # Non-blocking
```

### 3. Hardware Access

บาง hardware operations อาจ block แม้จะอยู่ใน async code

```python
# DS18B20 conversion ใช้เวลา 750ms และ block
temp = temp_sensor.read()  # ยังคง block!

# วิธีแก้: ใช้ non-blocking read ถ้ามี
temp_sensor.start_conversion()
await asyncio.sleep_ms(750)
temp = temp_sensor.read_result()
```

---

## เมื่อไหร่ไม่ควรใช้ Async (When NOT to Use Async)

1. **โปรเจกต์ง่ายๆ**: ถ้าทำงานทีละอย่างได้ ไม่จำเป็นต้องใช้ async
2. **เริ่มต้นเรียนรู้**: ควรเข้าใจ synchronous code ก่อน
3. **Hardware จำกัด**: Async ใช้ memory และ CPU มากกว่า

---

## วัตถุประสงค์การเรียนรู้ (Learning Objectives)

หลังจากศึกษาโฟลเดอร์นี้ (สำหรับผู้เรียนขั้นสูง) จะสามารถ:

1. **เข้าใจ Concurrency**: ความแตกต่างระหว่าง sync และ async
2. **ใช้ uasyncio**: เขียน coroutines และจัดการ tasks
3. **ออกแบบ Non-blocking System**: UI ที่ตอบสนองได้
4. **รู้ข้อจำกัด**: เมื่อไหร่ควร/ไม่ควรใช้ async

---

## ลำดับการศึกษาแนะนำ (Recommended Study Order)

> **ข้อกำหนดเบื้องต้น**: ควรเข้าใจระบบหลัก (hardware/, core/, modes/, ui/) ก่อน

1. ศึกษาพื้นฐาน `uasyncio` จาก MicroPython documentation
2. `scheduler.py` - ดูโครงสร้าง Task และ TaskScheduler
3. `async_pump.py` - ดูการแปลง Pump เป็น async
4. `async_titration.py` - ดูการรวม async components

---

## อ้างอิง (References)

- [MicroPython uasyncio Documentation](https://docs.micropython.org/en/latest/library/uasyncio.html)
- [Peter Hinch's uasyncio Tutorial](https://github.com/peterhinch/micropython-async)

---

*TitraLab Week 3 - Async Support (Optional/Advanced)*
