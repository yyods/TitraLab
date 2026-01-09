# ==============================================================================
# exercise_03_composition_solution.py - เฉลย: Composition
# (Exercise: Composition - Solution)
# ==============================================================================
# เวลาโดยประมาณ: 20 นาที (Estimated time: 20 minutes)
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
# 1. เข้าใจหลักการ Composition ("has-a" relationship)
#    Understand Composition principle ("has-a" relationship)
# 2. สามารถสร้างคลาสที่มี list เป็น attribute ภายใน
#    Can create a class that contains a list as an internal attribute
# 3. เข้าใจการจัดการข้อมูลผ่าน methods ของคลาส
#    Understand data management through class methods
#
# Chemistry Connection (ความเชื่อมโยงกับเคมี):
# - ในการไทเทรชัน เราต้องบันทึกข้อมูล pH และปริมาตรหลายจุด
#   During titration, we need to record multiple pH and volume data points
# - DataLogger ช่วยจัดเก็บและวิเคราะห์ข้อมูลเหล่านี้อย่างเป็นระบบ
#   DataLogger helps store and analyze this data systematically
# - สถิติพื้นฐานช่วยตรวจสอบความถูกต้องของการทดลอง
#   Basic statistics help verify experimental accuracy
#
# ==============================================================================

from time import ticks_ms, ticks_diff


