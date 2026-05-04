# ==============================================================================
# exercise_02_property_starter.py - แบบฝึกหัด: @property
# (Exercise: @property - Starter Code)
# ==============================================================================
# เวลาโดยประมาณ: 15 นาที (Estimated time: 15 minutes)
#
# นิสิตจะได้ฝึกสร้าง @property พร้อม validation
# Students will practice creating @property with validation
#
# โจทย์: สร้างคลาส CalibrationData พร้อม @property
#
# ==============================================================================


class CalibrationData:
    """
    คลาสเก็บข้อมูล Calibration สำหรับ pH Sensor

    TODO: นิสิตต้องเติมโค้ดให้สมบูรณ์

    Context ทางเคมี:
    - slope และ intercept มาจากการ calibrate pH sensor
    - สมการ: pH = slope * voltage(V) + intercept
    - slope ทฤษฎีที่ 25C ≈ -16.9 pH/V (= 1000/(-59.16 mV/pH จาก Nernst))
    - ค่าจริงจาก calibration อาจต่างจากค่าทฤษฎี
    - R-squared บอกความแม่นยำของ calibration (ค่ายิ่งใกล้ 1 ยิ่งดี)

    สิ่งที่ต้องทำ:
    1. เพิ่ม @property สำหรับ slope พร้อม validation
    2. เพิ่ม @property สำหรับ intercept พร้อม validation
    3. เพิ่ม @property สำหรับ equation (computed, read-only)
    4. เพิ่ม @property สำหรับ is_valid (read-only)
    """

    def __init__(self, slope=-5.79, intercept=16.77):
        """
        สร้าง CalibrationData

        Args:
            slope (float): ค่า slope ของสมการ calibration
            intercept (float): ค่า intercept ของสมการ calibration
        """
        # Private attributes
        self._slope = slope
        self._intercept = intercept
        self._r_squared = 0.0
        self._is_validated = False

        print(f"[CalibrationData] สร้างข้อมูล calibration")

    # =========================================================================
    # TODO: เพิ่ม @property สำหรับ slope
    # =========================================================================

    @property
    def slope(self):
        """
        ค่า slope ของสมการ calibration

        TODO: เติม return statement
        """
        # TODO: return ค่า _slope
        pass

    @slope.setter
    def slope(self, value):
        """
        กำหนดค่า slope พร้อม validation

        TODO: เติมโค้ด
        1. ตรวจสอบว่า value เป็นตัวเลข (int หรือ float)
           - ถ้าไม่ใช่ ให้ raise TypeError
        2. ถ้า value > 0 ให้แสดง warning
        3. กำหนดค่าให้ _slope
        4. set _is_validated = False (ต้อง validate ใหม่)

        Args:
            value: ค่า slope ใหม่

        Raises:
            TypeError: ถ้า value ไม่ใช่ตัวเลข
        """
        # TODO: ตรวจสอบประเภท
        # if not isinstance(value, (int, float)):
        #     raise TypeError("slope ต้องเป็นตัวเลข")
        pass

        # TODO: warning ถ้าค่าเป็นบวก
        # if value > 0:
        #     print("[CalibrationData] คำเตือน: slope ควรเป็นค่าลบ")
        pass

        # TODO: กำหนดค่า
        # self._slope = value
        # self._is_validated = False
        pass

    # =========================================================================
    # TODO: เพิ่ม @property สำหรับ intercept
    # =========================================================================

    @property
    def intercept(self):
        """
        ค่า intercept ของสมการ calibration

        TODO: เติม return statement
        """
        # TODO: return ค่า _intercept
        pass

    @intercept.setter
    def intercept(self, value):
        """
        กำหนดค่า intercept พร้อม validation

        TODO: เติมโค้ด
        1. ตรวจสอบว่า value เป็นตัวเลข
        2. กำหนดค่าให้ _intercept
        3. set _is_validated = False

        Args:
            value: ค่า intercept ใหม่

        Raises:
            TypeError: ถ้า value ไม่ใช่ตัวเลข
        """
        # TODO: ตรวจสอบประเภท
        pass

        # TODO: กำหนดค่า
        pass

    # =========================================================================
    # TODO: เพิ่ม @property สำหรับ equation (Computed property)
    # =========================================================================

    @property
    def equation(self):
        """
        สมการ calibration ในรูป string (Computed property)

        TODO: เติมโค้ด
        return string ในรูปแบบ "pH = -5.7900 * V + 16.7700"
        ใช้ f-string พร้อม :.4f สำหรับ format ตัวเลข

        Returns:
            str: สมการ calibration
        """
        # TODO: return สมการในรูป string
        # return f"pH = {self._slope:.4f} * V + {self._intercept:.4f}"
        pass

    # =========================================================================
    # TODO: เพิ่ม @property สำหรับ is_valid (Read-only)
    # =========================================================================

    @property
    def is_valid(self):
        """
        สถานะว่า calibration ผ่านการตรวจสอบหรือไม่

        TODO: return ค่า _is_validated

        Returns:
            bool: True ถ้าผ่านการตรวจสอบ
        """
        # TODO: return ค่า _is_validated
        pass

    @property
    def r_squared(self):
        """ค่า R-squared"""
        return self._r_squared

    # =========================================================================
    # Methods
    # =========================================================================

    def validate(self, r_squared):
        """
        ตรวจสอบความถูกต้องของ calibration

        Args:
            r_squared (float): ค่า R-squared จากการ calibrate

        Returns:
            bool: True ถ้า R-squared >= 0.99
        """
        self._r_squared = r_squared
        self._is_validated = r_squared >= 0.99
        return self._is_validated


