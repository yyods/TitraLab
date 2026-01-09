# ==============================================================================
# scheduler.py - ตัวจัดการงาน Concurrent (Task Scheduler)
# ==============================================================================
# โมดูลนี้จัดการการทำงานหลาย tasks พร้อมกันสำหรับระบบไทเทรชัน
# This module manages concurrent task execution for the titration system
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
# 1. เรียนรู้การจัดการ tasks หลายตัว (Multiple task management)
# 2. เข้าใจ priority scheduling (การจัดลำดับความสำคัญ)
# 3. ใช้ asyncio.Queue สำหรับ task coordination
#
# ประเภทของ Tasks ในระบบ (Task Types):
# 1. Sensor Reading  - อ่านค่าเซ็นเซอร์ (High priority)
# 2. Pump Control    - ควบคุมปั๊ม (Medium priority)
# 3. Display Update  - อัปเดตจอแสดงผล (Low priority)
# 4. Data Logging    - บันทึกข้อมูล (Background)
# ==============================================================================

import uasyncio as asyncio
import time


class Task:
    """
    คลาสแทน task ที่จะทำงาน
    Class representing a task to be executed

    Attributes:
        name: ชื่อ task (task name)
        coro: coroutine function
        priority: ความสำคัญ (0=highest, 9=lowest)
        interval: ช่วงเวลาทำซ้ำ (repeat interval in seconds, None=once)
    """

    # ระดับความสำคัญ (Priority levels)
    PRIORITY_CRITICAL = 0   # สำคัญมาก (เช่น หยุดฉุกเฉิน)
    PRIORITY_HIGH = 1       # สูง (เช่น อ่านเซ็นเซอร์)
    PRIORITY_MEDIUM = 5     # กลาง (เช่น ควบคุมปั๊ม)
    PRIORITY_LOW = 7        # ต่ำ (เช่น อัปเดตจอ)
    PRIORITY_BACKGROUND = 9 # พื้นหลัง (เช่น บันทึกข้อมูล)

    def __init__(self, name, coro, priority=PRIORITY_MEDIUM, interval=None):
        """
        สร้าง Task object
        Create Task object

        Args:
            name: ชื่อ task (task name)
            coro: coroutine function หรือ async generator
            priority: ความสำคัญ (priority level)
            interval: ช่วงเวลาทำซ้ำ (seconds, None=run once)
        """
        self.name = name
        self.coro = coro
        self.priority = priority
        self.interval = interval
        self.last_run = 0
        self.run_count = 0
        self.is_enabled = True
        self._task_handle = None

    def __lt__(self, other):
        """เปรียบเทียบ priority สำหรับ sorting (Compare priority for sorting)"""
        return self.priority < other.priority

    def __repr__(self):
        return f"Task({self.name}, priority={self.priority}, interval={self.interval})"


