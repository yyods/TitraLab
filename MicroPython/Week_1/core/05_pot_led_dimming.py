# ==============================================================================
# 05_pot_led_dimming.py - ควบคุม LED ด้วย Potentiometer (LED Dimming with Pot)
# ==============================================================================
# สัปดาห์ที่ 1: รวม ADC + PWM (Week 1: Combining ADC + PWM)
# เวลา: ~20 นาที (Time: ~20 minutes)
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจการอ่าน Analog Input (ADC) และส่งออก Analog-like Output (PWM)
#   2. เข้าใจการ mapping ค่าระหว่างช่วงต่างๆ (0-4095 → 0-1023)
#   3. เตรียมพร้อมสำหรับ: pH sensor (ADC) → pump speed (PWM) ใน Week 3
#
# การเชื่อมโยงกับ Week 3 (Connection to Week 3):
#   - ตัวอย่างนี้: Potentiometer (ADC) → LED brightness (PWM)
#   - Week 3:      pH Sensor (ADC)     → Pump speed (PWM)
#   - หลักการเดียวกัน: อ่านค่า → ประมวลผล → ควบคุม output
#
# ฮาร์ดแวร์ (Hardware):
#   - GPIO32 = Potentiometer (ADC input)
#   - GPIO2  = LED Red (PWM output)
# ==============================================================================

from machine import Pin, ADC, PWM
import time

# นำเข้าขา GPIO (Import GPIO pins)
try:
    from pins import POT1_PIN, LED_RED
except ImportError:
    POT1_PIN = 32    # Potentiometer
    LED_RED = 2      # LED สีแดง

# ปล่อยให้แอป MicroPad สั่งหยุดได้ (allow the MicroPad app to stop this script)
try:
    from scilabpro import stop_requested
except ImportError:
    stop_requested = None

# ==============================================================================
# ค่าคงที่ (Constants)
# ==============================================================================
ADC_MAX = 4095       # 12-bit ADC (0-4095)
PWM_MAX = 1023       # 10-bit PWM (0-1023)
PWM_FREQ = 1000      # ความถี่ PWM (Hz)


# ==============================================================================
# คลาส PotLEDController (Potentiometer-LED Controller Class)
# ==============================================================================
class PotLEDController:
    """
    ควบคุม LED ด้วย Potentiometer (Control LED with Potentiometer)

    หลักการนี้ใช้ใน Week 3:
    - แทน Potentiometer ด้วย pH Sensor
    - แทน LED ด้วย Pump
    - ค่า pH ต่ำ → ปั๊มเร็ว, ค่า pH สูง → ปั๊มช้า

    ตัวอย่างการใช้ (Usage):
        controller = PotLEDController(pot_pin=32, led_pin=2)
        controller.update()  # อ่านค่า pot และปรับ LED
    """

    def __init__(self, pot_pin, led_pin):
        """
        สร้าง Controller (Create Controller)

        Args:
            pot_pin (int): GPIO pin สำหรับ Potentiometer (32)
            led_pin (int): GPIO pin สำหรับ LED (2)
        """
        # ตั้งค่า ADC สำหรับ Potentiometer
        self._adc = ADC(Pin(pot_pin))
        self._adc.atten(ADC.ATTN_11DB)  # ช่วง 0-3.3V

        # ตั้งค่า PWM สำหรับ LED
        self._pwm = PWM(Pin(led_pin))
        self._pwm.freq(PWM_FREQ)
        self._pwm.duty(0)

        self.pot_pin = pot_pin
        self.led_pin = led_pin

        print(f"PotLEDController พร้อมใช้งาน (ready)")
        print(f"  Potentiometer: GPIO{pot_pin} (ADC)")
        print(f"  LED: GPIO{led_pin} (PWM)")

    def read_pot(self):
        """อ่านค่า Potentiometer (Read potentiometer value)"""
        return self._adc.read()

    def map_value(self, value, in_min, in_max, out_min, out_max):
        """
        แปลงค่าจากช่วงหนึ่งไปอีกช่วง (Map value from one range to another)

        ใน Week 3 ใช้แปลง:
        - ADC (0-4095) → Voltage (0-3.3V) → pH (0-14)
        - pH → Pump duty cycle
        """
        return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

    def update(self):
        """
        อ่านค่า Potentiometer และปรับความสว่าง LED
        (Read pot and adjust LED brightness)

        Returns:
            tuple: (adc_value, duty_value, percent)
        """
        # อ่านค่า ADC (0-4095)
        adc_value = self.read_pot()

        # แปลงเป็น duty cycle (0-1023)
        duty_value = self.map_value(adc_value, 0, ADC_MAX, 0, PWM_MAX)

        # ตั้งค่า PWM
        self._pwm.duty(duty_value)

        # คำนวณเปอร์เซ็นต์
        percent = (duty_value / PWM_MAX) * 100

        return adc_value, duty_value, percent

    def deinit(self):
        """คืนทรัพยากร (Release resources)"""
        self._pwm.duty(0)
        self._pwm.deinit()


# ==============================================================================
# โปรแกรมหลัก (Main Program)
# ==============================================================================
if __name__ == "__main__":
    print("=" * 50)
    print("Potentiometer -> LED Dimming")
    print("ควบคุมความสว่าง LED ด้วย Potentiometer")
    print("=" * 50)
    print()
    print("การเชื่อมโยงกับ Week 3:")
    print("  Pot (ADC)  -> LED (PWM)     [ตัวอย่างนี้]")
    print("  pH (ADC)   -> Pump (PWM)    [Week 3]")
    print()
    print("หมุน Potentiometer เพื่อปรับความสว่าง LED")
    print("กด Ctrl+C เพื่อหยุด")
    print("-" * 50)

    # สร้าง Controller
    controller = PotLEDController(POT1_PIN, LED_RED)

    try:
        count = 0
        while True:
            # ตรวจคำสั่งหยุดจากแอป (check for an app stop request)
            if stop_requested is not None and stop_requested():
                print("\nได้รับคำสั่งหยุดจากแอป (Stop requested by app)")
                break

            count += 1
            adc, duty, percent = controller.update()

            # แสดงผลแบบ progress bar
            bar_len = int(percent / 5)  # 20 ช่อง = 100%
            bar = "#" * bar_len + "-" * (20 - bar_len)

            print(f"[{count:3d}] ADC:{adc:4d} -> PWM:{duty:4d} [{bar}] {percent:5.1f}%")
            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\n\nหยุดโปรแกรม (Program stopped)")

    finally:
        controller.deinit()
        print()
        print("=" * 50)
        print("สรุป (Summary):")
        print("-" * 50)
        print("  1. ADC อ่านค่า 0-4095 จาก Potentiometer")
        print("  2. Map ค่า ADC → PWM duty (0-1023)")
        print("  3. PWM ควบคุมความสว่าง LED")
        print()
        print("  Week 3: pH Sensor → Pump Speed")
        print("  หลักการเดียวกัน!")
        print("=" * 50)
