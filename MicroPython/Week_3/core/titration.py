# ==============================================================================
# titration.py - คลาสควบคุมการไทเทรชันอัตโนมัติ (Automatic Titration Controller)
# ==============================================================================
# โมดูลนี้ควบคุมกระบวนการไทเทรชันแบบอัตโนมัติทั้งหมด
# This module controls the complete automatic titration process
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
# 1. เรียนรู้หลักการไทเทรชันกรด-เบส (acid-base titration)
# 2. เข้าใจการหาจุดสมมูล (equivalence point) ด้วยวิธี derivative
# 3. บันทึกและวิเคราะห์ข้อมูลการทดลอง (data logging and analysis)
#
# หลักการทางเคมี (Chemistry Principles):
# - จุดสมมูล (equivalence point) คือจุดที่กรดและเบสทำปฏิกิริยาพอดี
# - วิธี derivative: หาจุดที่ dpH/dV มีค่าสูงสุด
# - ที่จุดสมมูล การเปลี่ยนแปลง pH ต่อปริมาตรจะมากที่สุด
# ==============================================================================

import time
import gc


class TitrationController:
    """
    คลาสควบคุมการไทเทรชันอัตโนมัติ
    Automatic titration controller class

    อัลกอริทึม - Constant Dose Volume (Algorithm):
    ใช้ปริมาตรคงที่ 0.2 mL ต่อ step ตลอดทั้งการไทเทรต (ปั๊มที่ 100% เสมอ):
      สูบ 0.2 mL → หยุด → รอ 2 วินาที → อ่าน pH → ทำซ้ำ

    เหตุผลทางการเรียนรู้ (Pedagogical Rationale):
    - ทุกจุดบนกราฟห่างกัน 0.2 mL เท่ากัน ง่ายต่อการอ่านกราฟ
    - นิสิตตรวจสอบได้: total_volume = dose_count x 0.2 mL
    - เหมือนการไทเทรตมือ: "หยดสารไทแทรนต์ทีละหยด" แบบสม่ำเสมอ

    คุณสมบัติ (Features):
    - ควบคุมปั๊มเติมสารละลายทีละ 0.2 mL (Stepwise titrant pump control)
    - อ่านค่า pH แบบเรียลไทม์ (Real-time pH reading)
    - หาจุดสมมูลด้วยวิธี derivative (Equivalence point by derivative method)
    - บันทึกข้อมูลลง ESP32 flash storage (Data logging to ESP32 flash)

    หมายเหตุ: ไฟล์ CSV บันทึกใน ESP32 flash storage และดาวน์โหลดผ่าน Thonny IDE
    Note: CSV files saved to ESP32 flash storage and downloaded via Thonny IDE
    """

    # ค่าคงที่สำหรับการไทเทรชัน (Titration constants)
    # ใช้ปริมาตรคงที่ 0.2 mL ทุกครั้งเพื่อความเรียบง่ายในการเรียนรู้
    # Fixed 0.2 mL dose per step for pedagogical simplicity
    DEFAULT_DOSE_VOLUME = 0.2      # ปริมาตรคงที่ต่อครั้ง (Fixed mL per dose)
    DEFAULT_STABILIZE_TIME = 10.0  # เวลารอให้คงที่ (seconds to stabilize, pH needs 10-20s)
    DEFAULT_SAMPLE_VOLUME = 5.0    # ปริมาตรสารตัวอย่าง (sample volume mL)
    DEFAULT_PH_THRESHOLD = 0.01    # ค่า threshold สำหรับ pH คงที่

    # ปริมาตรเริ่มต้นสำหรับเตือนใกล้จุดสมมูล (Default volume for near-equivalence alert)
    # สำหรับการทดลอง HCl 0.1M 5mL + NaOH 0.1M → จุดสมมูลที่ 5.0 mL
    # For HCl 0.1M 5mL + NaOH 0.1M experiment → equivalence at 5.0 mL
    # หมายเหตุ: สามารถเปลี่ยนได้ผ่าน configure() (Note: configurable via configure())
    DEFAULT_ALERT_VOLUME_ML = 4.80  # ค่าเริ่มต้นเตือนที่ 4.80 mL (default alert at 4.80 mL)

    # CSV Header สำหรับบันทึกข้อมูล (CSV Header for data logging)
    # ชื่อคอลัมน์ตรงกับ EquivPoint analysis tool (Column names match EquivPoint)
    # "Volume (mL)" และ "pH Value" เป็นคอลัมน์หลักที่ EquivPoint ต้องการ
    CSV_HEADERS = ['Volume (mL)', 'pH Value', 'Cycle', 'Time(s)', 'Temperature(C)']

    def __init__(self, pump, ph_sensor, temp_sensor=None,
                 display=None, buzzer=None, led_indicator=None, buttons=None):
        """
        กำหนดค่าเริ่มต้น TitrationController
        Initialize TitrationController

        Args:
            pump: ออบเจ็กต์ควบคุมปั๊ม (Pump controller object)
            ph_sensor: ออบเจ็กต์เซ็นเซอร์ pH (pH sensor object)
            temp_sensor: ออบเจ็กต์เซ็นเซอร์อุณหภูมิ (Temperature sensor, optional)
            display: ออบเจ็กต์จอแสดงผล (Display object, optional)
            buzzer: ออบเจ็กต์ Buzzer (Buzzer object, optional)
            led_indicator: ออบเจ็กต์ LED แสดงสถานะ (LED indicator, optional)
            buttons: ออบเจ็กต์ปุ่มกด สำหรับ BTN3 ยกเลิก (Buttons for BTN3 cancel, optional)

        หมายเหตุ: ไม่ใช้ SD Card - ข้อมูลบันทึกใน ESP32 flash storage
        Note: SD Card NOT USED - data saved to ESP32 flash storage
        """
        # อุปกรณ์หลัก (Main hardware)
        self.pump = pump
        self.ph_sensor = ph_sensor
        self.temp_sensor = temp_sensor

        # อุปกรณ์เสริม (Optional hardware)
        self.display = display
        self.buzzer = buzzer
        self.led = led_indicator
        self.buttons = buttons  # สำหรับ BTN3 ยกเลิก (for BTN3 cancel)

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
        self.sample_volume = self.DEFAULT_SAMPLE_VOLUME
        # ปริมาตรสูงสุด = 2 เท่าของปริมาตรตัวอย่าง (Max = 2x sample volume)
        # เพื่อให้ได้กราฟ S-curve ที่สมบูรณ์ทั้งก่อนและหลังจุดสมมูล
        # For a complete S-curve with data before and after equivalence point
        self.max_volume = 2 * self.sample_volume
        # ปริมาตรสำหรับเตือนใกล้จุดสมมูล (Volume for near-equivalence alert)
        # สามารถเปลี่ยนได้ผ่าน configure() (configurable via configure())
        self.alert_volume = self.DEFAULT_ALERT_VOLUME_ML
        # จำนวน step ทั้งหมด คำนวณครั้งเดียวใน configure() (Total steps, calculated once in configure())
        self.total_steps = int(self.max_volume / self.dose_volume)

        # สถานะการทำงาน (Operation state)
        self._is_running = False
        self._should_stop = False
        self._current_filename = None

    def configure(self, dose_volume=None, stabilize_time=None, sample_volume=None,
                  alert_volume=None):
        """
        ตั้งค่าพารามิเตอร์การไทเทรชัน
        Configure titration parameters

        หมายเหตุ: max_volume คำนวณอัตโนมัติจาก 2 * sample_volume เสมอ
        Note: max_volume is always auto-calculated as 2 * sample_volume

        Args:
            dose_volume: ปริมาตรต่อครั้ง (mL per dose)
            stabilize_time: เวลารอให้คงที่ (seconds)
            sample_volume: ปริมาตรสารตัวอย่าง (sample volume mL)
                          max_volume จะถูกคำนวณเป็น 2 * sample_volume
                          max_volume is auto-calculated as 2 * sample_volume
            alert_volume: ปริมาตรสำหรับเตือนใกล้จุดสมมูล (mL)
                          (volume for near-equivalence alert)
                          ค่าเริ่มต้น: 4.80 mL (default: 4.80 mL)
        """
        if dose_volume is not None:
            self.dose_volume = dose_volume
        if stabilize_time is not None:
            self.stabilize_time = stabilize_time
        if sample_volume is not None:
            self.sample_volume = sample_volume
            # ปริมาตรสูงสุด = 2 เท่าของปริมาตรตัวอย่าง (Max = 2x sample volume)
            self.max_volume = 2 * self.sample_volume
        if alert_volume is not None:
            self.alert_volume = alert_volume

        # คำนวณจำนวน step ทั้งหมดและเก็บเป็น instance variable
        # Calculate total steps and store as instance variable
        # FIX: คำนวณครั้งเดียวเพื่อความสอดคล้อง (Calculate once for consistency)
        self.total_steps = int(self.max_volume / self.dose_volume)

        print(f"ตั้งค่าการไทเทรชัน (Titration configured):")
        print(f"  - ปริมาตรตัวอย่าง (Sample volume): {self.sample_volume} mL")
        print(f"  - ปริมาตรสูงสุด (Max volume): {self.max_volume} mL (2x sample)")
        print(f"  - ปริมาตรต่อครั้ง (Dose): {self.dose_volume} mL")
        print(f"  - จำนวน step ทั้งหมด (Total steps): {self.total_steps}")
        print(f"  - เวลารอ (Stabilize): {self.stabilize_time} s")
        print(f"  - ปริมาตรเตือน (Alert volume): {self.alert_volume} mL")

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

    def _read_sensors(self):
        """
        อ่านค่าจากเซ็นเซอร์ทั้งหมด
        Read values from all sensors

        Returns:
            tuple: (pH, temperature)
        """
        # อ่านค่า pH (Read pH value)
        ph_value = self.ph_sensor.read_ph() if self.ph_sensor else 7.0

        # อ่านค่าอุณหภูมิ (Read temperature)
        # FIX Issue #2: ใช้ read() แทน read_temperature() ตาม TemperatureSensor class
        # FIX Issue #14: เพิ่มคำเตือนเมื่อเซ็นเซอร์อุณหภูมิผิดพลาด
        temp_value = 25.0  # ค่าเริ่มต้น (default)
        if self.temp_sensor:
            try:
                # ใช้ read() method ตาม TemperatureSensor class (Use read() per TemperatureSensor class)
                temp_value = self.temp_sensor.read()
            except Exception as e:
                # FIX Issue #14: แสดงคำเตือนแทนการเงียบ (Show warning instead of silent failure)
                print(f"คำเตือน: เซ็นเซอร์อุณหภูมิผิดพลาด ({e}), ใช้ค่าเริ่มต้น 25.0°C")
                print(f"WARNING: Temp sensor error ({e}), using default 25.0°C")
                temp_value = 25.0

        return (ph_value, temp_value)

    def _dispense_titrant(self, volume_ml):
        """
        เติมสารละลายไทแทรนต์
        Dispense titrant solution

        Args:
            volume_ml: ปริมาตรที่จะเติม (volume to dispense in mL)

        หมายเหตุ (Note):
            FIX Issue #1: ปริมาตรรวมคำนวณจาก cycle_count * dose_volume
            แทนการสะสม += เพื่อหลีกเลี่ยงปัญหา floating-point drift
            Total volume calculated from cycle_count * dose_volume
            instead of += accumulation to avoid floating-point drift
        """
        if self.pump:
            # ใช้ run_for_volume ถ้ามี มิฉะนั้นใช้ pump_volume
            # Use run_for_volume if available, otherwise pump_volume
            if hasattr(self.pump, 'run_for_volume'):
                self.pump.run_for_volume(volume_ml)
            elif hasattr(self.pump, 'pump_volume'):
                self.pump.pump_volume(volume_ml)
            # FIX Issue #1: คำนวณปริมาตรจาก cycle_count แทนการสะสม +=
            # Calculate volume from cycle_count instead of += accumulation
            # เพื่อหลีกเลี่ยง floating-point drift (e.g., 50 x 0.2 = 9.999999 instead of 10.0)
            # To avoid floating-point drift
            self.current_volume = self.cycle_count * self.dose_volume

    def _log_data_point(self, cycle, elapsed_time, volume, ph, temperature):
        """
        บันทึกจุดข้อมูล
        Log data point

        Args:
            cycle: หมายเลขรอบ (cycle number)
            elapsed_time: เวลาที่ผ่านไป (elapsed time in seconds)
            volume: ปริมาตรรวม (total volume in mL)
            ph: ค่า pH (pH value)
            temperature: อุณหภูมิ (temperature in Celsius)
        """
        # เก็บในหน่วยความจำ (Store in memory)
        self.data_points.append({
            'cycle': cycle,
            'time': elapsed_time,
            'volume': volume,
            'ph': ph,
            'temperature': temperature
        })

        # บันทึกลง ESP32 flash storage (Log to ESP32 flash storage)
        # ลำดับคอลัมน์ตรงกับ EquivPoint: Volume, pH, Cycle, Time, Temperature
        if self._current_filename:
            try:
                data_row = f"{volume:.3f},{ph:.3f},{cycle},{elapsed_time:.2f},{temperature:.2f}\n"
                with open(self._current_filename, 'a') as f:
                    f.write(data_row)
                    # FIX Issue #5: flush เพื่อให้แน่ใจว่าข้อมูลถูกเขียนลง flash
                    # Flush to ensure data is written to flash
                    # ป้องกันการสูญหายของข้อมูลถ้าไฟดับ (Prevent data loss on power failure)
                    f.flush()
            except Exception as e:
                print(f"ข้อผิดพลาดบันทึกข้อมูล (Data logging error): {e}")

    def _update_display(self, cycle, volume, ph, temperature, derivative=None):
        """
        อัปเดตจอแสดงผล
        Update display

        Args:
            cycle: หมายเลขรอบ (cycle number)
            volume: ปริมาตร (volume in mL)
            ph: ค่า pH (pH value)
            temperature: อุณหภูมิ (temperature)
            derivative: ค่า dpH/dV (optional)
        """
        if self.display:
            try:
                gc.collect()  # ต้อง gc ก่อนทุกครั้งที่ใช้ display (GC before every display use)
                # ใช้ self.total_steps แทนการคำนวณซ้ำ (Use self.total_steps instead of recalculating)
                # ใช้เมธอด show_titration_status ถ้ามี
                # Use show_titration_status method if available
                if hasattr(self.display, 'show_titration_status'):
                    self.display.show_titration_status(
                        step=cycle,
                        total_steps=self.total_steps,
                        volume=volume,
                        max_volume=self.max_volume,
                        ph=ph,
                        temperature=temperature,
                        status_text="Titrating... BTN3:Cancel"
                    )
                else:
                    # แสดงผลพื้นฐาน (Basic display)
                    print(f"Cycle {cycle}: V={volume:.2f}mL, pH={ph:.2f}, T={temperature:.1f}C")
            except Exception as e:
                print(f"Display error: {e}")

    def calculate_derivative(self, index):
        """
        คำนวณ derivative (dpH/dV) ณ จุดที่กำหนด
        Calculate derivative (dpH/dV) at given index

        วิธีคำนวณ (Calculation Method):
        dpH/dV = (pH[i] - pH[i-1]) / (V[i] - V[i-1])

        Args:
            index: ตำแหน่งข้อมูล (data index)

        Returns:
            float: ค่า derivative (dpH/dV)
        """
        if index < 1 or index >= len(self.data_points):
            return 0.0

        current = self.data_points[index]
        previous = self.data_points[index - 1]

        delta_v = current['volume'] - previous['volume']
        delta_ph = current['ph'] - previous['ph']

        # ป้องกันหารด้วยศูนย์ (Prevent division by zero)
        # FIX Issue #4: เปลี่ยน threshold จาก 0.0001 เป็น 0.01 mL
        # Changed threshold from 0.0001 to 0.01 mL
        # 0.01 mL = 5% ของ dose 0.2 mL, ปลอดภัยจาก floating-point errors
        # 0.01 mL = 5% of 0.2 mL dose, safe from floating-point errors
        if abs(delta_v) < 0.01:
            return 0.0

        derivative = delta_ph / delta_v
        return derivative

    def detect_equivalence_point(self):
        """
        หาจุดสมมูลด้วยวิธี derivative
        Detect equivalence point using derivative method

        หลักการ (Principle):
        - จุดสมมูลคือจุดที่ |dpH/dV| มีค่าสูงสุด
        - การเปลี่ยนแปลง pH ต่อปริมาตรจะมากที่สุดที่จุดสมมูล
        - สำหรับการไทเทรตกรดด้วยเบส: dpH/dV จะเป็นบวกและสูงสุดที่จุดสมมูล

        Returns:
            tuple: (volume, pH) ที่จุดสมมูล หรือ None ถ้าไม่พบ
        """
        if len(self.data_points) < 3:
            print("ข้อมูลไม่เพียงพอสำหรับหาจุดสมมูล (Insufficient data for equivalence point)")
            return None

        max_abs_derivative = 0.0
        equivalence_index = -1

        # หาจุดที่ |dpH/dV| สูงสุด (Find maximum |dpH/dV|)
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

            print("=" * 50)
            print("พบจุดสมมูล! (Equivalence Point Found!)")
            print(f"  ปริมาตร (Volume): {eq_point['volume']:.3f} mL")
            print(f"  pH: {eq_point['ph']:.3f}")
            print(f"  dpH/dV สูงสุด (Max dpH/dV): {self.max_derivative:.3f}")
            print("=" * 50)

            return self.equivalence_point

        return None

    def _get_next_filename(self, base_name='titration_data'):
        """
        สร้างชื่อไฟล์ใหม่โดยเพิ่มหมายเลขเวอร์ชัน
        Generate new filename with version number

        Args:
            base_name: ชื่อไฟล์พื้นฐาน (base filename)

        Returns:
            str: ชื่อไฟล์ใหม่ เช่น titration_data_R1.csv
        """
        import os
        version = 1
        while True:
            filename = f"{base_name}_R{version}.csv"
            try:
                os.stat(filename)
                version += 1
            except OSError:
                return filename

    def save_results(self, filename=None):
        """
        บันทึกผลลัพธ์การไทเทรชันลงไฟล์ CSV ใน ESP32 flash storage
        Save titration results to CSV file in ESP32 flash storage

        หมายเหตุ: ไฟล์บันทึกใน ESP32 flash และดาวน์โหลดผ่าน Thonny IDE
        Note: Files saved to ESP32 flash and downloaded via Thonny IDE

        Args:
            filename: ชื่อไฟล์ (optional, auto-generated if not provided)

        Returns:
            str: ชื่อไฟล์ที่บันทึก หรือ None ถ้าล้มเหลว
        """
        if not self.data_points:
            print("ข้อผิดพลาด: ไม่มีข้อมูลให้บันทึก (Error: No data to save)")
            return None

        # สร้างชื่อไฟล์อัตโนมัติ (Auto-generate filename)
        if filename is None:
            filename = self._get_next_filename('titration_data')

        try:
            # เขียน header และข้อมูลทั้งหมด (Write header and all data)
            with open(filename, 'w') as f:
                # เขียน header (Write header)
                f.write(','.join(self.CSV_HEADERS) + '\n')

                # เขียนข้อมูลทั้งหมด (Write all data)
                # ลำดับคอลัมน์: Volume, pH, Cycle, Time, Temperature
                # Column order: Volume, pH, Cycle, Time, Temperature
                for point in self.data_points:
                    data_row = f"{point['volume']:.3f},{point['ph']:.3f},"
                    data_row += f"{point['cycle']},{point['time']:.2f},{point['temperature']:.2f}\n"
                    f.write(data_row)

                # เพิ่มบรรทัดสรุป (Add summary line)
                if self.equivalence_point:
                    summary = f"# Equivalence Point: Volume={self.equivalence_point[0]:.3f}mL, pH={self.equivalence_point[1]:.3f}\n"
                    f.write(summary)

            print(f"บันทึกผลลัพธ์ที่: {filename} (Results saved to: {filename})")
            print(f"ดาวน์โหลดไฟล์ผ่าน Thonny IDE (Download via Thonny IDE)")
            return filename

        except Exception as e:
            print(f"ข้อผิดพลาดบันทึกไฟล์ (Error saving file): {e}")
            return None

    def stop(self):
        """
        หยุดการไทเทรชัน
        Stop titration
        """
        self._should_stop = True
        print("กำลังหยุดการไทเทรชัน... (Stopping titration...)")

    def _wait_with_cancel(self, duration_s):
        """
        รอเวลาที่กำหนด พร้อมตรวจสอบ BTN3 ยกเลิก
        Wait for specified duration with BTN3 cancel check

        Args:
            duration_s: เวลาที่จะรอ (seconds)

        Returns:
            bool: True ถ้ารอครบ, False ถ้าถูกยกเลิก (True if completed, False if cancelled)
        """
        # รอด้วยการตรวจสอบ BTN3 ทุก 100ms
        # Wait with BTN3 check every 100ms
        wait_count = int(duration_s * 10)  # 100ms intervals
        for _ in range(wait_count):
            if self.buttons and self.buttons.is_pressed(3):
                self._should_stop = True
                return False
            time.sleep(0.1)
        return True

    @property
    def is_running(self):
        """
        ตรวจสอบสถานะการทำงาน
        Check running status
        """
        return self._is_running

    def run_titration(self, callback=None):
        """
        ดำเนินการไทเทรชันอัตโนมัติ - เก็บข้อมูลครบทุก step
        Run automatic titration - collect ALL data points

        หมายเหตุสำคัญ (Important Note):
        - ไทเทรชันจะทำงานจนครบทุก step (เช่น 50 step = 10.0 mL)
        - ไม่หยุดอัตโนมัติเมื่อพบจุดสมมูล
        - ข้อมูลทั้งหมดจะถูกวิเคราะห์ด้วย EquivPoint tool

        - Titration runs until ALL steps complete (e.g., 50 steps = 10.0 mL)
        - Does NOT stop automatically at equivalence point
        - All data analyzed with EquivPoint tool

        Args:
            callback: ฟังก์ชันเรียกกลับหลังแต่ละรอบ (callback function after each cycle)
                      callback(cycle, volume, ph, temperature, derivative) -> bool
                      Return False เพื่อหยุดการไทเทรชัน (Return False to stop)

        Returns:
            dict: ผลลัพธ์การไทเทรชัน (Titration results)
        """
        # ใช้ self.total_steps ที่คำนวณไว้ใน configure() แล้ว
        # Use self.total_steps already calculated in configure()
        print("\n" + "=" * 50)
        print("ไทเทรชันอัตโนมัติ (Auto Titration)")
        print("=" * 50)
        print(f"ปริมาตรตัวอย่าง (Sample): {self.sample_volume} mL")
        print(f"ปริมาตรสูงสุด (Max): {self.max_volume} mL (2x sample)")
        print(f"ปริมาตรต่อครั้ง (Dose): {self.dose_volume} mL")
        print(f"จำนวน step (Total steps): {self.total_steps}")
        print("-" * 50)

        # แสดงสถานะการสอบเทียบ (Show calibration status)
        # อัตราการไหล (Flow rate)
        if self.pump and hasattr(self.pump, 'flow_rate') and self.pump.flow_rate:
            print(f"อัตราการไหล (Flow rate): {self.pump.flow_rate:.4f} mL/s")
        else:
            print("อัตราการไหล (Flow rate): ค่าเริ่มต้น! (DEFAULT - not calibrated!)")

        # สมการ pH (pH calibration equation)
        if self.ph_sensor and hasattr(self.ph_sensor, 'slope') and hasattr(self.ph_sensor, 'intercept'):
            slope = self.ph_sensor.slope
            intercept = self.ph_sensor.intercept
            print(f"สมการ pH (pH equation): pH = {slope:.4f} * mV + {intercept:.4f}")
        else:
            print("สมการ pH (pH equation): ไม่พบข้อมูล! (NOT calibrated!)")

        print("-" * 50)
        print("กดปุ่ม 1 เริ่ม, ปุ่ม 3 ยกเลิก (BTN1:Start BTN3:Cancel)")

        # เก็บกวาดหน่วยความจำก่อนแสดงผล (GC before display - need 5120 bytes for buffer)
        gc.collect()

        # แสดงหน้าจอพร้อมเริ่ม (Show ready screen on TFT)
        if self.display:
            # เตรียมข้อมูลการสอบเทียบก่อนเรียก display
            # Prepare calibration data before calling display
            _flow = None
            _ph_eq = None
            try:
                if self.pump and hasattr(self.pump, 'flow_rate'):
                    _flow = self.pump.flow_rate
            except Exception:
                pass
            try:
                if self.ph_sensor and hasattr(self.ph_sensor, 'slope') and hasattr(self.ph_sensor, 'intercept'):
                    _ph_eq = (self.ph_sensor.slope, self.ph_sensor.intercept)
            except Exception:
                pass

            try:
                if hasattr(self.display, 'show_titration_ready'):
                    self.display.show_titration_ready(
                        sample_vol=self.sample_volume,
                        max_vol=self.max_volume,
                        dose_vol=self.dose_volume,
                        total_steps=self.total_steps,
                        flow_rate=_flow,
                        ph_equation=_ph_eq
                    )
                else:
                    self.display.show_message("Auto Titration", "BTN1:Start BTN3:Cancel")
            except TypeError as e:
                print(f"Display TypeError (fallback): {e}")
                try:
                    self.display.show_message("Auto Titration", "BTN1:Start BTN3:Cancel")
                except Exception:
                    pass
            except Exception as e:
                # ไม่ล้างจอ! ข้อมูลที่วาดบางส่วนดีกว่าไม่มีเลย
                # Do NOT clear screen! Partial content is better than nothing
                print(f"Display error (partial shown): {e}")

        # รอกดปุ่ม 1 เริ่ม หรือปุ่ม 3 ยกเลิก (Wait for BTN1 to start or BTN3 to cancel)
        if self.buttons:
            while True:
                if self.buttons.is_pressed(1):
                    time.sleep(0.2)  # Debounce
                    break
                if self.buttons.is_pressed(3):
                    # ยกเลิก (Cancel)
                    print("\n[CANCELLED] ยกเลิกการไทเทรชัน (Titration cancelled)")
                    gc.collect()
                    if self.display:
                        try:
                            self.display.show_message("Cancelled", "Returning to menu")
                        except MemoryError:
                            pass
                    if self.buzzer:
                        try:
                            self.buzzer.error_sound()
                        except:
                            pass
                    time.sleep(1.5)
                    return {'cancelled': True, 'total_cycles': 0, 'total_volume': 0}
                time.sleep(0.05)

        # เตรียมการเริ่มต้น (Initialize)
        self.reset()
        self._is_running = True
        self.start_time = time.ticks_ms()

        # สร้างไฟล์บันทึกข้อมูลใน ESP32 flash storage
        # Create data file in ESP32 flash storage
        try:
            self._current_filename = self._get_next_filename('titration_data')
            with open(self._current_filename, 'w') as f:
                f.write(','.join(self.CSV_HEADERS) + '\n')
            print(f"\nสร้างไฟล์: {self._current_filename} (File created)")
        except Exception as e:
            # FIX Issue #23: แสดงข้อผิดพลาดชัดเจนและเตือนผู้ใช้
            # Show clear error and warn user that data won't be saved
            print(f"ข้อผิดพลาด: ไม่สามารถสร้างไฟล์! (ERROR: Cannot create file!): {e}")
            self._current_filename = None
            # แสดงข้อความบนจอ (Show message on display)
            if self.display:
                try:
                    if hasattr(self.display, 'show_message'):
                        self.display.show_message("FILE ERROR!", "Data won't be saved")
                except Exception:
                    pass
            # ส่งเสียงเตือน (Play error sound)
            if self.buzzer:
                try:
                    if hasattr(self.buzzer, 'error_sound'):
                        self.buzzer.error_sound()
                    else:
                        # Fallback: เสียงเตือน 3 ครั้ง (3 warning beeps)
                        for _ in range(3):
                            self.buzzer.play_tone(500, 100)
                            time.sleep(0.1)
                except Exception:
                    pass
            # รอให้ผู้ใช้เห็นข้อความ (Wait for user to see message)
            time.sleep(2)
            # หมายเหตุ: ไทเทรชันจะดำเนินต่อแต่ไม่บันทึกข้อมูล
            # Note: Titration continues but data won't be saved
            print("คำเตือน: ไทเทรชันจะดำเนินต่อแต่ข้อมูลจะไม่ถูกบันทึก!")
            print("WARNING: Titration will continue but data will NOT be saved!")

        print("\n" + "=" * 50)
        print("เริ่มการไทเทรชัน! (Starting Titration!)")
        print("กดปุ่ม 3 เพื่อหยุด (Press BTN3 to stop)")
        print("=" * 50)

        # เปิด LED แสดงสถานะทำงาน (Turn on working status LED)
        if self.led:
            self.led.on()

        # ส่งเสียงเริ่มต้น (Beep to start)
        if self.buzzer:
            try:
                self.buzzer.beep()
            except:
                pass

        # อ่านค่าเริ่มต้นก่อนเติมสารละลาย (Read initial values at 0 mL)
        # นี่คือจุดเริ่มต้น: ยังไม่มีการหยดสารละลาย (Starting point: no titrant added yet)
        print(f"\n[Step 0] อ่านค่าเริ่มต้น (Reading initial values)...")
        ph_value, temp_value = self._read_sensors()
        self._log_data_point(0, 0.0, 0.0, ph_value, temp_value)
        self._update_display(0, 0.0, ph_value, temp_value)
        print(f"         pH เริ่มต้น = {ph_value:.2f} (Initial pH)")

        # รอให้ pH เริ่มต้นคงที่ก่อนเริ่มหยด (Wait for initial pH to stabilize before first dose)
        # FIX Bug 1: เพิ่มการรอก่อนหยดแรก (Add wait before first dose)
        print(f"         รอ {self.stabilize_time:.0f} วินาทีก่อนเริ่มหยด (Waiting before first dose)...")
        if not self._wait_with_cancel(self.stabilize_time):
            print("\n[CANCELLED by BTN3] หยุดการไทเทรชัน")
            self._is_running = False
            if self.led:
                self.led.off()
            return {'cancelled': True, 'total_cycles': 0, 'total_volume': 0}

        previous_derivative = 0.0
        alert_played = False  # Flag: เตือนใกล้จุดสมมูลแล้วหรือยัง (near-EP alert played?)

        # ใช้ self.total_steps ที่คำนวณไว้แล้ว (Use pre-calculated self.total_steps)
        # FIX Bug 2: ใช้ step count แทน volume เพื่อหลีกเลี่ยงปัญหา floating-point
        # Use step count instead of volume to avoid floating-point precision issues
        print(f"\n[Titration] จำนวน step ทั้งหมด: {self.total_steps} (Total steps)")

        try:
            # ลูปการไทเทรชันหลัก (Main titration loop)
            # FIX Bug 2: ใช้ cycle_count < self.total_steps แทน current_volume < max_volume
            # Use cycle_count < self.total_steps instead of current_volume < max_volume
            while not self._should_stop and self.cycle_count < self.total_steps:
                self.cycle_count += 1

                # เติมสารละลาย (Dispense titrant)
                self._dispense_titrant(self.dose_volume)

                # รอให้คงที่ พร้อม BTN3 ยกเลิก (Wait for stabilization with BTN3 cancel)
                if not self._wait_with_cancel(self.stabilize_time):
                    print("\n[CANCELLED by BTN3] หยุดการไทเทรชัน")
                    break

                # อ่านค่าเซ็นเซอร์ (Read sensors)
                ph_value, temp_value = self._read_sensors()

                # คำนวณเวลาที่ผ่านไป (Calculate elapsed time)
                elapsed_time = time.ticks_diff(time.ticks_ms(), self.start_time) / 1000.0

                # บันทึกข้อมูล (Log data)
                self._log_data_point(self.cycle_count, elapsed_time,
                                    self.current_volume, ph_value, temp_value)

                # คำนวณ derivative (Calculate derivative)
                derivative = self.calculate_derivative(len(self.data_points) - 1)

                # อัปเดตจอแสดงผล (Update display)
                self._update_display(self.cycle_count, self.current_volume,
                                    ph_value, temp_value, derivative)

                # แสดงข้อมูลใน console (Print to console)
                print(f"Cycle {self.cycle_count:3d}: V={self.current_volume:6.2f}mL, "
                      f"pH={ph_value:5.2f}, dpH/dV={derivative:+7.3f}")

                # =============================================================
                # เตือนใกล้จุดสมมูล (Near-equivalence point alert)
                # สำหรับ HCl 0.1M 5mL + NaOH 0.1M: จุดสมมูลที่ ~5.0 mL
                # เตือนที่ 4.80 mL (ค่าเริ่มต้น) เพื่อให้นิสิตเตรียมสังเกต
                # FIX Issue #22: ใช้ self.alert_volume แทน hardcoded ALERT_VOLUME_ML
                # =============================================================
                # FIX: ใช้ step count แทน volume เพื่อหลีกเลี่ยงปัญหา floating-point
                # Use step count instead of volume to avoid floating-point issues
                # เช่น alert_step = 4.80 / 0.2 = 24 (example)
                alert_step = int(self.alert_volume / self.dose_volume)
                if not alert_played and self.cycle_count >= alert_step:
                    alert_played = True
                    print("\n" + "!" * 50)
                    print(f"⚠️  ใกล้จุดสมมูล! (Approaching Equivalence Point!)")
                    print(f"    ปริมาตร: {self.current_volume:.2f} mL")
                    print("!" * 50 + "\n")

                    # ส่งเสียงเตือน 3 ครั้ง (Beep 3 times)
                    if self.buzzer:
                        try:
                            for _ in range(3):
                                self.buzzer.play_tone(2000, 200)  # เสียงสูง 2000 Hz
                                time.sleep(0.1)
                        except Exception:
                            pass

                    # อัปเดตจอแสดงผลพร้อมข้อความเตือน (Update display with alert)
                    if self.display:
                        try:
                            # ใช้ self.total_steps แทนการคำนวณซ้ำ (Use self.total_steps instead of recalculating)
                            if hasattr(self.display, 'show_titration_status'):
                                self.display.show_titration_status(
                                    step=self.cycle_count,
                                    total_steps=self.total_steps,
                                    volume=self.current_volume,
                                    max_volume=self.max_volume,
                                    ph=ph_value,
                                    temperature=temp_value,
                                    status_text="!! NEAR EQUIV POINT !!"
                                )
                        except Exception:
                            pass

                # หมายเหตุ: ไม่หยุดไทเทรชันอัตโนมัติเมื่อพบจุดสมมูล
                # Note: Do NOT stop titration automatically when equivalence point detected
                # เหตุผล: ต้องการข้อมูลครบ 50 จุดสำหรับวิเคราะห์ด้วย EquivPoint tool
                # Reason: Need all 50 data points for analysis with EquivPoint tool
                # จุดสมมูลจะถูกหาในตอนท้ายโดย detect_equivalence_point()
                # Equivalence point will be found at the end by detect_equivalence_point()

                previous_derivative = derivative

                # เรียก callback ถ้ามี (Call callback if provided)
                if callback:
                    if not callback(self.cycle_count, self.current_volume,
                                   ph_value, temp_value, derivative):
                        print("หยุดโดย callback (Stopped by callback)")
                        break

        except Exception as e:
            print(f"ข้อผิดพลาดระหว่างไทเทรชัน (Error during titration): {e}")

        finally:
            self._is_running = False

            # ปิด LED (Turn off LED)
            if self.led:
                self.led.off()

        # วิเคราะห์หาจุดสมมูล (Analyze for equivalence point)
        self.detect_equivalence_point()

        # ส่งเสียงเตือนเสร็จสิ้น (Beep to indicate completion)
        if self.buzzer:
            try:
                self.buzzer.play_tone(1000, 500)
                time.sleep(0.2)
                self.buzzer.play_tone(1500, 500)
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
        print("การไทเทรชันเสร็จสิ้น (Titration Complete)")
        print("=" * 50)
        print(f"จำนวนรอบทั้งหมด (Total cycles): {results['total_cycles']}")
        print(f"ปริมาตรรวม (Total volume): {results['total_volume']:.3f} mL")
        print(f"เวลารวม (Total time): {results['total_time']:.1f} s")
        if results['equivalence_point']:
            print(f"จุดสมมูล (Equivalence point): V={results['equivalence_point'][0]:.3f} mL, "
                  f"pH={results['equivalence_point'][1]:.3f}")
        print("=" * 50)

        # แสดงหน้าจอเสร็จสิ้น (Show completion screen)
        gc.collect()
        if self.display:
            try:
                eq_vol = results['equivalence_point'][0] if results['equivalence_point'] else None
                eq_ph = results['equivalence_point'][1] if results['equivalence_point'] else None

                if hasattr(self.display, 'show_titration_complete'):
                    self.display.show_titration_complete(
                        total_vol=results['total_volume'],
                        eq_vol=eq_vol,
                        eq_ph=eq_ph,
                        filename=results['filename']
                    )
                else:
                    if results['equivalence_point']:
                        self.display.show_success(f"EP: {eq_vol:.2f}mL")
                    else:
                        self.display.show_success("Complete!")
            except Exception as e:
                print(f"Display error: {e}")

        # รอกดปุ่ม 1 เพื่อกลับเมนู (Wait for BTN1 to return to menu)
        if self.buttons:
            print("กดปุ่ม 1 เพื่อกลับเมนู (Press BTN1 to return to menu)")
            while True:
                if self.buttons.is_pressed(1):
                    time.sleep(0.2)  # Debounce
                    break
                if self.buttons.is_pressed(3):
                    time.sleep(0.2)
                    break
                time.sleep(0.05)
        else:
            # ถ้าไม่มีปุ่ม รอ 5 วินาที (If no buttons, wait 5 seconds)
            time.sleep(5)

        return results

    def get_titration_curve(self):
        """
        ดึงข้อมูลกราฟการไทเทรชัน
        Get titration curve data

        Returns:
            tuple: (volumes, phs) รายการปริมาตรและค่า pH
        """
        volumes = [p['volume'] for p in self.data_points]
        phs = [p['ph'] for p in self.data_points]
        return (volumes, phs)

    def get_derivative_curve(self):
        """
        ดึงข้อมูลกราฟ derivative
        Get derivative curve data

        Returns:
            tuple: (volumes, derivatives) รายการปริมาตรและค่า dpH/dV
        """
        volumes = []
        derivatives = []

        for i in range(1, len(self.data_points)):
            volumes.append(self.data_points[i]['volume'])
            derivatives.append(self.calculate_derivative(i))

        return (volumes, derivatives)


