# ==============================================================================
# ph_sensor.py - คลาสเซ็นเซอร์ pH สำหรับ TitraLab
# (pH Sensor Class for TitraLab)
# ==============================================================================
# โมดูลนี้จัดการการอ่านค่า pH จาก ADC และการสอบเทียบ
# This module handles pH reading from ADC and calibration
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจหลักการทำงานของ pH electrode
#   2. เรียนรู้สมการ Nernst และความสัมพันธ์ mV-pH
#   3. ประยุกต์ใช้การสอบเทียบ 3 จุด (3-point calibration)
#
# หลักการทางเคมี (Chemistry Principles):
#   สมการ Nernst: E = E0 - (2.303 * R * T) / (n * F) * pH
#
#   ที่อุณหภูมิ 25 C (298.15 K):
#   - Theoretical slope = -59.16 mV/pH unit
#   - E0 = แรงดันที่ pH 7 (ขึ้นอยู่กับ electrode)
#
#   ในทางปฏิบัติ slope อาจแตกต่างเนื่องจาก:
#   - อายุการใช้งานของหัววัด (electrode aging)
#   - สภาพของ reference electrode
#   - อุณหภูมิ (temperature variations)
#
# ==============================================================================

from machine import Pin, ADC
from time import sleep_ms

# นำเข้าค่าคงที่จาก config (Import constants from config)
try:
    from config import (
        PH_PIN, ADC_MAX_VALUE, ADC_REFERENCE_MV, ADC_SAMPLES,
        PH_BUFFER_VALUES, DEFAULT_PH_SLOPE, DEFAULT_PH_INTERCEPT,
        NERNST_THEORETICAL_SLOPE,
        ADC_ROBUST_SAMPLES, ADC_SAMPLE_DELAY_MS, ADC_IQR_FACTOR
    )
except ImportError:
    # ค่าเริ่มต้นถ้าไม่พบ config (Default values if config not found)
    PH_PIN = 25
    ADC_MAX_VALUE = 4095
    ADC_REFERENCE_MV = 3300
    ADC_SAMPLES = 10
    PH_BUFFER_VALUES = [4.00, 7.00, 10.00]
    # สมการ: pH = slope_m * mV + intercept_b
    # Equation: pH = slope_m * mV + intercept_b
    DEFAULT_PH_SLOPE = -0.016911       # slope_m (pH/mV)
    DEFAULT_PH_INTERCEPT = 34.9800     # intercept_b (pH)
    NERNST_THEORETICAL_SLOPE = -59.16  # mV/pH ที่ 25 C (theoretical)
    # ค่าคงที่สำหรับ robust ADC filtering (Robust ADC filtering constants)
    ADC_ROBUST_SAMPLES = 25            # จำนวนตัวอย่าง (number of samples)
    ADC_SAMPLE_DELAY_MS = 20           # หน่วงเวลาระหว่างตัวอย่าง (delay between samples)
    ADC_IQR_FACTOR = 1.5               # ตัวคูณ IQR (Tukey factor)


