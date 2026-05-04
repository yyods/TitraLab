# ==============================================================================
# exercise_02_property_solution.py - เฉลย: @property
# (Exercise: @property - Solution)
# ==============================================================================
# เวลาโดยประมาณ: 15 นาที (Estimated time: 15 minutes)
#
# เฉลยแบบฝึกหัดการสร้าง @property พร้อม validation
#
# ==============================================================================


class CalibrationData:
    """
    คลาสเก็บข้อมูล Calibration สำหรับ pH Sensor

    เฉลย: คลาสที่สมบูรณ์พร้อมคำอธิบาย
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
    # เฉลย: @property สำหรับ slope
    # =========================================================================

    @property
    def slope(self):
        """
        ค่า slope ของสมการ calibration

        เฉลย: return ค่า _slope
        """
        return self._slope

    @slope.setter
    def slope(self, value):
        """
        กำหนดค่า slope พร้อม validation

        เฉลย:
        1. ตรวจสอบว่า value เป็นตัวเลข
        2. ถ้า value > 0 แสดง warning
        3. กำหนดค่าให้ _slope
        4. set _is_validated = False

        Args:
            value: ค่า slope ใหม่

        Raises:
            TypeError: ถ้า value ไม่ใช่ตัวเลข
        """
        # เฉลย: ตรวจสอบประเภท
        if not isinstance(value, (int, float)):
            raise TypeError("slope ต้องเป็นตัวเลข (slope must be a number)")

        # เฉลย: warning ถ้าค่าเป็นบวก
        if value > 0:
            print("[CalibrationData] คำเตือน: slope ควรเป็นค่าลบตามสมการ Nernst")

        # เฉลย: กำหนดค่า
        self._slope = value
        self._is_validated = False  # ต้อง validate ใหม่

        print(f"[CalibrationData] slope ใหม่: {value:.4f}")

    # =========================================================================
    # เฉลย: @property สำหรับ intercept
    # =========================================================================

    @property
    def intercept(self):
        """
        ค่า intercept ของสมการ calibration

        เฉลย: return ค่า _intercept
        """
        return self._intercept

    @intercept.setter
    def intercept(self, value):
        """
        กำหนดค่า intercept พร้อม validation

        เฉลย:
        1. ตรวจสอบว่า value เป็นตัวเลข
        2. กำหนดค่าให้ _intercept
        3. set _is_validated = False

        Args:
            value: ค่า intercept ใหม่

        Raises:
            TypeError: ถ้า value ไม่ใช่ตัวเลข
        """
        # เฉลย: ตรวจสอบประเภท
        if not isinstance(value, (int, float)):
            raise TypeError("intercept ต้องเป็นตัวเลข (intercept must be a number)")

        # เฉลย: กำหนดค่า
        self._intercept = value
        self._is_validated = False

        print(f"[CalibrationData] intercept ใหม่: {value:.4f}")

    # =========================================================================
    # เฉลย: @property สำหรับ equation (Computed property)
    # =========================================================================

    @property
    def equation(self):
        """
        สมการ calibration ในรูป string (Computed property)

        เฉลย:
        ใช้ f-string พร้อม :.4f สำหรับ format ตัวเลข
        คืนค่าสมการในรูปแบบที่อ่านได้

        Returns:
            str: สมการ calibration
        """
        return f"pH = {self._slope:.4f} * V + {self._intercept:.4f}"

    # =========================================================================
    # เฉลย: @property สำหรับ is_valid (Read-only)
    # =========================================================================

    @property
    def is_valid(self):
        """
        สถานะว่า calibration ผ่านการตรวจสอบหรือไม่

        เฉลย: return ค่า _is_validated
        นี่คือ read-only property เพราะไม่มี setter

        Returns:
            bool: True ถ้าผ่านการตรวจสอบ
        """
        return self._is_validated

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

        if self._is_validated:
            print(f"[CalibrationData] Calibration ผ่าน! R2 = {r_squared:.4f}")
        else:
            print(f"[CalibrationData] Calibration ไม่ผ่าน R2 = {r_squared:.4f} (ต้องการ >= 0.99)")

        return self._is_validated


# ==============================================================================
# ทดสอบโค้ด
# Test code
# ==============================================================================

if __name__ == "__main__":
    print("=" * 50)
    print("ทดสอบ CalibrationData (เฉลย)")
    print("=" * 50)

    # สร้าง object
    cal = CalibrationData()

    # ทดสอบ getter
    print(f"\n--- Getter ---")
    print(f"slope: {cal.slope}")
    print(f"intercept: {cal.intercept}")
    print(f"equation: {cal.equation}")
    print(f"is_valid: {cal.is_valid}")

    # ทดสอบ setter
    print(f"\n--- Setter ---")
    cal.slope = -6.0
    print(f"slope หลังเปลี่ยน: {cal.slope}")

    cal.intercept = 17.0
    print(f"intercept หลังเปลี่ยน: {cal.intercept}")
    print(f"equation ใหม่: {cal.equation}")

    # ทดสอบ warning (slope เป็นบวก)
    print(f"\n--- ทดสอบ warning ---")
    cal.slope = 5.0  # ควรแสดง warning

    # ทดสอบ validation
    print(f"\n--- ทดสอบ validate ---")
    print(f"validate(0.98): {cal.validate(0.98)}")
    print(f"is_valid: {cal.is_valid}")

    print(f"validate(0.995): {cal.validate(0.995)}")
    print(f"is_valid: {cal.is_valid}")

    # ทดสอบ TypeError
    print(f"\n--- ทดสอบ TypeError ---")
    try:
        cal.slope = "hello"
    except TypeError as e:
        print(f"TypeError: {e}")
        print("(คาดไว้แล้ว)")

    print("\n" + "=" * 50)
    print("ทดสอบเสร็จสิ้น!")
    print("=" * 50)
