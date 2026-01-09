# ==============================================================================
# exercise_03_composition_starter.py - แบบฝึกหัด: Composition
# (Exercise: Composition - Starter Code)
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
# โจทย์: สร้างคลาส DataLogger ที่ใช้ Composition
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

    TODO: นิสิตต้องเติมโค้ดให้สมบูรณ์ในแต่ละ method
    """

    def __init__(self, name="Experiment"):
        """
        สร้าง DataLogger object (Initialize DataLogger object)

        Args:
            name (str): ชื่อการทดลอง (Experiment name)

        TODO: สร้าง attributes ดังนี้
        1. _name: เก็บชื่อการทดลอง (store experiment name)
        2. _data: list เปล่าสำหรับเก็บข้อมูล (empty list for storing data)
        3. _start_time: เวลาเริ่มต้นจาก ticks_ms() (start time from ticks_ms())

        หมายเหตุ: _data คือ Composition - DataLogger "has-a" list
        Note: _data is Composition - DataLogger "has-a" list
        """
        # TODO: สร้าง _name attribute เก็บชื่อการทดลอง
        # self._name = name
        pass

        # TODO: สร้าง _data เป็น list เปล่า (นี่คือ Composition!)
        # self._data = []
        pass

        # TODO: บันทึกเวลาเริ่มต้น
        # self._start_time = ticks_ms()
        pass

        # แสดงข้อความเมื่อสร้าง object (Display message when object is created)
        # print(f"[DataLogger] สร้างใหม่: {name}")

    # =========================================================================
    # Properties (คุณสมบัติ)
    # =========================================================================

    @property
    def name(self):
        """
        ชื่อการทดลอง (Experiment name)

        TODO: return ค่า _name

        Returns:
            str: ชื่อการทดลอง
        """
        # TODO: return _name
        pass

    @property
    def count(self):
        """
        จำนวนข้อมูลที่บันทึกไว้ (Number of recorded data points)

        TODO: return จำนวนข้อมูลใน _data โดยใช้ len()

        Returns:
            int: จำนวนข้อมูล
        """
        # TODO: return len(self._data)
        pass

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

        TODO:
        1. คำนวณ timestamp = ticks_diff(ticks_ms(), self._start_time)
        2. สร้าง dict ที่มี keys: 'volume', 'ph', 'temperature', 'timestamp'
        3. append dict นี้เข้าไปใน self._data
        4. print ข้อความยืนยันการเพิ่มข้อมูล

        ตัวอย่างโครงสร้าง dict:
        {
            'volume': 5.0,
            'ph': 3.5,
            'temperature': 25.0,
            'timestamp': 1234
        }
        """
        # TODO: คำนวณ timestamp (เวลาที่ผ่านไปตั้งแต่เริ่มต้น)
        # timestamp = ticks_diff(ticks_ms(), self._start_time)
        pass

        # TODO: สร้าง dict เก็บข้อมูล
        # point = {
        #     'volume': volume,
        #     'ph': ph,
        #     'temperature': temperature,
        #     'timestamp': timestamp
        # }
        pass

        # TODO: เพิ่มข้อมูลเข้า list (นี่คือการใช้ Composition!)
        # self._data.append(point)
        pass

        # TODO: แสดงข้อความยืนยัน
        # print(f"[DataLogger] เพิ่มจุด #{len(self._data)}: V={volume:.2f}mL, pH={ph:.2f}")
        pass

    def get_last(self):
        """
        ดึงข้อมูลล่าสุด (Get the last data point)

        TODO:
        1. ตรวจสอบว่ามีข้อมูลใน _data หรือไม่
        2. ถ้ามี return ข้อมูลตัวสุดท้าย (self._data[-1])
        3. ถ้าไม่มี return None

        Returns:
            dict or None: ข้อมูลล่าสุด หรือ None ถ้าไม่มีข้อมูล
        """
        # TODO: ตรวจสอบว่ามีข้อมูลหรือไม่
        # if self._data:
        #     return self._data[-1]
        # return None
        pass

    def get_all(self):
        """
        ดึงข้อมูลทั้งหมด (Get all data points)

        TODO: return list _data ทั้งหมด

        Returns:
            list: ข้อมูลทั้งหมดที่บันทึกไว้
        """
        # TODO: return self._data
        pass

    def clear(self):
        """
        ล้างข้อมูลทั้งหมด (Clear all data)

        TODO:
        1. ล้าง _data โดยใช้ .clear() หรือ = []
        2. reset _start_time เป็นเวลาปัจจุบัน
        3. print ข้อความยืนยันการล้างข้อมูล
        """
        # TODO: ล้างข้อมูล
        # self._data.clear()
        pass

        # TODO: reset เวลาเริ่มต้น
        # self._start_time = ticks_ms()
        pass

        # TODO: แสดงข้อความยืนยัน
        # print(f"[DataLogger] ล้างข้อมูลทั้งหมดแล้ว")
        pass

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

        TODO:
        1. ตรวจสอบว่ามีข้อมูลหรือไม่ ถ้าไม่มี return None
        2. ดึงค่า pH ทั้งหมดจาก _data มาเก็บใน list
        3. คำนวณ min, max, avg
        4. return dict ที่มี keys: 'min_ph', 'max_ph', 'avg_ph', 'count'

        Returns:
            dict or None: สถิติ หรือ None ถ้าไม่มีข้อมูล

        Hint: ใช้ list comprehension เพื่อดึงค่า pH
        ph_values = [point['ph'] for point in self._data]
        """
        # TODO: ตรวจสอบว่ามีข้อมูลหรือไม่
        # if not self._data:
        #     return None
        pass

        # TODO: ดึงค่า pH ทั้งหมด
        # ph_values = [point['ph'] for point in self._data]
        pass

        # TODO: คำนวณสถิติ
        # min_ph = min(ph_values)
        # max_ph = max(ph_values)
        # avg_ph = sum(ph_values) / len(ph_values)
        pass

        # TODO: return dict
        # return {
        #     'min_ph': min_ph,
        #     'max_ph': max_ph,
        #     'avg_ph': avg_ph,
        #     'count': len(self._data)
        # }
        pass

    def __str__(self):
        """
        แสดงข้อมูลสรุปของ DataLogger (Display DataLogger summary)

        TODO: return string ที่แสดงชื่อและจำนวนข้อมูล

        Returns:
            str: ข้อมูลสรุป
        """
        # TODO: return f"DataLogger '{self._name}': {len(self._data)} points"
        pass


# ==============================================================================
# ทดสอบโค้ด (ไม่ต้องแก้ไข)
# Test code (Do not modify)
# ==============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("แบบฝึกหัดที่ 3: Composition - DataLogger")
    print("Exercise 3: Composition - DataLogger")
    print("=" * 60)

    try:
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
            (0.0, 2.0),    # เริ่มต้น - กรดเข้มข้น
            (5.0, 2.5),    # เติม base ไปบ้าง
            (10.0, 3.0),   # buffer region
            (15.0, 3.5),
            (20.0, 4.0),
            (22.0, 4.5),
            (24.0, 5.5),   # เข้าใกล้จุดสมมูล
            (25.0, 7.0),   # จุดสมมูล (equivalence point)
            (26.0, 9.0),   # ผ่านจุดสมมูล
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
        else:
            print("ไม่มีข้อมูลสำหรับคำนวณสถิติ")

        # === ทดสอบ __str__ ===
        print(f"\n--- __str__ ---")
        print(logger)

        # === ทดสอบ get_all ===
        print(f"\n--- ข้อมูลทั้งหมด (แสดง 3 รายการแรก) ---")
        all_data = logger.get_all()
        for i, point in enumerate(all_data[:3]):
            print(f"  #{i+1}: V={point['volume']:.1f}mL, pH={point['ph']:.2f}")
        print(f"  ... (และอีก {len(all_data)-3} รายการ)")

        # === ทดสอบ clear ===
        print(f"\n--- ล้างข้อมูล ---")
        logger.clear()
        print(f"จำนวนข้อมูลหลังล้าง: {logger.count}")
        print(f"get_last() หลังล้าง: {logger.get_last()}")
        print(f"get_statistics() หลังล้าง: {logger.get_statistics()}")

        print("\n" + "=" * 60)
        print("ทดสอบเสร็จสิ้น!")
        print("Test completed!")
        print("=" * 60)

    except AttributeError as e:
        print("\n" + "=" * 60)
        print("*** โค้ดยังไม่สมบูรณ์ (Code incomplete) ***")
        print(f"*** ข้อผิดพลาด: {e} ***")
        print("*** กรุณาเติมโค้ดในส่วน TODO ***")
        print("*** Please complete the TODO sections ***")
        print("=" * 60)
    except TypeError as e:
        print(f"\n*** TypeError: {e} ***")
        print("*** ตรวจสอบการ return ค่าจาก methods ***")
    except Exception as e:
        print(f"\n*** ข้อผิดพลาดอื่น (Other error): {e} ***")
        import sys
        sys.print_exception(e)
