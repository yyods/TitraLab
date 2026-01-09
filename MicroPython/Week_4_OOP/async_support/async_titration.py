# ==============================================================================
# async_titration.py - ไทเทรชันแบบ Asynchronous (Asynchronous Titration)
# ==============================================================================
# โมดูลนี้ให้การควบคุมไทเทรชันแบบ non-blocking ด้วย uasyncio
# This module provides non-blocking titration control using uasyncio
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
# 1. เรียนรู้การจัดการหลาย tasks พร้อมกัน (Concurrent task management)
# 2. เข้าใจ asyncio.gather() และ asyncio.create_task()
# 3. ประสานการทำงานระหว่าง pump, sensor, display (Coordinate pump, sensor, display)
#
# ข้อดีของ Async Titration (Benefits of Async Titration):
# - อ่านเซ็นเซอร์พร้อมเติมสารละลาย (Read sensors while dispensing)
# - อัปเดตจอแสดงผลแบบ real-time (Real-time display updates)
# - ตอบสนองต่อปุ่มหยุดทันที (Immediate response to stop button)
# ==============================================================================

import uasyncio as asyncio
import time

from .async_pump import AsyncPump


class AsyncTitrationController:
    """
    คลาสควบคุมการไทเทรชันแบบ asynchronous
    Asynchronous titration controller class

    คุณสมบัติ (Features):
    - เติมสารละลายแบบ non-blocking (Non-blocking dispensing)
    - อ่านเซ็นเซอร์พร้อมกัน (Concurrent sensor reading)
    - ตรวจจับจุดสมมูล real-time (Real-time equivalence point detection)
    - รองรับการยกเลิกทันที (Supports immediate cancellation)
    """

    # ค่าคงที่สำหรับการไทเทรชัน (Titration constants)
    DEFAULT_DOSE_VOLUME = 0.1      # ปริมาตรต่อครั้ง (mL per dose)
    DEFAULT_STABILIZE_TIME = 2.0  # เวลารอให้คงที่ (seconds to stabilize)
    DEFAULT_MAX_VOLUME = 50.0     # ปริมาตรสูงสุด (maximum volume mL)

    # CSV Header สำหรับบันทึกข้อมูล (CSV Header for data logging)
    CSV_HEADERS = ['Cycle', 'Time(s)', 'Volume(mL)', 'pH', 'Temperature(C)']

    def __init__(self, pump, ph_sensor, temp_sensor=None, sd_card=None,
                 display=None, buzzer=None):
        """
        กำหนดค่าเริ่มต้น AsyncTitrationController
        Initialize AsyncTitrationController

        Args:
            pump: ออบเจ็กต์ควบคุมปั๊ม (Pump controller object)
            ph_sensor: ออบเจ็กต์เซ็นเซอร์ pH (pH sensor object)
            temp_sensor: ออบเจ็กต์เซ็นเซอร์อุณหภูมิ (Temperature sensor, optional)
            sd_card: ออบเจ็กต์ SD Card Manager (SD Card manager, optional)
            display: ออบเจ็กต์จอแสดงผล (Display object, optional)
            buzzer: ออบเจ็กต์ Buzzer (Buzzer object, optional)
        """
        # สร้าง AsyncPump wrapper (Create AsyncPump wrapper)
        self.async_pump = AsyncPump(pump)
        self.ph_sensor = ph_sensor
        self.temp_sensor = temp_sensor

        # อุปกรณ์เสริม (Optional hardware)
        self.sd_card = sd_card
        self.display = display
        self.buzzer = buzzer

        # ข้อมูลการไทเทรชัน (Titration data)
        self.data_points = []       # รายการข้อมูล [(volume, pH, temp, time), ...]
        self.current_volume = 0.0   # ปริมาตรรวม (total volume)
        self.start_time = 0         # เวลาเริ่มต้น (start time)
        self.cycle_count = 0        # จำนวนรอบ (cycle count)

        # ผลลัพธ์การวิเคราะห์ (Analysis results)
        self.equivalence_point = None  # จุดสมมูล (volume, pH)
        self.max_derivative = 0.0      # ค่า derivative สูงสุด

        # ค่าตั้งการทำงาน (Operation settings)
        self.dose_volume = self.DEFAULT_DOSE_VOLUME
        self.stabilize_time = self.DEFAULT_STABILIZE_TIME
        self.max_volume = self.DEFAULT_MAX_VOLUME

        # สถานะการทำงาน (Operation state)
        self._is_running = False
        self._should_stop = False
        self._current_filename = None

        # ค่าล่าสุด (Latest readings)
        self._latest_ph = 7.0
        self._latest_temp = 25.0

    def configure(self, dose_volume=None, stabilize_time=None, max_volume=None):
        """
        ตั้งค่าพารามิเตอร์การไทเทรชัน
        Configure titration parameters

        Args:
            dose_volume: ปริมาตรต่อครั้ง (mL per dose)
            stabilize_time: เวลารอให้คงที่ (seconds)
            max_volume: ปริมาตรสูงสุด (maximum mL)
        """
        if dose_volume is not None:
            self.dose_volume = dose_volume
        if stabilize_time is not None:
            self.stabilize_time = stabilize_time
        if max_volume is not None:
            self.max_volume = max_volume

    def reset(self):
        """
        รีเซ็ตข้อมูลการไทเทรชัน
        Reset titration data
        """
        self.data_points = []
        self.current_volume = 0.0
        self.start_time = 0
        self.cycle_count = 0
        self.equivalence_point = None
        self.max_derivative = 0.0
        self._is_running = False
        self._should_stop = False
        self._current_filename = None

    async def _read_ph_async(self):
        """
        อ่านค่า pH แบบ async
        Read pH value asynchronously
        """
        if self.ph_sensor:
            # อ่านค่า pH (อาจใช้เวลา) (Read pH - may take time)
            self._latest_ph = self.ph_sensor.read_ph()
        return self._latest_ph

    async def _read_temp_async(self):
        """
        อ่านค่าอุณหภูมิแบบ async
        Read temperature asynchronously
        """
        if self.temp_sensor:
            try:
                self._latest_temp = self.temp_sensor.read_temperature()
            except Exception:
                self._latest_temp = 25.0
        return self._latest_temp

    async def _read_all_sensors_async(self):
        """
        อ่านเซ็นเซอร์ทั้งหมดพร้อมกัน
        Read all sensors concurrently

        Returns:
            tuple: (pH, temperature)
        """
        # อ่านเซ็นเซอร์พร้อมกัน (Read sensors concurrently)
        results = await asyncio.gather(
            self._read_ph_async(),
            self._read_temp_async()
        )
        return results

    async def _update_display_async(self, cycle, volume, ph, temperature):
        """
        อัปเดตจอแสดงผลแบบ async
        Update display asynchronously
        """
        if self.display:
            try:
                if hasattr(self.display, 'show_titration_status'):
                    self.display.show_titration_status(cycle, volume, ph, temperature)
            except Exception as e:
                print(f"Display error: {e}")

        # yield เพื่อให้ tasks อื่นทำงาน (Yield for other tasks)
        await asyncio.sleep(0)

    async def _log_data_async(self, cycle, elapsed_time, volume, ph, temperature):
        """
        บันทึกข้อมูลแบบ async
        Log data asynchronously
        """
        # เก็บในหน่วยความจำ (Store in memory)
        self.data_points.append({
            'cycle': cycle,
            'time': elapsed_time,
            'volume': volume,
            'ph': ph,
            'temperature': temperature
        })

        # บันทึกลง SD Card (Log to SD Card)
        if self.sd_card and self._current_filename:
            data_row = [cycle, f"{elapsed_time:.2f}", f"{volume:.3f}",
                       f"{ph:.3f}", f"{temperature:.2f}"]
            self.sd_card.append_csv_row(self._current_filename, data_row)

        # yield เพื่อให้ tasks อื่นทำงาน (Yield for other tasks)
        await asyncio.sleep(0)

    def calculate_derivative(self, index):
        """
        คำนวณ derivative (dpH/dV) ณ จุดที่กำหนด
        Calculate derivative (dpH/dV) at given index
        """
        if index < 1 or index >= len(self.data_points):
            return 0.0

        current = self.data_points[index]
        previous = self.data_points[index - 1]

        delta_v = current['volume'] - previous['volume']
        delta_ph = current['ph'] - previous['ph']

        if abs(delta_v) < 0.0001:
            return 0.0

        return delta_ph / delta_v

    def detect_equivalence_point(self):
        """
        หาจุดสมมูลด้วยวิธี derivative
        Detect equivalence point using derivative method
        """
        if len(self.data_points) < 3:
            return None

        max_abs_derivative = 0.0
        equivalence_index = -1

        for i in range(1, len(self.data_points)):
            derivative = self.calculate_derivative(i)
            abs_derivative = abs(derivative)

            if abs_derivative > max_abs_derivative:
                max_abs_derivative = abs_derivative
                equivalence_index = i
                self.max_derivative = derivative

        if equivalence_index > 0:
            eq_point = self.data_points[equivalence_index]
            self.equivalence_point = (eq_point['volume'], eq_point['ph'])
            return self.equivalence_point

        return None

    def stop(self):
        """
        หยุดการไทเทรชัน
        Stop titration
        """
        self._should_stop = True
        self.async_pump.stop()
        print("กำลังหยุดการไทเทรชัน... (Stopping titration...)")

    @property
    def is_running(self):
        """
        ตรวจสอบสถานะการทำงาน
        Check running status
        """
        return self._is_running

    async def run_titration_async(self, auto_detect=True, on_cycle_complete=None):
        """
        ดำเนินการไทเทรชันแบบ asynchronous
        Run asynchronous titration

        Args:
            auto_detect: หาจุดสมมูลอัตโนมัติและหยุด (auto detect and stop)
            on_cycle_complete: async callback หลังแต่ละรอบ
                               async def callback(cycle, volume, ph, temp, derivative) -> bool
                               Return False เพื่อหยุด

        Returns:
            dict: ผลลัพธ์การไทเทรชัน (Titration results)
        """
        # เตรียมการเริ่มต้น (Initialize)
        self.reset()
        self._is_running = True
        self.start_time = time.ticks_ms()

        # สร้างไฟล์บันทึกข้อมูล (Create data file)
        if self.sd_card:
            self._current_filename = self.sd_card.get_next_version('titration_data')
            self.sd_card.write_csv_header(self._current_filename, self.CSV_HEADERS)

        print("=" * 50)
        print("เริ่มการไทเทรชัน Async (Starting Async Titration)")
        print("=" * 50)

        # อ่านค่าเริ่มต้น (Read initial values)
        ph_value, temp_value = await self._read_all_sensors_async()
        await self._log_data_async(0, 0.0, 0.0, ph_value, temp_value)
        await self._update_display_async(0, 0.0, ph_value, temp_value)

        previous_derivative = 0.0

        try:
            # ลูปการไทเทรชันหลัก (Main titration loop)
            while not self._should_stop and self.current_volume < self.max_volume:
                self.cycle_count += 1

                # สร้าง tasks สำหรับทำงานพร้อมกัน (Create concurrent tasks)
                # 1. เติมสารละลาย (Dispense titrant)
                dispense_task = asyncio.create_task(
                    self.async_pump.pump_volume_async(self.dose_volume)
                )

                # รอการเติมสำเร็จ (Wait for dispense to complete)
                dispensed = await dispense_task
                self.current_volume += dispensed

                # รอให้คงที่ (Wait for stabilization)
                await asyncio.sleep(self.stabilize_time)

                # อ่านเซ็นเซอร์พร้อมกัน (Read sensors concurrently)
                ph_value, temp_value = await self._read_all_sensors_async()

                # คำนวณเวลาที่ผ่านไป (Calculate elapsed time)
                elapsed_time = time.ticks_diff(time.ticks_ms(), self.start_time) / 1000.0

                # บันทึกข้อมูลและอัปเดตจอแสดงผลพร้อมกัน (Log and update display concurrently)
                await asyncio.gather(
                    self._log_data_async(self.cycle_count, elapsed_time,
                                        self.current_volume, ph_value, temp_value),
                    self._update_display_async(self.cycle_count, self.current_volume,
                                              ph_value, temp_value)
                )

                # คำนวณ derivative (Calculate derivative)
                derivative = self.calculate_derivative(len(self.data_points) - 1)

                # แสดงข้อมูลใน console (Print to console)
                print(f"Cycle {self.cycle_count:3d}: V={self.current_volume:6.2f}mL, "
                      f"pH={ph_value:5.2f}, dpH/dV={derivative:+7.3f}")

                # ตรวจจับจุดสมมูลอัตโนมัติ (Auto-detect equivalence point)
                if auto_detect and len(self.data_points) > 3:
                    if abs(derivative) < abs(previous_derivative) * 0.5:
                        if abs(previous_derivative) > 0.5:
                            print("\nตรวจพบจุดสมมูล! (Equivalence point detected!)")
                            # เติมอีกเล็กน้อยเพื่อยืนยัน (Add more to confirm)
                            for _ in range(3):
                                self.cycle_count += 1
                                dispensed = await self.async_pump.pump_volume_async(self.dose_volume)
                                self.current_volume += dispensed
                                await asyncio.sleep(self.stabilize_time)
                                ph_value, temp_value = await self._read_all_sensors_async()
                                elapsed_time = time.ticks_diff(time.ticks_ms(), self.start_time) / 1000.0
                                await self._log_data_async(self.cycle_count, elapsed_time,
                                                          self.current_volume, ph_value, temp_value)
                            break

                previous_derivative = derivative

                # เรียก callback ถ้ามี (Call callback if provided)
                if on_cycle_complete:
                    should_continue = await on_cycle_complete(
                        self.cycle_count, self.current_volume,
                        ph_value, temp_value, derivative
                    )
                    if not should_continue:
                        print("หยุดโดย callback (Stopped by callback)")
                        break

        except asyncio.CancelledError:
            print("ไทเทรชันถูกยกเลิก (Titration cancelled)")

        except Exception as e:
            print(f"ข้อผิดพลาดระหว่างไทเทรชัน (Error during titration): {e}")

        finally:
            self._is_running = False
            self.async_pump.stop()

        # วิเคราะห์หาจุดสมมูล (Analyze for equivalence point)
        self.detect_equivalence_point()

        # ส่งเสียงเตือนเสร็จสิ้น (Beep to indicate completion)
        if self.buzzer:
            try:
                self.buzzer.beep(frequency=1000, duration_ms=500)
            except Exception:
                pass

        # สรุปผลลัพธ์ (Summary)
        results = {
            'total_cycles': self.cycle_count,
            'total_volume': self.current_volume,
            'total_time': time.ticks_diff(time.ticks_ms(), self.start_time) / 1000.0,
            'data_points': len(self.data_points),
            'equivalence_point': self.equivalence_point,
            'filename': self._current_filename
        }

        print("\n" + "=" * 50)
        print("การไทเทรชัน Async เสร็จสิ้น (Async Titration Complete)")
        print("=" * 50)

        return results

    def save_results(self, filename=None):
        """
        บันทึกผลลัพธ์การไทเทรชันลงไฟล์ CSV
        Save titration results to CSV file
        """
        if not self.sd_card:
            print("ข้อผิดพลาด: ไม่มี SD Card (Error: No SD Card)")
            return None

        if not self.data_points:
            print("ข้อผิดพลาด: ไม่มีข้อมูลให้บันทึก (Error: No data to save)")
            return None

        if filename is None:
            filename = self.sd_card.get_next_version('titration_data')

        if not self.sd_card.write_csv_header(filename, self.CSV_HEADERS):
            return None

        for point in self.data_points:
            data_row = [
                point['cycle'],
                f"{point['time']:.2f}",
                f"{point['volume']:.3f}",
                f"{point['ph']:.3f}",
                f"{point['temperature']:.2f}"
            ]
            self.sd_card.append_csv_row(filename, data_row)

        if self.equivalence_point:
            summary = f"# Equivalence Point: Volume={self.equivalence_point[0]:.3f}mL, pH={self.equivalence_point[1]:.3f}"
            self.sd_card.append_csv_row(filename, [summary])

        print(f"บันทึกผลลัพธ์ที่: {filename} (Results saved to: {filename})")
        return filename