# ==============================================================================
# ทดสอบโค้ด (ไม่ต้องแก้ไข)
# Test code (Do not modify)
# ==============================================================================

if __name__ == "__main__":
    print("=" * 50)
    print("ทดสอบ CalibrationData")
    print("Testing CalibrationData")
    print("=" * 50)

    try:
        # === Original test code ===
        # สร้าง object (Create object)
        cal = CalibrationData()

        # ทดสอบ getter (Test getter)
        print(f"\n--- Getter ---")
        print(f"slope: {cal.slope}")
        print(f"intercept: {cal.intercept}")
        print(f"equation: {cal.equation}")
        print(f"is_valid: {cal.is_valid}")

        # ทดสอบ setter (Test setter)
        print(f"\n--- Setter ---")
        cal.slope = -6.0
        print(f"slope หลังเปลี่ยน: {cal.slope}")

        cal.intercept = 17.0
        print(f"intercept หลังเปลี่ยน: {cal.intercept}")
        print(f"equation ใหม่: {cal.equation}")

        # ทดสอบ warning (slope เป็นบวก)
        print(f"\n--- ทดสอบ warning ---")
        cal.slope = 5.0  # ควรแสดง warning

        # ทดสอบ validation (Test validation)
        print(f"\n--- ทดสอบ validate ---")
        print(f"validate(0.98): {cal.validate(0.98)}")
        print(f"is_valid: {cal.is_valid}")

        print(f"validate(0.995): {cal.validate(0.995)}")
        print(f"is_valid: {cal.is_valid}")

        # ทดสอบ TypeError (Test TypeError)
        print(f"\n--- ทดสอบ TypeError ---")
        try:
            cal.slope = "hello"
        except TypeError as e:
            print(f"TypeError: {e}")
            print("(คาดไว้แล้ว)")

        print("\n" + "=" * 50)
        print("ทดสอบเสร็จสิ้น!")
        print("=" * 50)

    except NotImplementedError as e:
        print("\n" + "=" * 50)
        print("*** โค้ดยังไม่สมบูรณ์ (Code incomplete) ***")
        print(f"*** ข้อผิดพลาด: {e} ***")
        print("*** กรุณาเติมโค้ดในส่วน TODO ***")
        print("*** Please complete the TODO sections ***")
        print("=" * 50)
    except TypeError as e:
        print(f"\n*** TypeError: {e} ***")
        print("*** ตรวจสอบประเภทข้อมูลที่ส่งให้ฟังก์ชัน ***")
        print("*** Check the data types passed to functions ***")
    except Exception as e:
        print(f"\n*** ข้อผิดพลาดอื่น (Other error): {e} ***")
        print("*** ตรวจสอบโค้ดของคุณอีกครั้ง ***")
