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

    # CSV Header สำหรับบันทึกข้อมูล (CSV Header for data logging)
    # ชื่อคอลัมน์ตรงกับ EquivPoint analysis tool (Column names match EquivPoint)
    # "Volume (mL)" และ "pH Value" เป็นคอลัมน์หลักที่ EquivPoint ต้องการ
    CSV_HEADERS = ['Volume (mL)', 'pH Value', 'Cycle', 'Time(s)', 'Temperature(C)']

    def __init__(self, pump, ph_sensor, temp_sensor=None,
                 display=None, buzzer=None, led_indicator=None):
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

        # สถานะการทำงาน (Operation state)
        self._is_running = False
        self._should_stop = False
        self._current_filename = None

    def configure(self, dose_volume=None, stabilize_time=None, sample_volume=None):
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
        """
        if dose_volume is not None:
            self.dose_volume = dose_volume
        if stabilize_time is not None:
            self.stabilize_time = stabilize_time
        if sample_volume is not None:
            self.sample_volume = sample_volume
            # ปริมาตรสูงสุด = 2 เท่าของปริมาตรตัวอย่าง (Max = 2x sample volume)
            self.max_volume = 2 * self.sample_volume

        # คำนวณจำนวน step ทั้งหมด (Calculate total steps)
        total_steps = int(self.max_volume / self.dose_volume)

        print(f"ตั้งค่าการไทเทรชัน (Titration configured):")
        print(f"  - ปริมาตรตัวอย่าง (Sample volume): {self.sample_volume} mL")
        print(f"  - ปริมาตรสูงสุด (Max volume): {self.max_volume} mL (2x sample)")
        print(f"  - ปริมาตรต่อครั้ง (Dose): {self.dose_volume} mL")
        print(f"  - จำนวน step ทั้งหมด (Total steps): {total_steps}")
        print(f"  - เวลารอ (Stabilize): {self.stabilize_time} s")

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
        temp_value = 25.0  # ค่าเริ่มต้น (default)
        if self.temp_sensor:
            try:
                temp_value = self.temp_sensor.read_temperature()
            except Exception:
                temp_value = 25.0

        return (ph_value, temp_value)

    def _dispense_titrant(self, volume_ml):
        """
        เติมสารละลายไทแทรนต์
        Dispense titrant solution

        Args:
            volume_ml: ปริมาตรที่จะเติม (volume to dispense in mL)
        """
        if self.pump:
            # ใช้ run_for_volume ถ้ามี มิฉะนั้นใช้ pump_volume
            # Use run_for_volume if available, otherwise pump_volume
            if hasattr(self.pump, 'run_for_volume'):
                self.pump.run_for_volume(volume_ml)
            elif hasattr(self.pump, 'pump_volume'):
                self.pump.pump_volume(volume_ml)
            self.current_volume += volume_ml

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
                # ใช้เมธอด show_titration_status ถ้ามี
                # Use show_titration_status method if available
                if hasattr(self.display, 'show_titration_status'):
                    self.display.show_titration_status(cycle, volume, ph, temperature)
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
        if abs(delta_v) < 0.0001:
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

    @property
    def is_running(self):
        """
        ตรวจสอบสถานะการทำงาน
        Check running status
        """
        return self._is_running

    def run_titration(self, auto_detect=True, callback=None):
        """
        ดำเนินการไทเทรชันอัตโนมัติ
        Run automatic titration

        Args:
            auto_detect: หาจุดสมมูลอัตโนมัติและหยุด (auto detect and stop at equivalence point)
            callback: ฟังก์ชันเรียกกลับหลังแต่ละรอบ (callback function after each cycle)
                      callback(cycle, volume, ph, temperature, derivative) -> bool
                      Return False เพื่อหยุดการไทเทรชัน (Return False to stop)

        Returns:
            dict: ผลลัพธ์การไทเทรชัน (Titration results)
        """
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
            print(f"สร้างไฟล์: {self._current_filename} (File created: {self._current_filename})")
        except Exception as e:
            print(f"ไม่สามารถสร้างไฟล์ (Cannot create file): {e}")
            self._current_filename = None

        print("=" * 50)
        print("เริ่มการไทเทรชันอัตโนมัติ (Starting Automatic Titration)")
        print("=" * 50)
        print(f"ปริมาตรตัวอย่าง (Sample): {self.sample_volume} mL")
        print(f"ปริมาตรสูงสุด (Max): {self.max_volume} mL (2x sample)")
        print(f"ปริมาตรต่อครั้ง (Dose): {self.dose_volume} mL")
        print(f"จำนวน step (Total steps): {int(self.max_volume / self.dose_volume)}")
        print("-" * 50)

        # เปิด LED แสดงสถานะทำงาน (Turn on working status LED)
        if self.led:
            self.led.on()

        # อ่านค่าเริ่มต้นก่อนเติมสารละลาย (Read initial values)
        ph_value, temp_value = self._read_sensors()
        self._log_data_point(0, 0.0, 0.0, ph_value, temp_value)
        self._update_display(0, 0.0, ph_value, temp_value)

        previous_derivative = 0.0
        equivalence_detected = False

        try:
            # ลูปการไทเทรชันหลัก (Main titration loop)
            while not self._should_stop and self.current_volume < self.max_volume:
                self.cycle_count += 1

                # เติมสารละลาย (Dispense titrant)
                self._dispense_titrant(self.dose_volume)

                # รอให้คงที่ (Wait for stabilization)
                time.sleep(self.stabilize_time)

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

                # ตรวจจับจุดสมมูลอัตโนมัติ (Auto-detect equivalence point)
                if auto_detect and len(self.data_points) > 3:
                    # หาจุดที่ derivative เริ่มลดลงหลังจากสูงสุด
                    # Find where derivative starts decreasing after maximum
                    if abs(derivative) < abs(previous_derivative) * 0.5:
                        if abs(previous_derivative) > 0.5:  # threshold
                            print("\nตรวจพบจุดสมมูล! (Equivalence point detected!)")
                            equivalence_detected = True
                            # เติมอีกเล็กน้อยเพื่อยืนยัน (Add a bit more to confirm)
                            for _ in range(3):
                                self.cycle_count += 1
                                self._dispense_titrant(self.dose_volume)
                                time.sleep(self.stabilize_time)
                                ph_value, temp_value = self._read_sensors()
                                elapsed_time = time.ticks_diff(time.ticks_ms(), self.start_time) / 1000.0
                                self._log_data_point(self.cycle_count, elapsed_time,
                                                    self.current_volume, ph_value, temp_value)
                            break

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