class DataLogger:
    """
    คลาสบันทึกข้อมูลการทดลอง (Data logging class for experiments)

    ใช้ Composition: DataLogger "has-a" list สำหรับเก็บข้อมูล
    Uses Composition: DataLogger "has-a" list for storing data

    Composition คืออะไร?
    - Composition คือการออกแบบที่คลาสหนึ่ง "มี" (has-a) object อื่นเป็นส่วนประกอบ
    - ในที่นี้ DataLogger "มี" list สำหรับเก็บข้อมูล
    - ต่างจาก Inheritance ที่เป็น "is-a" relationship

    What is Composition?
    - Composition is a design where one class "has" another object as a component
    - Here, DataLogger "has" a list for storing data
    - Different from Inheritance which is an "is-a" relationship

    Chemistry Connection:
    - บันทึกข้อมูล pH และปริมาตรระหว่างการไทเทรชัน
    - Records pH and volume data during titration
    - ช่วยติดตามการเปลี่ยนแปลง pH ตลอดการทดลอง
    - Helps track pH changes throughout the experiment

    เฉลย: คลาสที่สมบูรณ์พร้อมคำอธิบาย
    """

    def __init__(self, name="Experiment"):
        """
        สร้าง DataLogger object (Initialize DataLogger object)

        Args:
            name (str): ชื่อการทดลอง (Experiment name)

        เฉลย:
        - _name: เก็บชื่อการทดลอง
        - _data: list เปล่าสำหรับเก็บข้อมูล (นี่คือ Composition!)
        - _start_time: เวลาเริ่มต้นสำหรับคำนวณ timestamp
        """
        # เฉลย: เก็บชื่อการทดลอง (Store experiment name)
        self._name = name

        # เฉลย: สร้าง list เปล่า - นี่คือ Composition!
        # DataLogger "has-a" list สำหรับเก็บข้อมูล
        # DataLogger "has-a" list for storing data
        self._data = []

        # เฉลย: บันทึกเวลาเริ่มต้น (Record start time)
        self._start_time = ticks_ms()

        # แสดงข้อความเมื่อสร้าง object (Display message when object is created)
        print(f"[DataLogger] สร้างใหม่: {name}")

    # =========================================================================
    # Properties (คุณสมบัติ)
    # =========================================================================

    @property
    def name(self):
        """
        ชื่อการทดลอง (Experiment name)

        เฉลย: return ค่า _name

        Returns:
            str: ชื่อการทดลอง
        """
        return self._name

    @property
    def count(self):
        """
        จำนวนข้อมูลที่บันทึกไว้ (Number of recorded data points)

        เฉลย: ใช้ len() นับจำนวนข้อมูลใน list

        Returns:
            int: จำนวนข้อมูล
        """
        return len(self._data)

    # =========================================================================
    # Data Management Methods (เมธอดจัดการข้อมูล)
    # =========================================================================

    def add_point(self, volume, ph, temperature=25.0):
        """
        เพิ่มจุดข้อมูลใหม่ (Add a new data point)

        Args:
            volume (float): ปริมาตรสารละลาย (mL)
            ph (float): ค่า pH ที่วัดได้
            temperature (float): อุณหภูมิ (C) ค่าเริ่มต้น 25.0

        เฉลย:
        1. คำนวณ timestamp จากเวลาที่ผ่านไป
        2. สร้าง dict เก็บข้อมูลทุกค่า
        3. append เข้า _data list (การใช้ Composition)
        """
        # เฉลย: คำนวณ timestamp (เวลาที่ผ่านไปตั้งแต่เริ่มต้น หน่วย ms)
        # ticks_diff ช่วยจัดการกรณี overflow ของ ticks_ms
        timestamp = ticks_diff(ticks_ms(), self._start_time)

        # เฉลย: สร้าง dict เก็บข้อมูลจุดนี้
        # ใช้ dict เพราะเก็บข้อมูลหลายประเภทได้สะดวก
        point = {
            'volume': volume,
            'ph': ph,
            'temperature': temperature,
            'timestamp': timestamp
        }

        # เฉลย: เพิ่มข้อมูลเข้า list (นี่คือการใช้ Composition!)
        # DataLogger delegate การเก็บข้อมูลให้ list
        self._data.append(point)

        # เฉลย: แสดงข้อความยืนยันการเพิ่มข้อมูล
        print(f"[DataLogger] เพิ่มจุด #{len(self._data)}: V={volume:.2f}mL, pH={ph:.2f}")

    def get_last(self):
        """
        ดึงข้อมูลล่าสุด (Get the last data point)

        เฉลย:
        - ตรวจสอบว่ามีข้อมูลหรือไม่ก่อน
        - ใช้ index -1 เพื่อเข้าถึงข้อมูลตัวสุดท้าย

        Returns:
            dict or None: ข้อมูลล่าสุด หรือ None ถ้าไม่มีข้อมูล
        """
        # เฉลย: ตรวจสอบว่ามีข้อมูลหรือไม่
        # if self._data จะเป็น True ถ้า list ไม่ว่าง
        if self._data:
            return self._data[-1]  # ใช้ -1 เข้าถึงตัวสุดท้าย
        return None

    def get_all(self):
        """
        ดึงข้อมูลทั้งหมด (Get all data points)

        เฉลย: return list _data โดยตรง

        Returns:
            list: ข้อมูลทั้งหมดที่บันทึกไว้
        """
        return self._data

    def clear(self):
        """
        ล้างข้อมูลทั้งหมด (Clear all data)

        เฉลย:
        - ใช้ .clear() ล้าง list (เร็วกว่า = [])
        - reset เวลาเริ่มต้นเพื่อเริ่มนับ timestamp ใหม่
        """
        # เฉลย: ล้างข้อมูลใน list
        # .clear() เร็วกว่าและใช้ memory น้อยกว่า = []
        self._data.clear()

        # เฉลย: reset เวลาเริ่มต้นสำหรับ timestamp ใหม่
        self._start_time = ticks_ms()

        # เฉลย: แสดงข้อความยืนยัน
        print(f"[DataLogger] ล้างข้อมูลทั้งหมดแล้ว")

    # =========================================================================
    # Statistics Methods (เมธอดคำนวณสถิติ)
    # =========================================================================

    def get_statistics(self):
        """
        คำนวณสถิติพื้นฐานของค่า pH (Calculate basic pH statistics)

        Chemistry Context:
        - min_ph: ค่า pH ต่ำสุด (จุดที่เป็นกรดที่สุด)
        - max_ph: ค่า pH สูงสุด (จุดที่เป็นเบสที่สุด)
        - avg_ph: ค่า pH เฉลี่ย
        - ค่าเหล่านี้ช่วยตรวจสอบว่าการไทเทรชันครอบคลุมช่วง pH ที่ต้องการหรือไม่

        เฉลย:
        1. ตรวจสอบว่ามีข้อมูลก่อน
        2. ใช้ list comprehension ดึงค่า pH
        3. คำนวณสถิติด้วย built-in functions

        Returns:
            dict or None: สถิติ หรือ None ถ้าไม่มีข้อมูล
        """
        # เฉลย: ตรวจสอบว่ามีข้อมูลหรือไม่
        if not self._data:
            return None

        # เฉลย: ดึงค่า pH ทั้งหมดด้วย list comprehension
        # นี่คือวิธี Pythonic ในการดึงค่าจาก list of dicts
        ph_values = [point['ph'] for point in self._data]

        # เฉลย: คำนวณสถิติด้วย built-in functions
        min_ph = min(ph_values)
        max_ph = max(ph_values)
        avg_ph = sum(ph_values) / len(ph_values)

        # เฉลย: return dict ที่มีสถิติทั้งหมด
        return {
            'min_ph': min_ph,
            'max_ph': max_ph,
            'avg_ph': avg_ph,
            'count': len(self._data)
        }

    def __str__(self):
        """
        แสดงข้อมูลสรุปของ DataLogger (Display DataLogger summary)

        เฉลย: สร้าง string ที่อ่านเข้าใจง่าย

        Returns:
            str: ข้อมูลสรุป
        """
        return f"DataLogger '{self._name}': {len(self._data)} points"