class PHSensor:
    """
    คลาสเซ็นเซอร์ pH สำหรับการไทเทรต (pH Sensor class for titration)

    คุณสมบัติหลัก (Main Features):
        - อ่านค่าแรงดันจาก ADC พร้อมการกำจัด outlier แบบ robust
        - แปลงแรงดันเป็นค่า pH ตามสมการสอบเทียบ
        - รองรับการสอบเทียบ 3 จุด

    หลักการทำงาน (Working Principle):
        1. ADC อ่านแรงดันจาก pH electrode (0-3.3V = 0-3300 mV)
        2. แปลงค่า ADC เป็นมิลลิโวลต์ (mV)
        3. ใช้สมการเส้นตรง pH = slope_m * mV + intercept_b
           เพื่อแปลง mV เป็น pH

    การกรองสัญญาณแบบ Robust (Robust Signal Filtering):
        ใช้วิธี IQR (Interquartile Range) หรือ Tukey's Fences:
        1. เก็บตัวอย่าง 25 ค่า (25 samples, 20ms apart = ~500ms total)
        2. เรียงลำดับและคำนวณ Q1 (25th percentile), Q3 (75th percentile)
        3. คำนวณ IQR = Q3 - Q1
        4. กำหนดขอบเขต: lower = Q1 - 1.5*IQR, upper = Q3 + 1.5*IQR
        5. ตัดค่านอกขอบเขตออก (ค่า outlier)
        6. เฉลี่ยค่าที่เหลือ (ถ้าทุกค่าถูกตัด ใช้ median แทน)

        วิธีนี้สามารถกำจัด ADC glitches ที่รุนแรงได้ เช่น:
        - ค่าที่ให้ pH = 26.9 แทนที่จะเป็น ~11.7
        - ค่าที่ให้ pH = 0.8 แทนที่จะเป็น ~11.7

    ตัวอย่างการใช้งาน (Usage Example):
        >>> ph_sensor = PHSensor()
        >>> voltage_mv, ph = ph_sensor.read()
        >>> print(f"Voltage: {voltage_mv:.1f} mV, pH: {ph:.2f}")
    """

    def __init__(self, pin=None, slope=None, intercept=None):
        """
        สร้าง PHSensor object (Create PHSensor object)

        สมการ: pH = slope_m * mV + intercept_b
        Equation: pH = slope_m * mV + intercept_b

        Args:
            pin (int): หมายเลขขา GPIO (GPIO pin number)
                       ค่าเริ่มต้น: GPIO25
            slope (float): slope_m ของสมการสอบเทียบ หน่วย pH/mV
                           (Calibration slope in pH/mV units)
                           ค่าเริ่มต้น: -0.016911
            intercept (float): intercept_b ของสมการสอบเทียบ หน่วย pH
                               (Calibration intercept in pH units)
                               ค่าเริ่มต้น: 34.9800
        """
        # กำหนดค่า (Set values)
        self._pin_number = pin if pin is not None else PH_PIN
        self._slope = slope if slope is not None else DEFAULT_PH_SLOPE
        self._intercept = intercept if intercept is not None else DEFAULT_PH_INTERCEPT

        # สร้าง ADC object (Create ADC object)
        self._adc = ADC(Pin(self._pin_number))
        # ตั้งค่า attenuation สำหรับอ่านแรงดัน 0-3.3V
        # Set attenuation for 0-3.3V reading range
        self._adc.atten(ADC.ATTN_11DB)

        # จำนวนตัวอย่างสำหรับการเฉลี่ย (Samples for averaging)
        self._samples = ADC_SAMPLES

        # ค่าบัฟเฟอร์สำหรับการสอบเทียบ (Buffer values for calibration)
        self._buffer_ph_values = PH_BUFFER_VALUES.copy()

        # เก็บค่าสอบเทียบ (Store calibration values)
        self._calibration_points = []

        print(f"pH Sensor พร้อมใช้งานที่ GPIO{self._pin_number} "
              f"(pH Sensor ready on GPIO{self._pin_number})")
        print(f"สมการ: pH = {self._slope:.6f} * mV + {self._intercept:.4f} "
              f"(Equation: pH = {self._slope:.6f} * mV + {self._intercept:.4f})")

    def init(self):
        """
        เริ่มต้น pH Sensor (Initialize pH Sensor)

        เมธอดนี้ถูกเรียกโดย HardwareHub - ADC พร้อมใช้งานตั้งแต่สร้าง object
        This method is called by HardwareHub - ADC ready from object creation.
        """
        pass  # ADC พร้อมใช้งานตั้งแต่ __init__ (ADC ready from __init__)

    def deinit(self):
        """
        ปิด pH Sensor (Deinitialize pH Sensor)

        เมธอดนี้ถูกเรียกเมื่อปิดโปรแกรม
        This method is called on shutdown.
        """
        pass  # ADC ไม่ต้อง cleanup (ADC does not need cleanup)

    @property
    def slope(self):
        """ค่า slope ของสมการสอบเทียบ (Calibration equation slope)"""
        return self._slope

    @slope.setter
    def slope(self, value):
        """กำหนดค่า slope ใหม่ (Set new slope value)"""
        self._slope = value
        print(f"Slope ใหม่: {value:.4f} (New slope: {value:.4f})")

    @property
    def intercept(self):
        """ค่า intercept ของสมการสอบเทียบ (Calibration equation intercept)"""
        return self._intercept

    @intercept.setter
    def intercept(self, value):
        """กำหนดค่า intercept ใหม่ (Set new intercept value)"""
        self._intercept = value
        print(f"Intercept ใหม่: {value:.4f} (New intercept: {value:.4f})")

    def set_calibration(self, slope, intercept):
        """
        กำหนดค่าสอบเทียบใหม่ (Set new calibration values)

        สมการ: pH = slope_m * mV + intercept_b
        Equation: pH = slope_m * mV + intercept_b

        Args:
            slope (float): slope_m (pH/mV)
            intercept (float): intercept_b (pH)

        หมายเหตุ (Note):
            FIX Issue #21: slope ควรเป็นค่าลบ (pH ลดเมื่อ mV เพิ่ม)
            slope should be negative (pH decreases as mV increases)
        """
        # FIX Issue #21: ตรวจสอบและแก้ไข slope ที่เป็นบวก
        # Validate and auto-correct positive slope
        if slope > 0:
            print(f"คำเตือน: slope ควรเป็นค่าลบ! ({slope:.6f} -> {-abs(slope):.6f})")
            print(f"WARNING: Slope should be negative! Auto-correcting...")
            slope = -abs(slope)
        self._slope = slope
        self._intercept = intercept
        print(f"สมการใหม่: pH = {slope:.6f} * mV + {intercept:.4f} "
              f"(New equation: pH = {slope:.6f} * mV + {intercept:.4f})")

    def read_raw(self):
        """
        อ่านค่า ADC ดิบ (Read raw ADC value)

        Returns:
            int: ค่า ADC 0-4095
        """
        return self._adc.read()

    def read_voltage_mv(self):
        """
        อ่านแรงดันเป็นมิลลิโวลต์ (Read voltage in millivolts)

        การคำนวณ (Calculation):
            voltage_mV = (ADC_value / 4095) * 3300

        Returns:
            float: แรงดันเป็น mV
        """
        adc_value = self._adc.read()
        voltage_mv = (adc_value / ADC_MAX_VALUE) * ADC_REFERENCE_MV
        return voltage_mv

    def _calculate_percentile(self, sorted_data, percentile):
        """
        คำนวณ percentile จากข้อมูลที่เรียงลำดับแล้ว
        Calculate percentile from sorted data

        ใช้วิธี linear interpolation สำหรับค่าที่ไม่ตรงกับ index
        Uses linear interpolation for values between indices

        Args:
            sorted_data (list): ข้อมูลที่เรียงลำดับแล้ว (sorted data)
            percentile (float): เปอร์เซ็นไทล์ที่ต้องการ 0-100 (desired percentile)

        Returns:
            float: ค่า percentile ที่คำนวณได้
        """
        n = len(sorted_data)
        if n == 0:
            return 0

        # คำนวณตำแหน่ง index (Calculate index position)
        # ใช้วิธี linear interpolation
        k = (percentile / 100.0) * (n - 1)
        f = int(k)  # floor index
        c = f + 1   # ceiling index

        # ถ้า index เป็นจำนวนเต็มพอดี (If index is exact integer)
        if f == k or c >= n:
            return sorted_data[min(f, n - 1)]

        # Linear interpolation ระหว่างสองค่า
        # Linear interpolation between two values
        return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])

    def read_voltage_robust(self):
        """
        อ่านแรงดันด้วยวิธี IQR-based outlier rejection (Tukey's Fences)
        Read voltage using IQR-based outlier rejection (Tukey's Fences)

        วิธีการ (Algorithm):
            1. เก็บตัวอย่าง 25 ค่า ห่างกัน 20ms (~500ms รวม)
               Collect 25 samples, 20ms apart (~500ms total)

            2. เรียงลำดับและคำนวณ Q1, Q3
               Sort and calculate Q1 (25th percentile), Q3 (75th percentile)

            3. คำนวณ IQR = Q3 - Q1
               Calculate IQR = Q3 - Q1

            4. กำหนดขอบเขต Tukey's Fences:
               Define Tukey's Fences bounds:
               - lower_bound = Q1 - 1.5 * IQR
               - upper_bound = Q3 + 1.5 * IQR

            5. ตัดค่านอกขอบเขต (outliers) ออก
               Reject values outside bounds (outliers)

            6. เฉลี่ยค่าที่เหลือ
               Average the remaining "clean" values

            7. ถ้าทุกค่าถูกตัด (edge case) ใช้ median แทน
               If all values rejected (edge case), use median instead

        ข้อดี (Advantages):
            - กำจัด ADC glitches รุนแรงได้ (เช่น ค่าที่ให้ pH = 26.9)
            - ไม่ต้องรู้ค่าที่คาดหวังล่วงหน้า (adaptive threshold)
            - ใช้ได้กับทุกช่วง pH (works across all pH ranges)

        Returns:
            float: แรงดันเป็นมิลลิโวลต์ที่กำจัด outlier แล้ว
                   (voltage in mV with outliers rejected)
        """
        # ขั้นตอนที่ 1: เก็บตัวอย่าง ADC หลายค่า
        # Step 1: Collect multiple ADC samples
        samples = []
        for _ in range(ADC_ROBUST_SAMPLES):
            samples.append(self._adc.read())
            sleep_ms(ADC_SAMPLE_DELAY_MS)

        # ขั้นตอนที่ 2: เรียงลำดับตัวอย่าง
        # Step 2: Sort samples
        sorted_samples = sorted(samples)
        n = len(sorted_samples)

        # ขั้นตอนที่ 3: คำนวณ Q1 (25th percentile) และ Q3 (75th percentile)
        # Step 3: Calculate Q1 (25th percentile) and Q3 (75th percentile)
        q1 = self._calculate_percentile(sorted_samples, 25)
        q3 = self._calculate_percentile(sorted_samples, 75)

        # ขั้นตอนที่ 4: คำนวณ IQR และขอบเขต
        # Step 4: Calculate IQR and bounds
        iqr = q3 - q1

        # จัดการกรณี IQR = 0 (ทุกค่าเท่ากัน)
        # Handle case where IQR = 0 (all values identical)
        if iqr == 0:
            # ถ้าทุกค่าเท่ากัน ใช้ค่าเฉลี่ยปกติ
            # If all values equal, use simple average
            avg_adc = sum(sorted_samples) / n
            voltage_mv = (avg_adc / ADC_MAX_VALUE) * ADC_REFERENCE_MV
            return voltage_mv

        lower_bound = q1 - (ADC_IQR_FACTOR * iqr)
        upper_bound = q3 + (ADC_IQR_FACTOR * iqr)

        # ขั้นตอนที่ 5: กรองค่า outlier ออก
        # Step 5: Filter out outliers
        clean_samples = [s for s in sorted_samples
                         if lower_bound <= s <= upper_bound]

        # ขั้นตอนที่ 6: คำนวณค่าเฉลี่ยจากค่าที่สะอาด
        # Step 6: Calculate average from clean samples
        if len(clean_samples) > 0:
            # ใช้ค่าเฉลี่ยของ clean samples
            # Use average of clean samples
            avg_adc = sum(clean_samples) / len(clean_samples)
        else:
            # Edge case: ทุกค่าถูกตัดออก (ไม่ควรเกิดขึ้นในสถานการณ์ปกติ)
            # Edge case: All values rejected (should not happen normally)
            # Fallback to median
            median_index = n // 2
            if n % 2 == 0:
                avg_adc = (sorted_samples[median_index - 1] +
                           sorted_samples[median_index]) / 2
            else:
                avg_adc = sorted_samples[median_index]

        # แปลงเป็นมิลลิโวลต์ (Convert to millivolts)
        voltage_mv = (avg_adc / ADC_MAX_VALUE) * ADC_REFERENCE_MV
        return voltage_mv

    def read_voltage(self):
        """
        อ่านแรงดันเป็นมิลลิโวลต์พร้อมการกรองสัญญาณแบบ Robust
        Read voltage in millivolts with robust signal filtering

        ใช้วิธี IQR-based outlier rejection (Tukey's Fences) เพื่อกำจัด
        ค่าผิดปกติจาก ADC glitches ที่ทำให้ได้ค่า pH ผิดพลาดรุนแรง

        Uses IQR-based outlier rejection (Tukey's Fences) to eliminate
        abnormal values from ADC glitches that cause severe pH errors

        วิธีการกรอง Robust (Robust Filtering Method):
            1. เก็บตัวอย่าง 25 ค่า ห่างกัน 20ms (~500ms รวม)
            2. เรียงลำดับและคำนวณ Q1, Q3, IQR
            3. กำหนดขอบเขต: [Q1 - 1.5*IQR, Q3 + 1.5*IQR]
            4. ตัดค่านอกขอบเขตออก (outliers)
            5. เฉลี่ยค่าที่เหลือ

        หมายเหตุ (Notes):
            - เวลาอ่าน ~500ms (25 samples x 20ms)
            - สามารถกำจัด outlier รุนแรง เช่น pH=26.9 หรือ pH=0.8
            - ถ้าต้องการวิธีเดิม (trimmed mean) ใช้ read_voltage_simple()

        Returns:
            float: แรงดันเป็นมิลลิโวลต์ (voltage in mV)
        """
        # ใช้ robust IQR-based method
        # Use robust IQR-based method
        return self.read_voltage_robust()

    def read_voltage_simple(self):
        """
        อ่านแรงดันด้วยวิธี trimmed mean (วิธีเดิม)
        Read voltage using trimmed mean method (legacy method)

        วิธีนี้ใช้ในกรณีที่ต้องการอ่านเร็ว แต่ไม่ robust ต่อ outlier รุนแรง
        This method is for fast reading but not robust against severe outliers

        วิธีการกรอง (Filtering Method):
            1. อ่านค่า 10 ครั้ง
            2. เรียงลำดับจากน้อยไปมาก
            3. ตัดค่าสูงสุด-ต่ำสุดออก (index 0, 1, 8, 9)
            4. เฉลี่ยค่าตรงกลาง (index 2-7)

        Returns:
            float: แรงดันเป็นมิลลิโวลต์ (voltage in mV)
        """
        # เก็บค่าหลายตัวอย่าง (Collect multiple samples)
        samples = []
        for _ in range(self._samples):
            samples.append(self._adc.read())
            sleep_ms(10)  # หน่วงเวลาเล็กน้อยระหว่างการอ่าน

        # เรียงลำดับ (Sort samples)
        samples.sort()

        # เฉลี่ยค่าตรงกลาง ตัด 2 ค่าแรกและ 2 ค่าท้าย
        # Average middle values, trim 2 from each end
        trimmed_samples = samples[2:8]  # index 2 to 7
        avg_adc = sum(trimmed_samples) / len(trimmed_samples)

        # แปลงเป็นมิลลิโวลต์ (Convert to millivolts)
        voltage_mv = (avg_adc / ADC_MAX_VALUE) * ADC_REFERENCE_MV
        return voltage_mv

    def read(self):
        """
        อ่านค่า pH พร้อมแรงดัน (Read pH with voltage)

        การคำนวณ (Calculation):
            pH = slope_m * mV + intercept_b

        Returns:
            tuple: (voltage_mv, pH)
                - voltage_mv (float): แรงดันเป็นมิลลิโวลต์ (voltage in mV)
                - pH (float): ค่า pH ที่คำนวณได้

        หมายเหตุ (Note):
            FIX Issue #6: ตรวจสอบค่า pH อยู่ในช่วงที่เป็นไปได้
            Validates pH is within reasonable range (-2.0 to 16.0)
        """
        voltage_mv = self.read_voltage()
        ph_value = self._slope * voltage_mv + self._intercept

        # FIX Issue #6: ตรวจสอบค่า pH อยู่ในช่วงที่เป็นไปได้
        # Validate pH is within reasonable range
        # ค่า pH ที่เป็นไปได้: -2.0 ถึง 16.0 (รวม outlier เล็กน้อย)
        # Reasonable pH range: -2.0 to 16.0 (including slight outliers)
        # ตรวจสอบ NaN ด้วย ph_value != ph_value (NaN check)
        if ph_value < -2.0 or ph_value > 16.0 or ph_value != ph_value:
            print(f"คำเตือน: pH นอกช่วง ({ph_value:.2f}), ใช้ค่าเริ่มต้น 7.0")
            print(f"WARNING: pH out of bounds ({ph_value:.2f}), using default 7.0")
            ph_value = 7.0  # ค่าเริ่มต้นที่ปลอดภัย (Safe default)

        return voltage_mv, ph_value

    def read_ph(self):
        """
        อ่านเฉพาะค่า pH (Read pH value only)

        Returns:
            float: ค่า pH
        """
        _, ph = self.read()
        return ph

    def read_averaged(self, num_readings=5, delay_ms=100):
        """
        อ่านค่า pH เฉลี่ยจากหลายครั้ง (Read averaged pH from multiple readings)

        Args:
            num_readings (int): จำนวนครั้งที่อ่าน (number of readings)
            delay_ms (int): เวลาหน่วงระหว่างการอ่าน (delay between readings in ms)

        Returns:
            tuple: (avg_voltage_mv, avg_pH)
        """
        voltages = []
        phs = []

        for _ in range(num_readings):
            v, p = self.read()
            voltages.append(v)
            phs.append(p)
            sleep_ms(delay_ms)

        avg_voltage_mv = sum(voltages) / len(voltages)
        avg_ph = sum(phs) / len(phs)

        return avg_voltage_mv, avg_ph

    def read_voltage_averaged(self, num_samples=10):
        """
        อ่านแรงดันเฉลี่ยจากหลายตัวอย่าง (Read averaged voltage from multiple samples)

        Args:
            num_samples (int): จำนวนตัวอย่าง (Number of samples)

        Returns:
            float: แรงดันเฉลี่ยเป็น mV (Averaged voltage in mV)
        """
        readings = []
        for _ in range(num_samples):
            readings.append(self.read_voltage())
            sleep_ms(50)

        return sum(readings) / len(readings)

    def add_calibration_point(self, buffer_ph, voltage):
        """
        เพิ่มจุดสอบเทียบ (Add calibration point)

        Args:
            buffer_ph (float): ค่า pH ของสารละลายบัฟเฟอร์
            voltage (float): แรงดันที่อ่านได้ (V)
        """
        self._calibration_points.append({
            'ph': buffer_ph,
            'voltage': voltage
        })
        print(f"เพิ่มจุดสอบเทียบ: pH {buffer_ph:.2f} = {voltage:.4f} V "
              f"(Added calibration point: pH {buffer_ph:.2f} = {voltage:.4f} V)")

    def clear_calibration_points(self):
        """ล้างจุดสอบเทียบทั้งหมด (Clear all calibration points)"""
        self._calibration_points = []
        print("ล้างจุดสอบเทียบแล้ว (Calibration points cleared)")

    def get_calibration_points(self):
        """
        อ่านจุดสอบเทียบทั้งหมด (Get all calibration points)

        Returns:
            list: รายการจุดสอบเทียบ (list of calibration points)
        """
        return self._calibration_points.copy()

    def calculate_nernst_slope(self, temperature_c=25.0):
        """
        คำนวณ slope ทฤษฎีตามสมการ Nernst ที่อุณหภูมิที่กำหนด
        Calculate theoretical slope from Nernst equation at given temperature

        สมการ Nernst (Nernst Equation):
            E = E0 - (2.303 * R * T) / (n * F) * pH

            โดย:
            - R = 8.314 J/(mol*K) (Gas constant)
            - F = 96485 C/mol (Faraday constant)
            - n = 1 (Number of electrons for H+)
            - T = temperature in Kelvin

        Args:
            temperature_c (float): อุณหภูมิองศาเซลเซียส (temperature in Celsius)

        Returns:
            float: Theoretical slope in mV/pH
        """
        R = 8.314       # Gas constant (J/(mol*K))
        F = 96485       # Faraday constant (C/mol)
        n = 1           # Number of electrons
        T = temperature_c + 273.15  # Convert to Kelvin

        # Slope = -(2.303 * R * T) / (n * F) * 1000 (convert to mV)
        slope = -(2.303 * R * T) / (n * F) * 1000

        return slope

    def validate_calibration(self, r_squared):
        """
        ตรวจสอบความถูกต้องของการสอบเทียบ (Validate calibration)

        Args:
            r_squared (float): ค่า R-squared จากการคำนวณ

        Returns:
            tuple: (is_valid, message)
        """
        if r_squared >= 0.99:
            return True, "การสอบเทียบถูกต้อง (Calibration valid)"
        elif r_squared >= 0.95:
            return True, "การสอบเทียบยอมรับได้ (Calibration acceptable)"
        else:
            return False, "การสอบเทียบไม่ถูกต้อง กรุณาสอบเทียบใหม่ (Calibration invalid, please recalibrate)"

    def get_buffer_values(self):
        """
        อ่านค่าบัฟเฟอร์มาตรฐาน (Get standard buffer values)

        Returns:
            list: รายการค่า pH ของบัฟเฟอร์ [4.00, 7.00, 10.00]
        """
        return self._buffer_ph_values.copy()

    def estimate_probe_efficiency(self):
        """
        ประเมินประสิทธิภาพของหัววัด (Estimate probe efficiency)

        เปรียบเทียบ slope ที่สอบเทียบกับ slope ทฤษฎี
        Compare calibrated slope with theoretical slope

        slope ทฤษฎี (theoretical slope):
            Nernst: -59.16 mV/pH -> inverted: -0.016903 pH/mV (at 25 C)

        Returns:
            float: ประสิทธิภาพเป็นเปอร์เซ็นต์ (efficiency as percentage)
        """
        if self._slope == 0:
            return 0

        # Theoretical slope at 25 C:
        # Nernst = -59.16 mV/pH -> inverted = 1/(-59.16) = -0.016903 pH/mV
        theoretical_slope_ph_per_mv = 1.0 / NERNST_THEORETICAL_SLOPE

        # คำนวณประสิทธิภาพ (Calculate efficiency)
        efficiency = (self._slope / theoretical_slope_ph_per_mv) * 100

        return abs(efficiency)

    def __repr__(self):
        """แสดงข้อมูลเซ็นเซอร์ pH"""
        return (f"PHSensor(pin={self._pin_number}, "
                f"slope={self._slope:.4f}, intercept={self._intercept:.4f})")
