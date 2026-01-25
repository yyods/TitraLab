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
        NERNST_THEORETICAL_SLOPE
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


class PHSensor:
    """
    คลาสเซ็นเซอร์ pH สำหรับการไทเทรต (pH Sensor class for titration)

    คุณสมบัติหลัก (Main Features):
        - อ่านค่าแรงดันจาก ADC
        - แปลงแรงดันเป็นค่า pH ตามสมการสอบเทียบ
        - รองรับการสอบเทียบ 3 จุด

    หลักการทำงาน (Working Principle):
        1. ADC อ่านแรงดันจาก pH electrode (0-3.3V = 0-3300 mV)
        2. แปลงค่า ADC เป็นมิลลิโวลต์ (mV)
        3. ใช้สมการเส้นตรง pH = slope_m * mV + intercept_b
           เพื่อแปลง mV เป็น pH

    การกรองสัญญาณ (Signal Filtering):
        - อ่านค่า 10 ครั้งติดต่อกัน
        - เรียงลำดับและตัดค่าสูงสุด-ต่ำสุดออก
        - เฉลี่ยค่าที่เหลือเพื่อลด noise

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
        """
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

    def read_voltage(self):
        """
        อ่านแรงดันเป็นมิลลิโวลต์พร้อมการกรองสัญญาณ
        Read voltage in millivolts with signal filtering

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
        """
        voltage_mv = self.read_voltage()
        ph_value = self._slope * voltage_mv + self._intercept
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


# ==============================================================================
# ตัวอย่างการใช้งาน (Usage Example)
# ==============================================================================
if __name__ == "__main__":
    print("=" * 50)
    print("ทดสอบคลาส PHSensor (Testing PHSensor Class)")
    print("=" * 50)

    # สร้าง PHSensor object (Create PHSensor object)
    ph_sensor = PHSensor()
    print(ph_sensor)

    print("\n--- ข้อมูลทางเคมี (Chemistry Information) ---")
    print(f"Theoretical slope at 25C: {NERNST_THEORETICAL_SLOPE:.2f} mV/pH")
    print(f"Buffer values: {ph_sensor.get_buffer_values()}")

    try:
        print("\n--- ทดสอบการอ่านค่า (Reading Test) ---")
        for i in range(5):
            voltage_mv, ph = ph_sensor.read()
            raw = ph_sensor.read_raw()
            print(f"อ่านครั้งที่ {i+1}: Raw ADC={raw}, mV={voltage_mv:.1f}, pH={ph:.2f}")
            sleep_ms(1000)

        print("\n--- ทดสอบการอ่านเฉลี่ย (Averaged Reading Test) ---")
        avg_mv, avg_ph = ph_sensor.read_averaged(num_readings=3, delay_ms=500)
        print(f"ค่าเฉลี่ย: mV={avg_mv:.1f}, pH={avg_ph:.2f}")

        print("\n--- ทดสอบ Nernst slope (Nernst Slope Test) ---")
        for temp in [20, 25, 30]:
            slope = ph_sensor.calculate_nernst_slope(temp)
            print(f"Theoretical slope at {temp}C: {slope:.2f} mV/pH")

    except KeyboardInterrupt:
        print("\nหยุดโดยผู้ใช้ (Stopped by user)")

    print("เสร็จสิ้น (Done)")
