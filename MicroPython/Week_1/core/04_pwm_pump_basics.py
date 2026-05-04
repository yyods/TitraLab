# ==============================================================================
# 04_pwm_pump_basics.py - พื้นฐาน PWM สำหรับปั๊ม (PWM Basics for Pump Control)
# ==============================================================================
# สัปดาห์ที่ 1: พื้นฐาน PWM (Week 1: PWM Basics)
# เวลา: ~30 นาที (Time: ~30 minutes)
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจ PWM: ควบคุมความเร็วด้วย Duty Cycle
#   2. เข้าใจการควบคุมปั๊มสำหรับไทเทรชัน
#   3. เตรียมพร้อมสำหรับการไทเทรชันอัตโนมัติใน Week 3
#
# การเชื่อมโยงกับ Week 3 (Connection to Week 3):
#   - GPIO21 = Pump PWM output
#   - Phase 1: เร็ว (80%) -> Phase 2: กลาง (50%) -> Phase 3: ช้า (25%)
#
# ฮาร์ดแวร์ (Hardware):
#   - GPIO21 -> EL357N optocoupler -> MOSFET -> Pump 12V
# ==============================================================================

from machine import Pin, PWM
import time

# นำเข้าขา GPIO (Import GPIO pins)
try:
    from pins import PUMP_PIN, LED_GREEN, LED_RED
except ImportError:
    PUMP_PIN = 21     # ปั๊ม (Pump)
    LED_GREEN = 4     # สถานะปั๊มทำงาน
    LED_RED = 2       # สถานะปั๊มหยุด

# ==============================================================================
# ค่าคงที่ (Constants)
# ==============================================================================
PWM_FREQ = 1000      # ความถี่ PWM (Hz)
DUTY_MAX = 1023      # 10-bit PWM (0-1023)

# ความเร็วที่ใช้ในแต่ละ Phase ของไทเทรชัน (Titration phase speeds)
SPEED_FAST = 80      # Phase 1: ห่างจากจุดสมมูล
SPEED_MEDIUM = 50    # Phase 2: เข้าใกล้
SPEED_SLOW = 25      # Phase 3: ใกล้มาก


# ==============================================================================
# คลาส PumpController (Pump Controller Class)
# ==============================================================================
class PumpController:
    """
    คลาสควบคุมปั๊มสำหรับไทเทรชัน (Pump Controller for Titration)

    ใน Week 3 จะใช้สำหรับควบคุมปั๊มอัตโนมัติ
    In Week 3, used for automatic pump control

    ตัวอย่างการใช้ (Usage):
        pump = PumpController(21)
        pump.start(50)           # เริ่มที่ 50%
        pump.set_speed(25)       # ลดเหลือ 25%
        pump.stop()              # หยุดปั๊ม
    """

    def __init__(self, pin_number, name="Pump"):
        """
        สร้าง PumpController (Create PumpController)

        Args:
            pin_number (int): GPIO pin (21=Pump)
            name (str): ชื่อสำหรับแสดงผล
        """
        self.pin_number = pin_number
        self.name = name
        self.is_running = False
        self._pwm = PWM(Pin(pin_number))
        self._pwm.freq(PWM_FREQ)
        self._pwm.duty(0)  # เริ่มต้นปิด

        print(f"Pump '{name}' พร้อมใช้งานที่ GPIO{pin_number} (ready)")

    def start(self, speed_percent=100):
        """เปิดปั๊มที่ความเร็วที่กำหนด (Start pump at specified speed)"""
        duty = int((speed_percent / 100) * DUTY_MAX)
        duty = max(0, min(DUTY_MAX, duty))
        self._pwm.duty(duty)
        self.is_running = True
        print(f"Pump ON: {speed_percent}% (duty={duty})")

    def stop(self):
        """ปิดปั๊ม (Stop pump)"""
        self._pwm.duty(0)
        self.is_running = False
        print("Pump OFF")

    def set_speed(self, speed_percent):
        """ปรับความเร็วปั๊ม (Adjust pump speed)"""
        duty = int((speed_percent / 100) * DUTY_MAX)
        duty = max(0, min(DUTY_MAX, duty))
        self._pwm.duty(duty)
        self.is_running = duty > 0
        print(f"Speed: {speed_percent}% (duty={duty})")

    def deinit(self):
        """คืนทรัพยากร PWM (Release PWM resources)"""
        self.stop()
        self._pwm.deinit()


# ==============================================================================
# โปรแกรมหลัก (Main Program)
# ==============================================================================
if __name__ == "__main__":
    print("=" * 50)
    print("PWM Basics for Pump Control")
    print("พื้นฐาน PWM สำหรับปั๊มไทเทรชัน")
    print("=" * 50)
    print()
    print("กลยุทธ์ไทเทรชัน (Titration Strategy):")
    print(f"  Phase 1: เร็ว   ({SPEED_FAST}%) - ห่างจากจุดสมมูล")
    print(f"  Phase 2: กลาง  ({SPEED_MEDIUM}%) - เข้าใกล้")
    print(f"  Phase 3: ช้า   ({SPEED_SLOW}%) - ใกล้มาก")
    print("  Phase 4: หยุด  (0%) - ถึงจุดสมมูล!")
    print()
    print("กด Ctrl+C เพื่อหยุด")
    print("-" * 50)

    # สร้าง PumpController
    pump = PumpController(PUMP_PIN, "Titration")
    led_green = Pin(LED_GREEN, Pin.OUT)
    led_red = Pin(LED_RED, Pin.OUT)

    try:
        # จำลองการไทเทรชัน (Simulate titration phases)
        phases = [
            (SPEED_FAST, "Phase 1: ห่างจากจุดสมมูล", 2),
            (SPEED_MEDIUM, "Phase 2: เข้าใกล้", 2),
            (SPEED_SLOW, "Phase 3: ใกล้มาก", 2),
            (0, "Phase 4: ถึงจุดสมมูล!", 1)
        ]

        for speed, desc, duration in phases:
            print(f"\n{desc}")
            if speed > 0:
                pump.start(speed)
                led_green.on()
                led_red.off()
            else:
                pump.stop()
                led_green.off()
                led_red.on()
            time.sleep(duration)

    except KeyboardInterrupt:
        print("\n\nหยุดโปรแกรม (Program stopped)")

    finally:
        pump.deinit()
        led_green.off()
        led_red.off()
        print()
        print("=" * 50)
        print("สรุป (Summary):")
        print("-" * 50)
        print("  1. PWM ควบคุมความเร็วด้วย Duty Cycle 0-1023")
        print("  2. ความถี่ 1000 Hz เหมาะสำหรับปั๊ม")
        print("  3. Week 3: ปรับความเร็วตามค่า pH อัตโนมัติ")
        print("=" * 50)
