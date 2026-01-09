# ==============================================================================
# async_pump.py - ควบคุมปั๊มแบบ Asynchronous (Asynchronous Pump Control)
# ==============================================================================
# โมดูลนี้ให้การควบคุมปั๊มแบบ non-blocking ด้วย uasyncio
# This module provides non-blocking pump control using uasyncio
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
# 1. เรียนรู้การแปลง synchronous code เป็น asynchronous
# 2. เข้าใจ async/await pattern
# 3. ใช้ asyncio.sleep() แทน time.sleep()
#
# ข้อดีของ Async Pump (Benefits of Async Pump):
# - ไม่บล็อกการทำงานอื่นขณะเติมสารละลาย (Non-blocking during dispensing)
# - สามารถอ่านเซ็นเซอร์พร้อมกันได้ (Can read sensors concurrently)
# - ตอบสนองปุ่มกดได้แม้ระหว่างทำงาน (Responsive to buttons during operation)
#
# Hardware Configuration:
# - Pump: GPIO21 (PWM)
# ==============================================================================

import uasyncio as asyncio


class AsyncPump:
    """
    คลาส wrapper สำหรับควบคุมปั๊มแบบ asynchronous
    Asynchronous wrapper class for pump control

    คุณสมบัติ (Features):
    - pump_volume_async(): เติมสารละลายแบบ non-blocking
    - รองรับการยกเลิกกลางคัน (Supports cancellation)
    - callback เมื่อเสร็จสิ้น (Completion callback)
    """

    def __init__(self, pump):
        """
        กำหนดค่าเริ่มต้น AsyncPump
        Initialize AsyncPump

        Args:
            pump: ออบเจ็กต์ Pump ที่จะ wrap (Pump object to wrap)
        """
        self._pump = pump
        self._is_running = False
        self._should_stop = False
        self._current_task = None

    @property
    def pump(self):
        """
        เข้าถึง Pump object ตัวจริง
        Access underlying Pump object
        """
        return self._pump

    @property
    def is_running(self):
        """
        ตรวจสอบสถานะการทำงาน
        Check running status
        """
        return self._is_running

    def stop(self):
        """
        หยุดการทำงานของปั๊ม
        Stop pump operation
        """
        self._should_stop = True
        if self._pump:
            self._pump.stop()

    async def pump_volume_async(self, volume_ml, callback=None):
        """
        เติมสารละลายตามปริมาตรที่กำหนด (แบบ async)
        Dispense specified volume asynchronously

        Args:
            volume_ml: ปริมาตรที่ต้องการเติม (mL to dispense)
            callback: ฟังก์ชันเรียกกลับเมื่อเสร็จ (Completion callback)
                      callback(actual_volume, success)

        Returns:
            float: ปริมาตรที่เติมจริง (Actual volume dispensed)

        ตัวอย่างการใช้งาน (Usage Example):
            async def main():
                async_pump = AsyncPump(pump)
                volume = await async_pump.pump_volume_async(1.0)
                print(f"Dispensed {volume} mL")
        """
        if not self._pump:
            print("ข้อผิดพลาด: ไม่มี Pump object (Error: No Pump object)")
            return 0.0

        self._is_running = True
        self._should_stop = False
        actual_volume = 0.0

        try:
            # ดึงค่า flow rate จาก pump (Get flow rate from pump)
            flow_rate = getattr(self._pump, 'flow_rate', 1.0)  # mL/s

            # คำนวณเวลาที่ต้องการ (Calculate required time)
            duration_s = volume_ml / flow_rate

            # แบ่งเป็นช่วงเล็กๆ สำหรับการตรวจสอบ (Split into small intervals)
            interval_s = 0.1  # 100ms ต่อช่วง (100ms per interval)
            volume_per_interval = flow_rate * interval_s

            # เริ่มการทำงานของปั๊ม (Start pump)
            self._pump.start()

            elapsed = 0.0
            while elapsed < duration_s and not self._should_stop:
                # รอแบบ non-blocking (Non-blocking wait)
                await asyncio.sleep(interval_s)
                elapsed += interval_s
                actual_volume += volume_per_interval

                # ป้องกันการเติมเกิน (Prevent over-dispensing)
                if actual_volume >= volume_ml:
                    actual_volume = volume_ml
                    break

        except asyncio.CancelledError:
            # ถูกยกเลิก (Was cancelled)
            print("การเติมสารละลายถูกยกเลิก (Dispensing cancelled)")

        except Exception as e:
            print(f"ข้อผิดพลาด (Error): {e}")

        finally:
            # หยุดปั๊ม (Stop pump)
            self._pump.stop()
            self._is_running = False

        # เรียก callback ถ้ามี (Call callback if provided)
        if callback:
            success = not self._should_stop and actual_volume >= volume_ml * 0.95
            callback(actual_volume, success)

        return actual_volume

    async def purge_async(self, duration_s=5.0):
        """
        ล้างท่อแบบ async
        Purge tubing asynchronously

        Args:
            duration_s: เวลาล้าง (purge duration in seconds)
        """
        self._is_running = True
        self._should_stop = False

        try:
            print(f"กำลังล้างท่อ {duration_s} วินาที (Purging for {duration_s} seconds)")
            self._pump.start()

            # รอแบบ non-blocking (Non-blocking wait)
            elapsed = 0.0
            while elapsed < duration_s and not self._should_stop:
                await asyncio.sleep(0.1)
                elapsed += 0.1

        except asyncio.CancelledError:
            print("การล้างท่อถูกยกเลิก (Purge cancelled)")

        finally:
            self._pump.stop()
            self._is_running = False

        print("ล้างท่อเสร็จสิ้น (Purge complete)")

    async def dispense_drops_async(self, num_drops, drop_volume=0.05, delay_between=0.5):
        """
        เติมสารละลายทีละหยด (แบบ async)
        Dispense drops asynchronously

        Args:
            num_drops: จำนวนหยด (number of drops)
            drop_volume: ปริมาตรต่อหยด (mL per drop)
            delay_between: หน่วงระหว่างหยด (seconds between drops)

        Returns:
            int: จำนวนหยดที่เติม (Number of drops dispensed)
        """
        self._is_running = True
        self._should_stop = False
        drops_dispensed = 0

        try:
            for i in range(num_drops):
                if self._should_stop:
                    break

                # เติมหนึ่งหยด (Dispense one drop)
                await self.pump_volume_async(drop_volume)
                drops_dispensed += 1

                # หน่วงระหว่างหยด (Delay between drops)
                if i < num_drops - 1:  # ไม่หน่วงหลังหยดสุดท้าย
                    await asyncio.sleep(delay_between)

        except asyncio.CancelledError:
            print("การหยดถูกยกเลิก (Dropping cancelled)")

        finally:
            self._is_running = False

        return drops_dispensed

    def cancel(self):
        """
        ยกเลิก task ปัจจุบัน
        Cancel current task
        """
        self._should_stop = True
        if self._current_task:
            self._current_task.cancel()


