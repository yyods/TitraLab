# ==============================================================================
# ph_sensor.py - คลาสเซ็นเซอร์ pH สืบทอดจาก BaseSensor
# (pH Sensor Class - Inherits from BaseSensor)
# ==============================================================================
# โมดูลนี้สาธิตการ Inheritance โดย PHSensor สืบทอดจาก BaseSensor
# This module demonstrates Inheritance with PHSensor extending BaseSensor
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจการ inherit จาก parent class: class PHSensor(BaseSensor)
#   2. ใช้ super().__init__() เรียก constructor ของ parent
#   3. Override methods: read(), _init_hardware()
#   4. เพิ่ม methods เฉพาะ: read_ph(), read_voltage(), calibrate()
#   5. ใช้ @property สำหรับ encapsulation: slope, intercept
#
# หลักการทางเคมี (Chemistry Principles):
#   สมการ Nernst: E = E0 - (2.303RT/nF) * pH
#   ที่ 25 C: slope ทฤษฎี = -59.16 mV/pH
#
#   การแปลงค่า (Conversion):
#   pH = slope * voltage + intercept
#
# Hardware Configuration:
#   - GPIO 25: pH Sensor (ADC input)
#   - ADC 12-bit: 0-4095 (0-3.3V)
#
# ==============================================================================

from machine import Pin, ADC
from time import sleep_ms

# นำเข้า BaseSensor จากไฟล์ base_sensor.py
# Import BaseSensor from base_sensor.py
try:
    from base_sensor import BaseSensor
except ImportError:
    from lib.base_sensor import BaseSensor


# ==============================================================================
# ค่าคงที่สำหรับ pH Sensor (pH Sensor Constants)
# ==============================================================================
# GPIO และ ADC Configuration
PH_PIN = 25                    # GPIO25 สำหรับ pH sensor
ADC_MAX_VALUE = 4095           # 12-bit ADC maximum value
ADC_REFERENCE_MV = 3300        # แรงดันอ้างอิง 3.3V = 3300 mV

# ค่า Calibration เริ่มต้น (Default Calibration Values)
DEFAULT_SLOPE = -5.7901        # ค่า slope จาก calibration
DEFAULT_INTERCEPT = 16.769     # ค่า intercept จาก calibration

# ค่าทางเคมี (Chemistry Constants)
NERNST_SLOPE_25C = -59.16      # mV/pH ที่ 25 C (ค่าทฤษฎี)
PH_BUFFER_VALUES = [4.00, 7.00, 10.00]  # ค่า pH มาตรฐานสำหรับ calibration


