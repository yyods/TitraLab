# ==============================================================================
# 01_inheritance_sensors.py - พื้นฐาน Inheritance (Inheritance Basics)
# ==============================================================================
# เวลาในการสอน: ~45 นาที (Teaching time: ~45 minutes)
#
# โปรแกรมนี้สอนพื้นฐาน Inheritance สำหรับนิสิตเคมี
# This program teaches Inheritance basics for chemistry students
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจ Inheritance: class Child(Parent)
#   2. เรียนรู้ super().__init__() สำหรับเรียก parent constructor
#   3. เข้าใจ Method Overriding
#   4. เห็นประโยชน์ของ code reuse
#
# การเชื่อมโยงกับเคมี (Chemistry Connection):
#   - BaseSensor เหมือน "เซ็นเซอร์ทั่วไป"
#   - PHSensor คือ "หัววัด pH" ที่เป็นเซ็นเซอร์ชนิดหนึ่ง
#   - TempSensor คือ "หัววัดอุณหภูมิ" ที่เป็นเซ็นเซอร์อีกชนิด
#   - เหมือนกับที่ "กรดแก่" และ "กรดอ่อน" เป็นประเภทของ "กรด"
#
# ==============================================================================

from time import sleep_ms


# ==============================================================================
# ส่วนที่ 1: แนวคิด Inheritance (15 นาที)
# Part 1: Inheritance Concept (15 minutes)
# ==============================================================================

print("=" * 60)
print("ส่วนที่ 1: แนวคิด Inheritance")
print("Part 1: Inheritance Concept")
print("=" * 60)

# -----------------------------------------------------------------------------
# Inheritance คืออะไร? (What is Inheritance?)
# -----------------------------------------------------------------------------
# Inheritance คือการสร้างคลาสใหม่จากคลาสที่มีอยู่แล้ว
# คลาสใหม่จะ "สืบทอด" attributes และ methods จากคลาสเดิม
#
# ศัพท์สำคัญ (Important Terms):
#   - Parent Class / Base Class / Super Class = คลาสแม่
#   - Child Class / Derived Class / Sub Class = คลาสลูก
#
# Syntax:
#   class ChildClass(ParentClass):
#       pass
# -----------------------------------------------------------------------------


# ตัวอย่าง 1.1: คลาสแม่พื้นฐาน (Basic Parent Class)
class Sensor:
    """
    คลาสพื้นฐานสำหรับเซ็นเซอร์ทุกชนิด (Base class for all sensors)

    นี่คือคลาสแม่ที่กำหนด "โครงสร้างพื้นฐาน" ที่เซ็นเซอร์ทุกชนิดควรมี
    เปรียบเหมือน "สูตรโครงสร้างทั่วไป" ในเคมี
    """

    def __init__(self, name, pin):
        """
        Constructor ของคลาสแม่

        Args:
            name (str): ชื่อเซ็นเซอร์ (Sensor name)
            pin (int): หมายเลขขา GPIO (GPIO pin number)
        """
        self.name = name        # ทุกเซ็นเซอร์มีชื่อ (Every sensor has a name)
        self.pin = pin          # ทุกเซ็นเซอร์ต่อกับ GPIO (Every sensor connects to GPIO)
        self.read_count = 0     # นับจำนวนครั้งที่อ่าน (Count readings)

        print(f"สร้าง {name} ที่ GPIO{pin} (Created {name} on GPIO{pin})")

    def read(self):
        """
        อ่านค่าจากเซ็นเซอร์ (Read value from sensor)

        นี่คือ "abstract method" - คลาสลูกต้อง override
        เหมือน "method template" ที่บอกว่าเซ็นเซอร์ต้องอ่านค่าได้
        """
        raise NotImplementedError("คลาสลูกต้อง implement read()")

    def log(self, message):
        """
        แสดงข้อความ log (Display log message)

        Method นี้ใช้ได้กับเซ็นเซอร์ทุกชนิด (Shared by all sensors)
        """
        print(f"[{self.name}] {message}")