# ==============================================================================
# ตัวอย่างการใช้งาน (Usage Example)
# ==============================================================================
if __name__ == '__main__':
    print("=" * 50)
    print("ทดสอบ AsyncTitrationController")
    print("Testing AsyncTitrationController")
    print("=" * 50)
    print("\nตัวอย่างการใช้งาน (Usage example):")
    print("""
    import uasyncio as asyncio
    from hardware.pump import Pump
    from hardware.ph_sensor import PHSensor
    from async_support.async_titration import AsyncTitrationController

    # สร้าง hardware (Create hardware)
    pump = Pump()
    pump.init()

    ph_sensor = PHSensor()
    ph_sensor.init()

    # สร้าง AsyncTitrationController (Create controller)
    titration = AsyncTitrationController(
        pump=pump,
        ph_sensor=ph_sensor
    )

    # ตั้งค่าพารามิเตอร์ (Configure parameters)
    titration.configure(
        dose_volume=0.1,
        stabilize_time=2.0,
        max_volume=25.0
    )

    # Callback function (optional)
    async def on_cycle(cycle, volume, ph, temp, derivative):
        print(f"Cycle {cycle}: {volume:.2f}mL, pH={ph:.2f}")
        return True  # Continue

    # รัน async titration (Run async titration)
    async def main():
        results = await titration.run_titration_async(
            auto_detect=True,
            on_cycle_complete=on_cycle
        )
        print(f"เสร็จสิ้น! จุดสมมูล: {results['equivalence_point']}")

    asyncio.run(main())
    """)