class PHSensor(BaseSensor):
    """
    คลาสเซ็นเซอร์ pH สืบทอดจาก BaseSensor
    (pH Sensor class inheriting from BaseSensor)

    ===== การ Inherit (Inheritance) =====

    class PHSensor(BaseSensor):  <-- PHSensor สืบทอดจาก BaseSensor

    PHSensor ได้รับ:
    1. Attributes จาก BaseSensor: _name, _pin_number, _is_initialized, etc.
    2. Methods จาก BaseSensor: log(), read_averaged(), read_filtered(), etc.
    3. Properties จาก BaseSensor: name, pin_number, is_initialized, etc.

    PHSensor เพิ่มเติม:
    1. Attributes เฉพาะ: _slope, _intercept, _adc, _calibration_points
    2. Methods เฉพาะ: read_ph(), read_voltage(), read_voltage_mv(), calibrate()
    3. Properties เฉพาะ: slope, intercept

    PHSensor Override:
    1. read() - อ่านค่า pH แทนที่ BaseSensor.read()
    2. _init_hardware() - เริ่มต้น ADC

    ===== ตัวอย่างการใช้งาน (Usage Example) =====

        # สร้าง pH sensor
        ph_sensor = PHSensor()

        # เริ่มต้นฮาร์ดแวร์
        ph_sensor.init()

        # อ่านค่า pH
        ph_value = ph_sensor.read()
        print(f"pH: {ph_value:.2f}")

        # อ่านแรงดัน
        voltage = ph_sensor.read_voltage()
        print(f"Voltage: {voltage:.4f} V")

        # ใช้ methods ที่สืบทอดจาก BaseSensor
        avg_ph = ph_sensor.read_averaged(num_samples=5)
        filtered_ph = ph_sensor.read_filtered(num_samples=10)

    Attributes:
        _slope (float): ความชันของสมการ calibration (private)
        _intercept (float): จุดตัดแกน Y ของสมการ calibration (private)
        _adc (ADC): ADC object สำหรับอ่านค่า (private)
        _calibration_points (list): จุด calibration ที่บันทึกไว้ (private)
    """

    def __init__(self, pin=None, slope=None, intercept=None):
        """
        Constructor - สร้าง PHSensor object

        ===== หลักการ super().__init__() =====

        เมื่อ child class มี __init__ ของตัวเอง:
        1. ต้องเรียก super().__init__() ก่อนเสมอ
        2. super().__init__() เริ่มต้น attributes ของ parent class
        3. จากนั้นจึงเริ่มต้น attributes เฉพาะของ child class

        Args:
            pin (int): GPIO pin สำหรับ pH sensor (ค่าเริ่มต้น: GPIO25)
            slope (float): ค่า slope ของสมการ calibration
            intercept (float): ค่า intercept ของสมการ calibration
        """
        # กำหนดค่า pin (Set pin value)
        pin_number = pin if pin is not None else PH_PIN

        # ===== เรียก constructor ของ parent class =====
        # super() คืน reference ไปยัง parent class (BaseSensor)
        # __init__() เรียก constructor ของ parent
        # นี่คือขั้นตอนสำคัญในการ inherit
        super().__init__(name="pH Sensor", pin=pin_number)

        # ===== เริ่มต้น attributes เฉพาะของ PHSensor =====
        # Attributes เหล่านี้ไม่มีใน BaseSensor
        self._slope = slope if slope is not None else DEFAULT_SLOPE
        self._intercept = intercept if intercept is not None else DEFAULT_INTERCEPT
        self._adc = None  # จะสร้างใน _init_hardware()
        self._calibration_points = []

        # แสดงข้อมูล calibration เริ่มต้น
        self.log(f"สมการ: pH = {self._slope:.4f} * V + {self._intercept:.4f}")
        self.log(f"Equation: pH = {self._slope:.4f} * V + {self._intercept:.4f}")

    # =========================================================================
    # Properties - @property สำหรับ Encapsulation
    # =========================================================================

    @property
    def slope(self):
        """
        ค่า slope ของสมการ calibration (Calibration equation slope)

        ===== @property =====

        ทำให้เข้าถึง _slope ได้แบบ read:
            value = sensor.slope  # อ่านค่า

        Returns:
            float: ค่า slope
        """
        return self._slope

    @slope.setter
    def slope(self, value):
        """
        กำหนดค่า slope ใหม่ (Set new slope value)

        ===== @property.setter =====

        ทำให้กำหนดค่า _slope ได้:
            sensor.slope = -5.5  # กำหนดค่าใหม่

        สามารถเพิ่ม validation ได้:
        - ตรวจสอบว่าค่าอยู่ในช่วงที่ถูกต้อง
        - แสดง warning ถ้าค่าผิดปกติ

        Args:
            value (float): ค่า slope ใหม่
        """
        # Validation: slope ควรเป็นค่าลบ (pH สูง = voltage ต่ำ)
        if value > 0:
            self.log("คำเตือน: slope ควรเป็นค่าลบ (Warning: slope should be negative)")

        self._slope = value
        self.log(f"Slope ใหม่: {value:.4f} (New slope: {value:.4f})")

    @property
    def intercept(self):
        """
        ค่า intercept ของสมการ calibration (Calibration equation intercept)

        Returns:
            float: ค่า intercept
        """
        return self._intercept

    @intercept.setter
    def intercept(self, value):
        """
        กำหนดค่า intercept ใหม่ (Set new intercept value)

        Args:
            value (float): ค่า intercept ใหม่
        """
        self._intercept = value
        self.log(f"Intercept ใหม่: {value:.4f} (New intercept: {value:.4f})")

    @property
    def calibration_equation(self):
        """
        สมการ calibration ในรูป string (Calibration equation as string)

        Read-only property - ไม่มี setter

        Returns:
            str: สมการในรูปแบบ "pH = slope * V + intercept"
        """
        return f"pH = {self._slope:.4f} * V + {self._intercept:.4f}"

    # =========================================================================
    # Override Methods - Methods ที่ override จาก BaseSensor
    # =========================================================================

    def _init_hardware(self):
        """
        เริ่มต้น ADC สำหรับ pH sensor (Initialize ADC for pH sensor)

        ===== Method Overriding =====

        นี่คือการ override method จาก BaseSensor
        BaseSensor._init_hardware() raise NotImplementedError
        PHSensor._init_hardware() implement การเริ่มต้นจริง

        หมายเหตุ:
        - Method นี้ถูกเรียกโดย init() ใน BaseSensor
        - ไม่ควรเรียกโดยตรง (prefix _ แสดงว่าเป็น internal)
        """
        # ตรวจสอบ pin ก่อน (Validate pin first)
        self.validate_pin(self._pin_number)

        # สร้าง ADC object (Create ADC object)
        self._adc = ADC(Pin(self._pin_number))

        # ตั้งค่า attenuation สำหรับอ่าน 0-3.3V
        # ATTN_11DB: Full range 0-3.3V
        self._adc.atten(ADC.ATTN_11DB)

        self.log(f"ADC เริ่มต้นที่ GPIO{self._pin_number} (ADC initialized on GPIO{self._pin_number})")

    def read(self):
        """
        อ่านค่า pH (Read pH value)

        ===== Method Overriding =====

        Override BaseSensor.read() ที่ raise NotImplementedError
        PHSensor.read() คืนค่า pH จริง

        เนื่องจาก read() เป็น method หลักที่ BaseSensor กำหนด
        methods อื่นๆ เช่น read_averaged(), read_filtered()
        จะใช้ read() นี้โดยอัตโนมัติ

        Returns:
            float: ค่า pH (0.00 - 14.00)
        """
        if self._adc is None:
            self.log("ยังไม่ได้เริ่มต้น กรุณาเรียก init() ก่อน")
            self.log("Not initialized, please call init() first")
            return None

        # อ่านค่าแรงดัน (Read voltage)
        voltage = self.read_voltage()

        # คำนวณ pH จากสมการ calibration
        # pH = slope * voltage + intercept
        ph_value = self._slope * voltage + self._intercept

        # อัปเดต state (Update state)
        self._last_value = ph_value
        self._read_count += 1

        return ph_value

    # =========================================================================
    # PHSensor-specific Methods - Methods เฉพาะสำหรับ pH
    # =========================================================================

    def read_raw(self):
        """
        อ่านค่า ADC ดิบ (Read raw ADC value)

        ค่า ADC อยู่ในช่วง 0-4095 (12-bit)

        Returns:
            int: ค่า ADC ดิบ (0-4095)
        """
        if self._adc is None:
            return None
        return self._adc.read()

    def read_voltage_mv(self):
        """
        อ่านแรงดันเป็นมิลลิโวลต์ (Read voltage in millivolts)

        การคำนวณ (Calculation):
            voltage_mV = (ADC_value / 4095) * 3300

        Returns:
            float: แรงดันเป็น mV
        """
        raw = self.read_raw()
        if raw is None:
            return None

        voltage_mv = (raw / ADC_MAX_VALUE) * ADC_REFERENCE_MV
        return voltage_mv

    def read_voltage(self):
        """
        อ่านแรงดันเป็นโวลต์พร้อมการกรอง (Read voltage in volts with filtering)

        วิธีการกรอง (Filtering Method):
        1. อ่านค่า 10 ครั้ง
        2. เรียงลำดับจากน้อยไปมาก
        3. ตัดค่า 2 ค่าแรกและ 2 ค่าสุดท้าย (outliers)
        4. เฉลี่ยค่าตรงกลาง

        Returns:
            float: แรงดันเป็น V
        """
        if self._adc is None:
            return None

        # อ่านหลาย samples (Read multiple samples)
        samples = []
        for _ in range(10):
            samples.append(self._adc.read())
            sleep_ms(10)

        # เรียงลำดับ (Sort)
        samples.sort()

        # ตัดค่าสุดขีด 2 ค่าแรกและ 2 ค่าสุดท้าย (Trim extremes)
        trimmed = samples[2:8]

        # คำนวณค่าเฉลี่ย (Calculate average)
        avg_adc = sum(trimmed) / len(trimmed)

        # แปลงเป็นโวลต์ (Convert to volts)
        voltage = (avg_adc / ADC_MAX_VALUE) * (ADC_REFERENCE_MV / 1000)

        return voltage

    def read_ph(self):
        """
        อ่านค่า pH อย่างเดียว (Read pH value only)

        Alias สำหรับ read() เพื่อความชัดเจน

        Returns:
            float: ค่า pH
        """
        return self.read()

    def read_with_voltage(self):
        """
        อ่านทั้ง pH และ voltage (Read both pH and voltage)

        Returns:
            tuple: (voltage, ph_value)
        """
        voltage = self.read_voltage()
        if voltage is None:
            return None, None

        ph_value = self._slope * voltage + self._intercept
        self._last_value = ph_value
        self._read_count += 1

        return voltage, ph_value

    # =========================================================================
    # Calibration Methods
    # =========================================================================

    def set_calibration(self, slope, intercept):
        """
        กำหนดค่า calibration ใหม่ (Set new calibration values)

        Args:
            slope (float): ค่า slope ใหม่
            intercept (float): ค่า intercept ใหม่
        """
        self._slope = slope
        self._intercept = intercept
        self.log(f"สมการใหม่: pH = {slope:.4f} * V + {intercept:.4f}")
        self.log(f"New equation: pH = {slope:.4f} * V + {intercept:.4f}")

    def add_calibration_point(self, buffer_ph, voltage):
        """
        เพิ่มจุด calibration (Add calibration point)

        Args:
            buffer_ph (float): ค่า pH ของสารละลายบัฟเฟอร์
            voltage (float): แรงดันที่วัดได้ (V)
        """
        self._calibration_points.append({
            'ph': buffer_ph,
            'voltage': voltage
        })
        self.log(f"เพิ่มจุด: pH {buffer_ph:.2f} = {voltage:.4f} V")
        self.log(f"Added point: pH {buffer_ph:.2f} = {voltage:.4f} V")

    def clear_calibration_points(self):
        """ล้างจุด calibration ทั้งหมด (Clear all calibration points)"""
        self._calibration_points = []
        self.log("ล้างจุด calibration แล้ว (Calibration points cleared)")

    def calculate_calibration(self):
        """
        คำนวณสมการ calibration จากจุดที่บันทึกไว้
        (Calculate calibration equation from recorded points)

        ต้องมีอย่างน้อย 2 จุด (At least 2 points required)

        Returns:
            tuple: (slope, intercept, r_squared) หรือ None ถ้าไม่พอ
        """
        points = self._calibration_points

        if len(points) < 2:
            self.log("ต้องมีอย่างน้อย 2 จุดสำหรับ calibration")
            self.log("At least 2 points required for calibration")
            return None

        # ดึงข้อมูล x (voltage) และ y (pH)
        x = [p['voltage'] for p in points]
        y = [p['ph'] for p in points]

        n = len(points)

        # คำนวณ Linear Regression
        # slope = (n*sum(xy) - sum(x)*sum(y)) / (n*sum(x^2) - (sum(x))^2)
        # intercept = (sum(y) - slope*sum(x)) / n

        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(xi ** 2 for xi in x)

        denominator = n * sum_x2 - sum_x ** 2
        if denominator == 0:
            self.log("ไม่สามารถคำนวณได้ (Cannot calculate)")
            return None

        slope = (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n

        # คำนวณ R-squared
        y_mean = sum_y / n
        ss_tot = sum((yi - y_mean) ** 2 for yi in y)
        ss_res = sum((y[i] - (slope * x[i] + intercept)) ** 2 for i in range(n))

        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        # อัปเดตค่า calibration
        self._slope = slope
        self._intercept = intercept

        self.log(f"Calibration: slope={slope:.4f}, intercept={intercept:.4f}, R2={r_squared:.4f}")

        return slope, intercept, r_squared

    def get_calibration_points(self):
        """
        รับจุด calibration ทั้งหมด (Get all calibration points)

        Returns:
            list: รายการจุด calibration
        """
        return self._calibration_points.copy()

    @staticmethod
    def get_buffer_values():
        """
        รับค่า pH บัฟเฟอร์มาตรฐาน (Get standard buffer pH values)

        Static method - เรียกได้โดยไม่ต้องสร้าง instance:
            values = PHSensor.get_buffer_values()

        Returns:
            list: [4.00, 7.00, 10.00]
        """
        return PH_BUFFER_VALUES.copy()

    @staticmethod
    def calculate_nernst_slope(temperature_c=25.0):
        """
        คำนวณ slope ทฤษฎีตาม Nernst ที่อุณหภูมิที่กำหนด
        (Calculate theoretical Nernst slope at given temperature)

        สมการ Nernst:
            E = E0 - (2.303 * R * T) / (n * F) * pH

        Slope = -(2.303 * R * T) / (n * F) * 1000 (mV/pH)

        Args:
            temperature_c (float): อุณหภูมิเซลเซียส

        Returns:
            float: Theoretical slope in mV/pH
        """
        R = 8.314       # Gas constant (J/(mol*K))
        F = 96485       # Faraday constant (C/mol)
        n = 1           # Number of electrons for H+
        T = temperature_c + 273.15  # Convert to Kelvin

        slope = -(2.303 * R * T) / (n * F) * 1000
        return slope

    # =========================================================================
    # Magic Methods
    # =========================================================================

    def __repr__(self):
        """
        แสดงข้อมูล object สำหรับ debugging

        Override __repr__ จาก BaseSensor เพื่อเพิ่มข้อมูล calibration
        """
        return (f"PHSensor(pin={self._pin_number}, "
                f"slope={self._slope:.4f}, "
                f"intercept={self._intercept:.4f}, "
                f"initialized={self._is_initialized})")


# ==============================================================================
# ตัวอย่างการใช้งาน (Usage Example)
# ==============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("PHSensor - เซ็นเซอร์ pH สืบทอดจาก BaseSensor")
    print("(PHSensor - pH Sensor inheriting from BaseSensor)")
    print("=" * 60)

    # สร้าง pH sensor
    ph_sensor = PHSensor()
    print(f"\nrepr: {repr(ph_sensor)}")
    print(f"str: {str(ph_sensor)}")

    # แสดง properties
    print(f"\n--- Properties ---")
    print(f"name: {ph_sensor.name}")
    print(f"pin_number: {ph_sensor.pin_number}")
    print(f"slope: {ph_sensor.slope}")
    print(f"intercept: {ph_sensor.intercept}")
    print(f"calibration_equation: {ph_sensor.calibration_equation}")

    # ทดสอบ setter
    print(f"\n--- ทดสอบ setter ---")
    ph_sensor.slope = -6.0
    print(f"slope หลังเปลี่ยน: {ph_sensor.slope}")

    # Static methods
    print(f"\n--- Static Methods ---")
    print(f"Buffer values: {PHSensor.get_buffer_values()}")
    print(f"Nernst slope at 25C: {PHSensor.calculate_nernst_slope(25):.2f} mV/pH")
    print(f"Nernst slope at 30C: {PHSensor.calculate_nernst_slope(30):.2f} mV/pH")

    # เริ่มต้นและอ่านค่า
    print(f"\n--- เริ่มต้นฮาร์ดแวร์ ---")
    if ph_sensor.init():
        try:
            print(f"\n--- ทดสอบอ่านค่า ---")
            for i in range(3):
                voltage, ph = ph_sensor.read_with_voltage()
                raw = ph_sensor.read_raw()
                print(f"ครั้งที่ {i+1}: Raw={raw}, V={voltage:.4f}V, pH={ph:.2f}")
                sleep_ms(1000)

            # ใช้ methods ที่สืบทอดจาก BaseSensor
            print(f"\n--- Methods จาก BaseSensor ---")
            avg_ph = ph_sensor.read_averaged(num_samples=5)
            print(f"ค่าเฉลี่ย (5 samples): {avg_ph:.2f}")

            filtered_ph = ph_sensor.read_filtered(num_samples=10)
            print(f"ค่ากรอง (10 samples): {filtered_ph:.2f}")

            print(f"\nจำนวนครั้งที่อ่าน: {ph_sensor.read_count}")
            print(f"ค่าล่าสุด: {ph_sensor.last_value:.2f}")

        except KeyboardInterrupt:
            print("\nหยุดโดยผู้ใช้ (Stopped by user)")
    else:
        print("ไม่สามารถเริ่มต้นได้ (Initialization failed)")

    print("\n" + "=" * 60)
    print("เสร็จสิ้น (Done)")
    print("=" * 60)