# ==============================================================================
# ทดสอบโค้ด
# Test code
# ==============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("เฉลยแบบฝึกหัดที่ 3: Composition - DataLogger")
    print("Exercise 3 Solution: Composition - DataLogger")
    print("=" * 60)

    # === สร้าง DataLogger ===
    print("\n--- สร้าง DataLogger ---")
    logger = DataLogger("Acid-Base Titration")
    print(f"ชื่อการทดลอง: {logger.name}")
    print(f"จำนวนข้อมูลเริ่มต้น: {logger.count}")

    # === เพิ่มข้อมูลจำลองการไทเทรชัน ===
    print("\n--- เพิ่มข้อมูลจำลอง (Simulated Titration Data) ---")

    # ข้อมูลจำลองการไทเทรชันกรดแก่-เบสแก่
    # Simulated strong acid-strong base titration data
    titration_data = [
        (0.0, 2.0),    # เริ่มต้น - กรดเข้มข้น (Starting - concentrated acid)
        (5.0, 2.5),    # เติม base ไปบ้าง (Some base added)
        (10.0, 3.0),   # buffer region
        (15.0, 3.5),
        (20.0, 4.0),
        (22.0, 4.5),
        (24.0, 5.5),   # เข้าใกล้จุดสมมูล (Approaching equivalence point)
        (25.0, 7.0),   # จุดสมมูล (equivalence point)
        (26.0, 9.0),   # ผ่านจุดสมมูล (Past equivalence point)
        (28.0, 10.5),
        (30.0, 11.0),  # excess base
    ]

    for volume, ph in titration_data:
        logger.add_point(volume, ph, temperature=25.0)

    # === ทดสอบ count ===
    print(f"\n--- ตรวจสอบจำนวนข้อมูล ---")
    print(f"จำนวนข้อมูลทั้งหมด: {logger.count}")

    # === ทดสอบ get_last ===
    print(f"\n--- ข้อมูลล่าสุด ---")
    last = logger.get_last()
    if last:
        print(f"Volume: {last['volume']:.2f} mL")
        print(f"pH: {last['ph']:.2f}")
        print(f"Temperature: {last['temperature']:.1f} C")
        print(f"Timestamp: {last['timestamp']} ms")
    else:
        print("ไม่มีข้อมูล")

    # === ทดสอบ get_statistics ===
    print(f"\n--- สถิติ pH ---")
    stats = logger.get_statistics()
    if stats:
        print(f"pH ต่ำสุด (min): {stats['min_ph']:.2f} (กรดที่สุด)")
        print(f"pH สูงสุด (max): {stats['max_ph']:.2f} (เบสที่สุด)")
        print(f"pH เฉลี่ย (avg): {stats['avg_ph']:.2f}")
        print(f"จำนวนจุด: {stats['count']}")

        # Chemistry insight
        print(f"\n  Chemistry Insight:")
        print(f"  - ช่วง pH: {stats['min_ph']:.1f} - {stats['max_ph']:.1f}")
        print(f"  - ครอบคลุม {stats['max_ph'] - stats['min_ph']:.1f} หน่วย pH")
        if stats['min_ph'] < 4 and stats['max_ph'] > 10:
            print(f"  - ครอบคลุมช่วง pH เพียงพอสำหรับการไทเทรชันกรดแก่-เบสแก่")
    else:
        print("ไม่มีข้อมูลสำหรับคำนวณสถิติ")

    # === ทดสอบ __str__ ===
    print(f"\n--- __str__ ---")
    print(logger)

    # === ทดสอบ get_all ===
    print(f"\n--- ข้อมูลทั้งหมด (แสดง 3 รายการแรก) ---")
    all_data = logger.get_all()
    for i, point in enumerate(all_data[:3]):
        print(f"  #{i+1}: V={point['volume']:.1f}mL, pH={point['ph']:.2f}, t={point['timestamp']}ms")
    print(f"  ... (และอีก {len(all_data)-3} รายการ)")

    # === ทดสอบ clear ===
    print(f"\n--- ล้างข้อมูล ---")
    logger.clear()
    print(f"จำนวนข้อมูลหลังล้าง: {logger.count}")
    print(f"get_last() หลังล้าง: {logger.get_last()}")
    print(f"get_statistics() หลังล้าง: {logger.get_statistics()}")

    # === สรุปแนวคิด Composition ===
    print("\n" + "=" * 60)
    print("สรุปแนวคิด Composition ที่ใช้ในแบบฝึกหัดนี้:")
    print("=" * 60)
    print("""
    1. DataLogger "has-a" list (_data)
       - DataLogger ไม่ได้สืบทอดจาก list
       - แต่ "มี" list เป็นส่วนประกอบภายใน

    2. Delegation (การมอบหมายงาน):
       - add_point() -> self._data.append()
       - get_last()  -> self._data[-1]
       - clear()     -> self._data.clear()
       - count       -> len(self._data)

    3. ข้อดีของ Composition:
       - ซ่อนรายละเอียดการเก็บข้อมูล
       - เปลี่ยนโครงสร้างข้อมูลได้ง่าย
       - เพิ่ม logic เช่น validation ได้
       - Interface ชัดเจน
    """)
    print("=" * 60)
    print("ทดสอบเสร็จสิ้น!")
    print("Test completed!")
    print("=" * 60)