class TaskScheduler:
    """
    ตัวจัดการงาน concurrent สำหรับระบบไทเทรชัน
    Concurrent task scheduler for titration system

    คุณสมบัติ (Features):
    - จัดลำดับความสำคัญของ tasks (Task prioritization)
    - รองรับ periodic tasks (Periodic task support)
    - จัดการ task lifecycle (Task lifecycle management)
    - รองรับการยกเลิก tasks (Task cancellation support)
    """

    def __init__(self):
        """
        กำหนดค่าเริ่มต้น TaskScheduler
        Initialize TaskScheduler
        """
        self._tasks = {}           # name -> Task
        self._running_tasks = {}   # name -> asyncio.Task
        self._is_running = False
        self._should_stop = False
        self._task_queue = None

    def add_task(self, name, coro, priority=Task.PRIORITY_MEDIUM, interval=None):
        """
        เพิ่ม task เข้า scheduler
        Add task to scheduler

        Args:
            name: ชื่อ task (task name)
            coro: coroutine function
            priority: ความสำคัญ (priority level)
            interval: ช่วงเวลาทำซ้ำ (seconds, None=run once)

        Returns:
            Task: task object ที่สร้าง
        """
        task = Task(name, coro, priority, interval)
        self._tasks[name] = task
        print(f"เพิ่ม task: {name} (Added task: {name})")
        return task

    def remove_task(self, name):
        """
        ลบ task ออกจาก scheduler
        Remove task from scheduler

        Args:
            name: ชื่อ task (task name)
        """
        if name in self._tasks:
            # ยกเลิก task ที่กำลังทำงาน (Cancel running task)
            if name in self._running_tasks:
                self._running_tasks[name].cancel()
                del self._running_tasks[name]
            del self._tasks[name]
            print(f"ลบ task: {name} (Removed task: {name})")

    def enable_task(self, name, enabled=True):
        """
        เปิด/ปิดการทำงานของ task
        Enable/disable task

        Args:
            name: ชื่อ task (task name)
            enabled: เปิดใช้งานหรือไม่ (enable status)
        """
        if name in self._tasks:
            self._tasks[name].is_enabled = enabled
            status = "เปิด" if enabled else "ปิด"
            print(f"Task {name}: {status} ({('enabled' if enabled else 'disabled')})")

    def get_task(self, name):
        """
        ดึง task object
        Get task object

        Args:
            name: ชื่อ task (task name)

        Returns:
            Task: task object หรือ None
        """
        return self._tasks.get(name)

    def list_tasks(self):
        """
        แสดงรายการ tasks ทั้งหมด
        List all tasks

        Returns:
            list: รายการ task names
        """
        return list(self._tasks.keys())

    async def _run_periodic_task(self, task):
        """
        รัน task แบบ periodic
        Run periodic task

        Args:
            task: Task object
        """
        while not self._should_stop and task.is_enabled:
            try:
                # รัน task (Run task)
                if asyncio.iscoroutinefunction(task.coro):
                    await task.coro()
                else:
                    task.coro()

                task.run_count += 1
                task.last_run = time.ticks_ms()

            except asyncio.CancelledError:
                print(f"Task {task.name} ถูกยกเลิก (cancelled)")
                break

            except Exception as e:
                print(f"Task {task.name} error: {e}")

            # รอจนถึงรอบถัดไป (Wait for next interval)
            if task.interval:
                await asyncio.sleep(task.interval)
            else:
                break  # one-time task

    async def _run_one_shot_task(self, task):
        """
        รัน task ครั้งเดียว
        Run one-shot task

        Args:
            task: Task object
        """
        try:
            if asyncio.iscoroutinefunction(task.coro):
                result = await task.coro()
            else:
                result = task.coro()

            task.run_count += 1
            task.last_run = time.ticks_ms()
            return result

        except asyncio.CancelledError:
            print(f"Task {task.name} ถูกยกเลิก (cancelled)")

        except Exception as e:
            print(f"Task {task.name} error: {e}")

        return None

    async def run_task_once(self, name):
        """
        รัน task ครั้งเดียวทันที
        Run task once immediately

        Args:
            name: ชื่อ task (task name)

        Returns:
            ผลลัพธ์จาก task (result from task)
        """
        task = self._tasks.get(name)
        if not task:
            print(f"ไม่พบ task: {name} (Task not found: {name})")
            return None

        return await self._run_one_shot_task(task)

    async def start(self):
        """
        เริ่มการทำงานของ scheduler
        Start scheduler
        """
        if self._is_running:
            print("Scheduler กำลังทำงานอยู่แล้ว (Scheduler already running)")
            return

        self._is_running = True
        self._should_stop = False

        print("=" * 50)
        print("เริ่มการทำงาน TaskScheduler (Starting TaskScheduler)")
        print("=" * 50)

        # จัดเรียง tasks ตาม priority (Sort tasks by priority)
        sorted_tasks = sorted(self._tasks.values())

        # สร้าง asyncio tasks สำหรับ periodic tasks (Create asyncio tasks)
        for task in sorted_tasks:
            if task.is_enabled:
                if task.interval:
                    # Periodic task
                    asyncio_task = asyncio.create_task(self._run_periodic_task(task))
                    self._running_tasks[task.name] = asyncio_task
                    print(f"  เริ่ม periodic task: {task.name} (Started periodic task)")
                else:
                    # One-shot task - รันทันที (Run immediately)
                    asyncio_task = asyncio.create_task(self._run_one_shot_task(task))
                    self._running_tasks[task.name] = asyncio_task
                    print(f"  เริ่ม one-shot task: {task.name} (Started one-shot task)")

        print(f"จำนวน tasks ที่ทำงาน: {len(self._running_tasks)}")
        print("(Number of running tasks)")
        print("=" * 50)

    async def stop(self):
        """
        หยุดการทำงานของ scheduler
        Stop scheduler
        """
        if not self._is_running:
            return

        print("\nกำลังหยุด TaskScheduler... (Stopping TaskScheduler...)")
        self._should_stop = True

        # ยกเลิก tasks ทั้งหมด (Cancel all tasks)
        for name, asyncio_task in self._running_tasks.items():
            asyncio_task.cancel()
            try:
                await asyncio_task
            except asyncio.CancelledError:
                pass

        self._running_tasks.clear()
        self._is_running = False
        print("TaskScheduler หยุดทำงานแล้ว (TaskScheduler stopped)")

    async def wait_all(self):
        """
        รอจนกว่า tasks ทั้งหมดจะเสร็จ
        Wait for all tasks to complete
        """
        if self._running_tasks:
            await asyncio.gather(*self._running_tasks.values(), return_exceptions=True)

    @property
    def is_running(self):
        """
        ตรวจสอบสถานะการทำงาน
        Check running status
        """
        return self._is_running

    def get_stats(self):
        """
        ดึงสถิติการทำงาน
        Get execution statistics

        Returns:
            dict: สถิติของแต่ละ task
        """
        stats = {}
        for name, task in self._tasks.items():
            stats[name] = {
                'priority': task.priority,
                'interval': task.interval,
                'run_count': task.run_count,
                'is_enabled': task.is_enabled,
                'is_running': name in self._running_tasks
            }
        return stats


# ==============================================================================
# Predefined Task Factories - ฟังก์ชันสร้าง tasks มาตรฐาน
# ==============================================================================