# ==============================================================================
# ตัวอย่างการใช้งาน (Usage Example)
# ==============================================================================
if __name__ == '__main__':
    print("=" * 50)
    print("ทดสอบ AsyncPump (Testing AsyncPump)")
    print("=" * 50)
    print("\nตัวอย่างการใช้งาน (Usage example):")
    print("""
    import uasyncio as asyncio
    from hardware.pump import Pump
    from async_support.async_pump import AsyncPump

    # สร้าง Pump และ AsyncPump (Create Pump and AsyncPump)
    pump = Pump()
    pump.init()
    async_pump = AsyncPump(pump)

    async def main():
        # เติม 1.0 mL แบบ async (Dispense 1.0 mL asynchronously)
        volume = await async_pump.pump_volume_async(1.0)
        print(f"เติมได้ {volume:.2f} mL (Dispensed {volume:.2f} mL)")

        # เติมทีละหยด (Dispense drops)
        drops = await async_pump.dispense_drops_async(5, drop_volume=0.05)
        print(f"เติมได้ {drops} หยด (Dispensed {drops} drops)")

    # รัน async function (Run async function)
    asyncio.run(main())
    """)

    # ทดสอบ mock (Mock test)
    class MockPump:
        """Mock Pump for testing"""
        flow_rate = 1.0

        def start(self):
            print("  [Mock] Pump started")

        def stop(self):
            print("  [Mock] Pump stopped")

    async def test_async_pump():
        """ทดสอบ AsyncPump (Test AsyncPump)"""
        mock_pump = MockPump()
        async_pump = AsyncPump(mock_pump)

        print("\nทดสอบ pump_volume_async() (Testing pump_volume_async())...")
        volume = await async_pump.pump_volume_async(0.3)
        print(f"  ผลลัพธ์: {volume:.2f} mL (Result: {volume:.2f} mL)")

    # รันทดสอบ (Run test)
    try:
        asyncio.run(test_async_pump())
        print("\nทดสอบสำเร็จ (Test passed)")
    except Exception as e:
        print(f"\nข้อผิดพลาด (Error): {e}")