# ตัวอย่าง 1.2: คลาสลูก - PHSensor (Child Class - PHSensor)
class PHSensor(Sensor):
    """
    เซ็นเซอร์ pH สืบทอดจาก Sensor (pH Sensor inherits from Sensor)

    class PHSensor(Sensor):  <-- บอกว่า PHSensor สืบทอดจาก Sensor

    PHSensor ได้รับ:
      - name, pin, read_count จาก Sensor
      - log() method จาก Sensor

    PHSensor เพิ่มเติม:
      - slope, intercept สำหรับคำนวณ pH
      - read_ph() method เฉพาะ
    """

    def __init__(self, pin=25, slope=-5.79, intercept=16.77):
        """
        Constructor ของ PHSensor

        หลักสำคัญ: ต้องเรียก super().__init__() ก่อนเสมอ
        เพื่อให้ Sensor ทำการ initialize ก่อน
        """
        # ===== เรียก constructor ของคลาสแม่ (Sensor) =====
        # super() = คลาสแม่ (Sensor)
        # __init__() = constructor ของคลาสแม่
        super().__init__("pH Sensor", pin)

        # ===== เพิ่ม attributes เฉพาะของ PHSensor =====
        self.slope = slope            # ความชันจาก calibration
        self.intercept = intercept    # จุดตัดแกน y จาก calibration

        self.log(f"สมการ: pH = {slope:.4f} * V + {intercept:.4f}")

    def read(self):
        """
        Override method read() จากคลาสแม่

        แทนที่จะ raise NotImplementedError
        เราคืนค่า pH จริง (จำลอง)
        """
        # จำลองการอ่านค่า (Simulate reading)
        voltage = 1.5  # จำลองแรงดัน (Simulated voltage)
        ph = self.slope * voltage + self.intercept

        self.read_count += 1  # ใช้ attribute จากคลาสแม่

        return ph

    def read_ph(self):
        """
        Method เฉพาะของ PHSensor (PHSensor-specific method)

        Method นี้ไม่มีใน Sensor - เป็นของ PHSensor เท่านั้น
        """
        return self.read()


# ตัวอย่าง 1.3: คลาสลูก - TempSensor (Child Class - TempSensor)
class TempSensor(Sensor):
    """
    เซ็นเซอร์อุณหภูมิ สืบทอดจาก Sensor (Temperature Sensor inherits from Sensor)
    """

    def __init__(self, pin=16, default_temp=25.0):
        """
        Constructor ของ TempSensor
        """
        # เรียก constructor ของคลาสแม่
        super().__init__("Temperature Sensor", pin)

        # Attributes เฉพาะของ TempSensor
        self.default_temp = default_temp

    def read(self):
        """
        Override method read()
        คืนค่าอุณหภูมิ (จำลอง)
        """
        # จำลองการอ่านค่า
        temp = self.default_temp + 0.5  # จำลองอุณหภูมิ
        self.read_count += 1
        return temp

    def read_celsius(self):
        """Method เฉพาะของ TempSensor"""
        return self.read()

    def read_fahrenheit(self):
        """Method เฉพาะของ TempSensor"""
        celsius = self.read()
        return celsius * 9/5 + 32


# ==============================================================================
# ส่วนที่ 2: ทดลองใช้งาน (15 นาที)
# Part 2: Hands-on Practice (15 minutes)
# ==============================================================================