def create_sensor_reading_task(sensor, callback, interval=1.0):
    """
    สร้าง task สำหรับอ่านเซ็นเซอร์
    Create sensor reading task

    Args:
        sensor: sensor object ที่มี read() method
        callback: async function(value) เพื่อรับค่า
        interval: ช่วงเวลาอ่าน (seconds)

    Returns:
        tuple: (coro, priority, interval)
    """
    async def read_sensor():
        value = sensor.read() if hasattr(sensor, 'read') else None
        if callback:
            await callback(value)
        return value

    return (read_sensor, Task.PRIORITY_HIGH, interval)


def create_display_update_task(display, data_provider, interval=0.5):
    """
    สร้าง task สำหรับอัปเดตจอแสดงผล
    Create display update task

    Args:
        display: display object
        data_provider: async function() ที่คืนค่าข้อมูลสำหรับแสดง
        interval: ช่วงเวลาอัปเดต (seconds)

    Returns:
        tuple: (coro, priority, interval)
    """
    async def update_display():
        if data_provider:
            data = await data_provider()
            if display and hasattr(display, 'update'):
                display.update(data)

    return (update_display, Task.PRIORITY_LOW, interval)


def create_data_logging_task(sd_card, data_provider, filename, interval=1.0):
    """
    สร้าง task สำหรับบันทึกข้อมูล
    Create data logging task

    Args:
        sd_card: SDCardManager object
        data_provider: async function() ที่คืนค่าข้อมูลสำหรับบันทึก
        filename: ชื่อไฟล์ CSV
        interval: ช่วงเวลาบันทึก (seconds)

    Returns:
        tuple: (coro, priority, interval)
    """
    async def log_data():
        if data_provider and sd_card:
            data = await data_provider()
            if data:
                sd_card.append_csv_row(filename, data)

    return (log_data, Task.PRIORITY_BACKGROUND, interval)


# ==============================================================================
# ตัวอย่างการใช้งาน (Usage Example)
# ==============================================================================
if __name__ == '__main__':
    print("=" * 50)
    print("ทดสอบ TaskScheduler (Testing TaskScheduler)")
    print("=" * 50)

    # ทดสอบ Mock tasks (Mock test)
    async def mock_sensor_task():
        """Mock sensor reading"""
        print("  [Mock] Reading sensor...")
        await asyncio.sleep(0.1)
        return 7.0

    async def mock_display_task():
        """Mock display update"""
        print("  [Mock] Updating display...")
        await asyncio.sleep(0.05)

    async def mock_pump_task():
        """Mock pump control"""
        print("  [Mock] Pumping...")
        await asyncio.sleep(0.2)

    async def test_scheduler():
        """ทดสอบ TaskScheduler (Test TaskScheduler)"""
        scheduler = TaskScheduler()

        # เพิ่ม tasks (Add tasks)
        scheduler.add_task("sensor", mock_sensor_task,
                          priority=Task.PRIORITY_HIGH, interval=0.5)
        scheduler.add_task("display", mock_display_task,
                          priority=Task.PRIORITY_LOW, interval=0.3)
        scheduler.add_task("pump", mock_pump_task,
                          priority=Task.PRIORITY_MEDIUM, interval=None)

        # แสดงรายการ tasks (List tasks)
        print(f"\nTasks: {scheduler.list_tasks()}")

        # เริ่มการทำงาน (Start scheduler)
        await scheduler.start()

        # รอสักครู่ (Wait a moment)
        print("\nรอ 2 วินาที (Waiting 2 seconds)...")
        await asyncio.sleep(2)

        # แสดงสถิติ (Show stats)
        print("\nสถิติ (Statistics):")
        stats = scheduler.get_stats()
        for name, stat in stats.items():
            print(f"  {name}: run_count={stat['run_count']}")

        # หยุดการทำงาน (Stop scheduler)
        await scheduler.stop()

    # รันทดสอบ (Run test)
    try:
        asyncio.run(test_scheduler())
        print("\nทดสอบสำเร็จ (Test passed)")
    except Exception as e:
        print(f"\nข้อผิดพลาด (Error): {e}")

    print("\n" + "=" * 50)
    print("ตัวอย่างการใช้งานจริง (Real usage example):")
    print("=" * 50)
    print("""
    import uasyncio as asyncio
    from async_support.scheduler import TaskScheduler, Task

    # สร้าง scheduler (Create scheduler)
    scheduler = TaskScheduler()

    # เพิ่ม tasks (Add tasks)
    scheduler.add_task(
        "ph_sensor",
        ph_sensor.read_ph_async,
        priority=Task.PRIORITY_HIGH,
        interval=1.0
    )

    scheduler.add_task(
        "display",
        update_display_async,
        priority=Task.PRIORITY_LOW,
        interval=0.5
    )

    # รัน scheduler (Run scheduler)
    async def main():
        await scheduler.start()

        # ทำงานอื่นๆ ระหว่าง tasks ทำงาน
        # Do other work while tasks run
        await asyncio.sleep(60)

        await scheduler.stop()

    asyncio.run(main())
    """)