# ==============================================================================
# ตัวอย่างการใช้งาน (Usage Example)
# ==============================================================================
if __name__ == '__main__':
    print("=" * 50)
    print("ทดสอบ TitrationController (Testing TitrationController)")
    print("=" * 50)
    print("\nโมดูลนี้ต้องการ hardware จริงในการทำงาน")
    print("This module requires actual hardware to run")
    print("\nหมายเหตุ: ไฟล์ CSV บันทึกใน ESP32 flash storage")
    print("Note: CSV files saved to ESP32 flash storage")
    print("ดาวน์โหลดผ่าน Thonny IDE (Download via Thonny IDE)")
    print("\nตัวอย่างการใช้งาน (Usage example):")
    print("""
    from hardware.pump import Pump
    from hardware.ph_sensor import PHSensor
    from hardware.temp_sensor import TemperatureSensor
    from core.titration import TitrationController

    # สร้าง hardware objects (Create hardware objects)
    pump = Pump()
    pump.init()

    ph_sensor = PHSensor()
    ph_sensor.init()

    temp_sensor = TemperatureSensor()
    temp_sensor.init()

    # สร้าง TitrationController (Create TitrationController)
    # หมายเหตุ: ไม่ต้องใช้ SD Card - ข้อมูลบันทึกใน ESP32 flash
    # Note: No SD Card needed - data saved to ESP32 flash
    titration = TitrationController(
        pump=pump,
        ph_sensor=ph_sensor,
        temp_sensor=temp_sensor
    )

    # ตั้งค่าพารามิเตอร์ (Configure parameters)
    # ใช้ปริมาตรคงที่ 0.2 mL ทุกครั้ง (Fixed 0.2 mL dose per step)
    # ปริมาตรสูงสุด = 2 เท่าปริมาตรตัวอย่าง (Max = 2x sample volume)
    titration.configure(
        dose_volume=0.2,       # 0.2 mL ต่อครั้ง (fixed dose volume)
        stabilize_time=10.0,   # รอ 10 วินาที (wait 10 seconds for stable pH)
        sample_volume=5.0      # ตัวอย่าง 5 mL → ไทเทรตสูงสุด 10 mL
                               # sample 5 mL → max titration 10 mL (2x)
    )

    # เริ่มการไทเทรชัน (Start titration)
    results = titration.run_titration(auto_detect=True)

    # บันทึกผลลัพธ์ (Save results)
    # ไฟล์จะบันทึกใน ESP32 flash เช่น titration_data_R1.csv
    # File saved to ESP32 flash e.g. titration_data_R1.csv
    titration.save_results()

    # แสดงจุดสมมูล (Show equivalence point)
    if results['equivalence_point']:
        vol, ph = results['equivalence_point']
        print(f"จุดสมมูล: {vol:.3f} mL, pH {ph:.3f}")

    # ดาวน์โหลดไฟล์ CSV ผ่าน Thonny IDE:
    # Download CSV file via Thonny IDE:
    # 1. เชื่อมต่อ ESP32 กับ Thonny (Connect ESP32 to Thonny)
    # 2. คลิกขวาที่ไฟล์ titration_data_R1.csv
    # 3. เลือก "Download to..." เพื่อบันทึกลงคอมพิวเตอร์
    # 4. วิเคราะห์ด้วย EquivPoint tool
    """)