if __name__ == "__main__":
    try:
        print("\n" + "=" * 60)
        print("ส่วนที่ 2: ทดลองใช้งาน")
        print("Part 2: Hands-on Practice")
        print("=" * 60)

        # สร้าง objects
        print("\n--- สร้าง sensor objects ---")
        ph_sensor = PHSensor()
        temp_sensor = TempSensor()

        # ตรวจสอบการ inherit
        print("\n--- ตรวจสอบการสืบทอด (Check Inheritance) ---")

        # isinstance() ตรวจสอบว่า object เป็น instance ของ class หรือไม่
        print(f"ph_sensor เป็น PHSensor? {isinstance(ph_sensor, PHSensor)}")    # True
        print(f"ph_sensor เป็น Sensor? {isinstance(ph_sensor, Sensor)}")        # True!
        print(f"temp_sensor เป็น TempSensor? {isinstance(temp_sensor, TempSensor)}")  # True
        print(f"temp_sensor เป็น Sensor? {isinstance(temp_sensor, Sensor)}")    # True!

        # issubclass() ตรวจสอบว่า class สืบทอดจาก class อื่นหรือไม่
        print(f"\nPHSensor สืบทอดจาก Sensor? {issubclass(PHSensor, Sensor)}")    # True
        print(f"TempSensor สืบทอดจาก Sensor? {issubclass(TempSensor, Sensor)}")  # True

        # ใช้ attributes ที่สืบทอด
        print("\n--- Attributes ที่สืบทอดจาก Sensor ---")
        print(f"ph_sensor.name: {ph_sensor.name}")        # จาก Sensor
        print(f"ph_sensor.pin: {ph_sensor.pin}")          # จาก Sensor
        print(f"temp_sensor.name: {temp_sensor.name}")    # จาก Sensor
        print(f"temp_sensor.pin: {temp_sensor.pin}")      # จาก Sensor

        # ใช้ methods ที่สืบทอด
        print("\n--- Methods ที่สืบทอดจาก Sensor ---")
        ph_sensor.log("ทดสอบ log() method")      # log() มาจาก Sensor
        temp_sensor.log("ทดสอบ log() method")    # log() มาจาก Sensor

        # ใช้ methods ที่ override
        print("\n--- Methods ที่ Override ---")
        ph = ph_sensor.read()           # read() ของ PHSensor (override)
        temp = temp_sensor.read()       # read() ของ TempSensor (override)
        print(f"pH: {ph:.2f}")
        print(f"Temperature: {temp:.2f} C")


        # ==============================================================================
        # ส่วนที่ 3: Polymorphism (15 นาที)
        # Part 3: Polymorphism (15 minutes)
        # ==============================================================================

        print("\n" + "=" * 60)
        print("ส่วนที่ 3: Polymorphism")
        print("Part 3: Polymorphism")
        print("=" * 60)

        print("""
Polymorphism (พหุสัณฐาน) คือความสามารถในการใช้ objects ต่างชนิด
ผ่าน interface เดียวกัน

เนื่องจาก PHSensor และ TempSensor สืบทอดจาก Sensor
เราสามารถใส่ทั้งคู่ใน list เดียวกันและเรียก read() ได้
โดยไม่ต้องรู้ว่าเป็นเซ็นเซอร์ชนิดไหน

เปรียบเหมือน: เราสามารถ "วัดค่า" จากเครื่องมือวัดต่างๆ ได้
โดยใช้หลักการเดียวกัน แม้เครื่องมือจะทำงานต่างกัน
""")

        # เก็บเซ็นเซอร์หลายชนิดในลิสต์เดียว
        sensors = [ph_sensor, temp_sensor]

        print("\n--- วนลูปอ่านค่าจากทุกเซ็นเซอร์ ---")
        for sensor in sensors:
            # ไม่ต้องรู้ว่าเป็น PHSensor หรือ TempSensor
            # แค่รู้ว่ามี read() method
            value = sensor.read()
            sensor.log(f"ค่าที่อ่านได้: {value:.2f}")

        # ฟังก์ชันที่รับ Sensor ใดๆ (Function that accepts any Sensor)
        def analyze_sensor(sensor):
            """
            ฟังก์ชันที่ทำงานกับ Sensor ใดๆ (Works with any Sensor)

            นี่คือพลังของ Polymorphism:
            - ฟังก์ชันเดียวใช้ได้กับหลาย sensor types
            - ไม่ต้องเขียนโค้ดซ้ำสำหรับแต่ละ type
            """
            print(f"\nวิเคราะห์ {sensor.name}:")
            print(f"  ต่อที่ GPIO{sensor.pin}")
            print(f"  จำนวนครั้งที่อ่าน: {sensor.read_count}")

            # อ่านค่าเพิ่ม 3 ครั้ง
            for i in range(3):
                value = sensor.read()
                print(f"  ค่าที่ {i+1}: {value:.2f}")

        print("\n--- ใช้ฟังก์ชันกับเซ็นเซอร์หลายชนิด ---")
        analyze_sensor(ph_sensor)
        analyze_sensor(temp_sensor)


        # ==============================================================================
        # ส่วนที่ 4: สรุป
        # Part 4: Summary
        # ==============================================================================

        print("\n" + "=" * 60)
        print("สรุป (Summary)")
        print("=" * 60)

        print("""
สิ่งที่เรียนรู้ในบทนี้:

1. Inheritance (การสืบทอด):
   - สร้างคลาสลูกจากคลาสแม่: class Child(Parent)
   - คลาสลูกได้รับ attributes และ methods จากคลาสแม่

2. super().__init__():
   - เรียก constructor ของคลาสแม่
   - ต้องเรียกก่อนใช้ self ในคลาสลูก

3. Method Overriding:
   - คลาสลูกสามารถกำหนด method ชื่อเดียวกับคลาสแม่
   - Method ใหม่จะแทนที่ method เดิม

4. Polymorphism:
   - ใช้ objects ต่างชนิดผ่าน interface เดียวกัน
   - ช่วยให้โค้ดยืดหยุ่นและใช้ซ้ำได้

การเชื่อมโยงกับเคมี:
   - BaseSensor = หลักการทั่วไปของเซ็นเซอร์
   - PHSensor = หัววัด pH (ใช้สมการ Nernst)
   - TempSensor = หัววัดอุณหภูมิ (DS18B20)
   - ทั้งหมดทำงานเหมือนกัน: อ่านค่า -> แปลง -> แสดงผล
""")

        print("=" * 60)
        print("จบบทเรียน Inheritance Basics")
        print("(End of Inheritance Basics)")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n")
        print("=" * 50)
        print("หยุดโปรแกรมโดยผู้ใช้ (Stopped by user - Ctrl+C)")
        print("=" * 50)
    except Exception as e:
        print(f"\n*** ข้อผิดพลาด (Error): {e} ***")
