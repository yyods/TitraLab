# ==============================================================================
# 08_intro_oop.py - OOP Basics for Chemistry Students
# ==============================================================================
# Week 1 Core: Class, Object, __init__, self
# Time: ~30 minutes
# ==============================================================================

# ==============================================================================
# Why OOP? (ทำไมต้องใช้ OOP?)
# ==============================================================================
# In chemistry lab, we have equipment with properties and actions:
#   - Beaker: has capacity, can add/pour liquid
#   - pH Meter: can read pH value
#   - LED: can turn on/off
#
# OOP lets us model these as code!
# ==============================================================================


# ==============================================================================
# PART 1: Class = Blueprint (คลาส = พิมพ์เขียว)
# ==============================================================================

class Beaker:
    """
    คลาส Beaker - จำลองบีกเกอร์ในห้องปฏิบัติการ
    (Beaker class - simulates a laboratory beaker)

    Class is like a recipe - it's not the cake, but tells how to make one.
    """

    def __init__(self, capacity_ml):
        """
        Constructor - ทำงานเมื่อสร้าง object (runs when creating object)

        Args:
            capacity_ml: ความจุสูงสุด (maximum capacity in mL)
        """
        # self.xxx = instance variable (ตัวแปรของ object นี้)
        self.capacity = capacity_ml     # ความจุ (capacity)
        self.current_volume = 0         # ปริมาตรปัจจุบัน (current volume)
        self.contents = "empty"         # สารในบีกเกอร์ (contents)

        print(f"Created beaker: {capacity_ml} mL")

    def add_liquid(self, volume_ml, liquid_name):
        """เติมของเหลว (Add liquid to beaker)"""
        if self.current_volume + volume_ml > self.capacity:
            print("Error: Exceeds capacity!")
            return False

        self.current_volume += volume_ml
        self.contents = liquid_name
        print(f"Added {volume_ml} mL of {liquid_name}")
        return True

    def pour_out(self, volume_ml):
        """เทออก (Pour out liquid)"""
        actual = min(volume_ml, self.current_volume)
        self.current_volume -= actual
        if self.current_volume == 0:
            self.contents = "empty"
        print(f"Poured out {actual} mL")

    def get_info(self):
        """แสดงข้อมูล (Display info)"""
        print(f"Capacity: {self.capacity} mL")
        print(f"Current: {self.current_volume} mL")
        print(f"Contents: {self.contents}")


# ==============================================================================
# PART 2: Understanding 'self' (เข้าใจ self)
# ==============================================================================
#
# self = reference to the current object (ตัวอ้างอิงถึง object ปัจจุบัน)
#
# When you write:    beaker_1.add_liquid(100, "HCl")
# Python translates: Beaker.add_liquid(beaker_1, 100, "HCl")
#
# That's why self must be the first parameter!
#
# ==============================================================================
# RULE 1: self must be first parameter in every method
#         def my_method(self, arg1, arg2):  # Correct
#         def my_method(arg1, arg2):        # Wrong!
#
# RULE 2: Use self.xxx to access instance variables
#         self.capacity = 250   # Store in object
#         print(self.capacity)  # Read from object
#
# RULE 3: Use self.method() to call other methods in same class
#         def toggle(self):
#             if self.is_on:
#                 self.off()    # Calls off() on this object
# ==============================================================================


# ==============================================================================
# PART 3: Object = Instance created from Class
# ==============================================================================

if __name__ == "__main__":
    print("=" * 50)
    print("OOP Basics - Beaker Example")
    print("=" * 50)

    # --- Create Objects (สร้าง Object) ---
    print("\n--- Creating 2 beakers ---")
    beaker_1 = Beaker(250)    # 250 mL beaker
    beaker_2 = Beaker(500)    # 500 mL beaker

    # Each object has its own values!
    # beaker_1.capacity = 250, beaker_2.capacity = 500

    # --- Use Methods (ใช้งาน method) ---
    print("\n--- Adding liquids ---")
    beaker_1.add_liquid(100, "Distilled Water")
    beaker_2.add_liquid(200, "HCl 0.1M")

    # --- Display Info (แสดงข้อมูล) ---
    print("\n--- Beaker 1 Info ---")
    beaker_1.get_info()

    print("\n--- Beaker 2 Info ---")
    beaker_2.get_info()

    # --- Pour out (เทออก) ---
    print("\n--- Pour out from Beaker 1 ---")
    beaker_1.pour_out(50)
    beaker_1.get_info()

    # --- Summary (สรุป) ---
    print("\n" + "=" * 50)
    print("Summary:")
    print("=" * 50)
    print("""
1. Class = Blueprint (พิมพ์เขียว)
   - class Beaker: defines the "template"

2. Object = Instance from Class
   - beaker_1 and beaker_2 are different objects
   - Each has its own variable values

3. __init__ = Constructor
   - Runs automatically when creating object
   - Use to set initial values

4. self = Reference to current object
   - self.capacity means "this object's capacity"

5. Method = Function inside class
   - add_liquid(), pour_out(), get_info()
   - Call via object: beaker_1.add_liquid()
""")
