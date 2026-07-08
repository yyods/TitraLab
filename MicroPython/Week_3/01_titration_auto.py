# ==============================================================================
# 01_titration_auto.py - บทเรียนไทเทรชันกรด-เบสอัตโนมัติ (Acid-Base Titration)
# ==============================================================================
# รันไฟล์นี้จากแอป MicroPad (ปุ่ม Run) หรือ Thonny — แท็บเล็ตแสดงกราฟเต็ม
# ส่วนจอ TFT บนบอร์ดแสดงสถานะสด (pH / ปริมาตร / แถบความคืบหน้า / ผลลัพธ์)
# Run from the MicroPad app (Run button) or Thonny. The tablet shows the full
# curve; the on-board TFT shows a live dashboard (pH, volume, progress, result).
#
# *** ห้ามตั้งชื่อ/คัดลอกไฟล์นี้เป็น /workspace/main.py ***
# *** เฟิร์มแวร์รัน main.py อัตโนมัติทุกครั้งที่บูต — บทเรียนที่บล็อกยาว
#     จะทำให้บอร์ดค้าง/เหมือนรีบูตวนไม่หยุด และปั๊มอาจทำงานโดยไม่มีคนดูแล ***
# *** NEVER name/copy this file to /workspace/main.py: the firmware auto-runs
#     main.py at EVERY boot — a long-blocking lesson makes the board appear to
#     reboot forever, and the pump could start unattended. ***
#
# โครงสร้างบทเรียน (Lesson structure — all hardware via scilabpro helpers):
#   1. โหลดผลสอบเทียบที่นิสิตทำเองใน Week_2 (pH slope/intercept + flow rate)
#      ถ้าไฟล์หาย -> แจ้ง event แล้วหยุด (บอกให้นิสิตไปสอบเทียบ Week_2 ก่อน)
#   2. เริ่มแบบ local (ถ้าต้องการ): รอกดปุ่ม BUTTON_1 บนบอร์ด หรือเริ่มทันที
#   3. อ่าน pH (ADC ดิบ + สมการสอบเทียบของนิสิต) และอุณหภูมิ (slp.ds18b20)
#   4. วนหยดไทแทรนต์ทีละ step ด้วย slp.set_actuator('CONTROL_1', ...) + ปิดทุกครั้ง
#      เวลาเปิดปั๊มต่อ step = DOSE_VOLUME_ML / flow_rate (closed-loop บนปริมาตร)
#   5. สตรีมทุกค่าไปแอปด้วย slp.data(...) และตรวจ slp.stop_requested() ทุกลูป
#   6. หาจุดสมมูล + คำนวณความเข้มข้น แล้วส่งผลด้วย slp.event('titration_complete')
#
# สำคัญด้านความปลอดภัย (Safety):
#   ปั๊มถูกเปิดด้วย max_on_ms เสมอ — ฮาร์ดแวร์ไทเมอร์ของเฟิร์มแวร์จะตัดปั๊มเอง
#   แม้สคริปต์จะค้าง และเราปิดปั๊มอย่างชัดเจน (explicit OFF) ในทุกเส้นทางออก
#   The pump is always armed with max_on_ms; the firmware hardware timer cuts it
#   even if the script hangs. We ALSO turn it OFF explicitly on every exit path.
# ==============================================================================

import time

import scilabpro as slp

import experiment as exp
from titration import (
    TitrationAnalysis,
    read_ph_median,
    load_ph_calibration,
    load_burst_deficit,
    load_flow_rate,
    pump_time_ms_for_volume,
)

# ==============================================================================
# จอ TFT (optional): ใช้แพตเทิร์นเดียวกับ Week_2 — release_tft() ก่อน SPI(1,...)
# TFT display (optional): the proven Week_2 pattern — release_tft() before SPI.
# ถ้าไม่มีจอ/ไดรเวอร์ บทเรียนยังทำงานได้ครบ (headless-safe)
# ==============================================================================
try:
    from machine import Pin, SPI
    from ili9341 import Display, color565
    from xglcd_font import XglcdFont
    _HAS_TFT = True
except ImportError:
    _HAS_TFT = False


class TitrationUI:
    """จอแสดงสถานะไทเทรชันบน TFT (320x240) — ทุกเมธอดกันพลาด (never raises).

    On-board titration dashboard. Every method is defensive: a display
    problem must never stop the chemistry. Thai goes to the Console (the
    18x24 font is Latin-only); the TFT shows the live numbers big.
    """

    # สี (colors)
    C_TITLE = None   # set in __init__ (needs color565)
    
    def __init__(self):
        self.ok = False
        if not _HAS_TFT:
            return
        try:
            slp.release_tft()          # ปลดจอจากเฟิร์มแวร์ก่อน (yield the TFT)
            spi = SPI(1, baudrate=40000000, sck=Pin(14), mosi=Pin(13))
            self.d = Display(spi, dc=Pin(27), cs=Pin(15), rst=Pin(0),
                             width=320, height=240, rotation=90)
            import gc
            gc.collect()               # ฟอนต์เสิร์ฟจากแฟลช (frozen fast-path)
            self.f = XglcdFont('fonts/EspressoDolce18x24.c', 18, 24)
            self.white = color565(255, 255, 255)
            self.cyan = color565(0, 255, 255)
            self.green = color565(80, 255, 80)
            self.yellow = color565(255, 210, 40)
            self.orange = color565(255, 140, 0)
            self.red = color565(255, 70, 70)
            self.grey = color565(90, 90, 90)
            self._status = ""
            self.ok = True
        except Exception as e:
            print("TFT off (headless):", e)

    def _text(self, x, y, msg, color):
        try:
            self.d.draw_text(x, y, msg, self.f, color, background=0)
        except Exception:
            pass

    def _frame(self, title, color):
        """ล้างจอ + หัวเรื่อง (clear + title bar)."""
        try:
            self.d.clear(hlines=2)
            self._text(10, 6, title, color)
            self.d.draw_hline(10, 36, 300, self.grey)
        except Exception:
            pass

    def splash(self, slope, intercept, flow):
        """หน้าเปิด: โชว์ว่ากำลังใช้ค่าสอบเทียบของบอร์ดตัวนี้ (นิสิตทำเอง!)."""
        if not self.ok:
            return
        self._frame("AUTO TITRATION", self.cyan)
        self._text(10, 50, "Your calibration:", self.white)
        self._text(10, 82, "pH m=%.5f" % slope, self.green)
        self._text(10, 112, "   b=%.2f" % intercept, self.green)
        self._text(10, 144, "flow=%.4f mL/s" % flow, self.green)
        self._text(10, 200, "MicroPad connected", self.grey)

    def prompt_start(self, timeout_s):
        if not self.ok:
            return
        self._frame("READY", self.green)
        self._text(10, 70, "PRESS BUTTON 1", self.yellow)
        self._text(10, 102, "TO START", self.yellow)
        self._text(10, 160, "(auto-cancel %ds)" % timeout_s, self.grey)

    def live_init(self, total_steps):
        if not self.ok:
            return
        self._frame("TITRATING...", self.cyan)
        self._text(10, 46, "pH", self.grey)
        self._text(10, 112, "Vol", self.grey)
        self._text(170, 112, "T", self.grey)
        try:  # กรอบแถบความคืบหน้า (progress bar frame)
            self.d.draw_rectangle(10, 168, 300, 22, self.grey)
        except Exception:
            pass

    def live(self, ph, volume, temp, step, total_steps, status):
        """อัปเดตตัวเลขสด — เขียนทับที่เดิม (draw over, background=black)."""
        if not self.ok:
            return
        self._text(70, 46, "%.2f  " % ph, self.white)
        self._text(80, 112, "%.1fmL " % volume, self.white)
        self._text(205, 112, "%.1fC " % temp, self.white)
        try:  # แถบความคืบหน้า (เติมทีละส่วน — ผ่าน cap ของไดรเวอร์)
            w = int(296 * step / total_steps)
            if w > 0:
                self.d.fill_rectangle(12, 170, w, 18, self.green)
        except Exception:
            pass
        if status != self._status:
            self._status = status
            self._text(10, 205, "%-14s" % status, self.yellow)

    def alert(self):
        if not self.ok:
            return
        self._text(10, 205, "NEAR EQUIV.PT!", self.orange)

    def results(self, eq_vol, conc):
        if not self.ok:
            return
        self._frame("COMPLETE!", self.green)
        if eq_vol is not None:
            self._text(10, 60, "Eq.pt %.2f mL" % eq_vol, self.white)
        else:
            self._text(10, 60, "Eq.pt not found", self.yellow)
        if conc is not None:
            self._text(10, 100, "Conc.", self.grey)
            self._text(10, 132, "%.4f M" % conc, self.cyan)
        self._text(10, 200, "See app for graph", self.grey)

    def aborted(self, why):
        if not self.ok:
            return
        self._frame("STOPPED", self.red)
        self._text(10, 70, why, self.white)
        self._text(10, 200, "Safe: pump OFF", self.green)

# ==============================================================================
# ขา GPIO สำหรับอุปกรณ์ที่ slp helper ต้องระบุเลขขา (titralab_v1_default)
# GPIO numbers for helpers that take a pin (firmware owns the routing profile)
# ==============================================================================
GREEN_LED_PIN = 4    # GREEN LED (output) — แสดงสถานะ "กำลังทำงาน"
BUTTON_1_PIN = 34    # BUTTON_1 (input-only) — ปุ่มเริ่มแบบ local
BUZZER_PIN = 26      # BUZZER (PWM output) — เสียงแจ้งเตือน/เสร็จสิ้น

# ตั้ง True เพื่อให้รอกดปุ่ม BUTTON_1 บนบอร์ดก่อนเริ่ม (local start)
# ตั้ง False เพื่อเริ่มทันทีเมื่อแอปสั่งรัน (app-driven start)
WAIT_FOR_LOCAL_START = True

# ==============================================================================
# ปิดเสียงบัซเซอร์ทันทีที่ไฟล์เริ่มรัน (import-time silence)
# ==============================================================================
# PWM ของ ESP32 "ทำงานต่อ" ข้ามการจบสคริปต์/soft-reset ได้ — ถ้ารอบก่อนถูกสั่งหยุด
# กลางเสียงบี๊บ เสียงจะดังค้างมาจนถึงรอบนี้ บรรทัดนี้ดับเสียงเป็นสิ่งแรกสุด
# ESP32 PWM keeps running across script end / soft reset: a previous run
# stopped mid-beep leaves the buzzer screaming into this run. Kill it FIRST,
# before anything slow (claim, calibration load, display init).
slp.buzzer(BUZZER_PIN).off()


def wait_for_button(button, timeout_ms=30000):
    """
    รอกดปุ่มเริ่ม BUTTON_1 (Wait for BUTTON_1 press, polling cooperative-stop)

    Args:
        button: ออบเจ็กต์ slp.pin(BUTTON_1_PIN, input=True)
        timeout_ms: เวลารอสูงสุด (ms) ก่อนเริ่มอัตโนมัติ

    Returns:
        bool: True ถ้ากดปุ่ม, False ถ้าหมดเวลา (ไม่เริ่มเองเพื่อความปลอดภัย)
              หรือมีคำสั่งหยุดจากแอป (no unattended auto-start)
    """
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < timeout_ms:
        # ตรวจคำสั่งหยุดจากแอปทุกลูป (poll cooperative stop every loop)
        if slp.stop_requested():
            return False
        # ปุ่ม input-only ทำงานแบบ active-high (มี pull-down บนบอร์ด)
        if button.value():
            return True
        time.sleep_ms(50)
    # หมดเวลา: ยกเลิก — บทเรียนที่ควบคุมปั๊มต้องมีคนยืนยันก่อนเริ่มเสมอ
    # Timeout → ABORT: an actuator lesson must never start unattended.
    return False


def dose_one_step(led, pump_time_ms):
    """
    หยดไทแทรนต์ 1 step อย่างปลอดภัย (Dose one titrant step, guarded)

    เวลาเปิดปั๊ม (pump_time_ms) คำนวณจากอัตราการไหลที่นิสิตสอบเทียบเอง (closed-loop
    บนปริมาตร) — ไม่ใช่ค่าคงที่ตายตัว ดังนั้นปริมาตรที่จ่ายจึงตรงกับ DOSE_VOLUME_ML จริง
    The on-time is derived from the student's calibrated flow rate (closed-loop on
    volume), NOT a hard-coded constant, so the delivered volume matches DOSE_VOLUME_ML.

    เปิดปั๊มด้วย max_on_ms เพื่อให้ฮาร์ดแวร์ไทเมอร์ตัดเองหากสคริปต์ค้าง จากนั้นรอ
    ตามเวลาที่คำนวณ แล้ว "ปิดปั๊มอย่างชัดเจน" เสมอใน finally
    Arms the pump with max_on_ms (hardware-timer safety) and ALWAYS turns it
    off explicitly afterwards, even if an error occurs.

    Args:
        led: ออบเจ็กต์ LED สถานะ หรือ None — ดับชั่วขณะระหว่างหยด แล้วกลับติดค้าง
             (status LED; OFF-blink during the dose, back to steady after)
        pump_time_ms: เวลาเปิดปั๊มที่คำนวณจาก flow_rate แล้ว clamp (computed on-time, ms)
    """
    # ไฟเขียว: ติดค้าง = การทดลองกำลังดำเนิน; "ดับชั่วขณะ" ระหว่างหยด =
    # จังหวะการหยดมองเห็นได้ (LED steady = running; OFF-blink marks each dose)
    if led is not None:
        led.value(0)
    try:
        # เปิดปั๊ม — max_on_ms คือเพดานความปลอดภัยจากเฟิร์มแวร์ (hardware guard)
        slp.set_actuator(exp.PUMP_ENDPOINT, True, max_on_ms=exp.DOSE_MAX_ON_MS)
        time.sleep_ms(pump_time_ms)
    finally:
        # ปิดปั๊มอย่างชัดเจนทุกเส้นทาง (explicit OFF on every path)
        slp.set_actuator(exp.PUMP_ENDPOINT, False)
        if led is not None:
            led.value(1)  # กลับสู่ติดค้าง = ยังทำงานอยู่ (back to steady running)


def save_titration_csv(rows, eq, unknown_c, completed):
    """บันทึกข้อมูลไทเทรชันเป็น .csv ใน /workspace/data (เลขรันอัตโนมัติ R1, R2, ...)

    Save the titration data as a CSV under /workspace/data with an
    auto-incrementing run number. Returns the path (or None on failure).
    นิสิตดาวน์โหลดไฟล์นี้จากแอปไปทำรายงาน/พล็อตต่อได้ (open/plot in the app).
    """
    import os
    data_dir = '/workspace/data'
    try:
        try:
            os.mkdir(data_dir)
        except OSError:
            pass  # มีอยู่แล้ว (already exists)
        # หาเลขรันถัดไป (find the next free run number)
        n = 1
        existing = os.listdir(data_dir)
        while ('titration_data_R%d.csv' % n) in existing:
            n += 1
        path = data_dir + '/titration_data_R%d.csv' % n
        with open(path, 'w') as f:
            f.write('# TitraLab Automatic Titration Data (Week_3)\n')
            f.write('# sample_volume_ml=%s\n' % exp.SAMPLE_VOLUME_ML)
            f.write('# titrant_concentration_m=%s\n' % exp.TITRANT_CONCENTRATION_M)
            f.write('# dose_volume_ml=%s\n' % exp.DOSE_VOLUME_ML)
            f.write('# completed=%s\n' % ('yes' if completed else 'stopped_early'))
            if eq:
                f.write('# equivalence_volume_ml=%.3f\n' % eq[0])
                f.write('# equivalence_ph_estimate=%.3f\n' % eq[1])
            if unknown_c is not None:
                f.write('# unknown_concentration_m=%.5f\n' % unknown_c)
            f.write('volume_ml,pH,temp_c\n')
            for v, ph, t in rows:
                f.write('%.3f,%.3f,%.2f\n' % (v, ph, t))
        return path
    except Exception as e:
        # การบันทึกล้มเหลวต้องไม่ทำให้บทเรียนพัง (saving must never break the lesson)
        print('บันทึก CSV ไม่สำเร็จ (CSV save failed):', e)
        return None


def run_titration():
    """
    ดำเนินการไทเทรชันอัตโนมัติแบบครบขั้นตอน (Run the full titration procedure)

    Returns:
        dict: สรุปผล (จำนวน step, ปริมาตรรวม, จุดสมมูล, ความเข้มข้นที่คำนวณได้)
    """
    # อ้างสิทธิ์ควบคุม (กรณีรันผ่าน USB ขณะแอปเชื่อมต่ออยู่)
    # Claim the controller lease (needed if launched from USB while a tablet is on).
    # ถ้าแท็บเล็ตถืออำนาจควบคุมอยู่ จะได้ OSError (-269 = อีกฝั่งถือ lease อยู่)
    # -> อธิบายและจบอย่างสะอาด แทนที่จะล้มด้วย traceback
    try:
        slp.claim_controller()
    except OSError:
        print("ควบคุมบอร์ดไม่ได้: แอป MicroPad กำลังถืออำนาจควบคุมอยู่")
        print("ปิดแอป (หรือกด Disconnect) แล้วรันใหม่ หรือสั่งรันจากแอปแทน")
        print("Cannot take control: the MicroPad app currently holds the")
        print("controller lease. Close/disconnect the app and re-run, or")
        print("launch this lesson from the app instead.")
        return {'aborted': True, 'reason': 'controller_lease_busy'}

    # =========================================================================
    # โหลดผลสอบเทียบที่นิสิตทำเองใน Week_2 (Load student-performed Week_2 calibration)
    # =========================================================================
    # *** หัวใจของบทเรียน: ใช้ค่าสอบเทียบของบอร์ดตัวเอง ไม่ใช่ค่าคงที่ตายตัว ***
    # ถ้าไฟล์หาย/อ่านไม่ได้ -> แจ้ง event แล้วหยุดอย่างสะอาด ก่อนแตะ actuator ใด ๆ
    # If a calibration file is missing -> emit an event and abort BEFORE any dosing.
    try:
        # สมการ pH ของนิสิต: pH = slope_m * mV + intercept_b (จาก Week_2)
        ph_slope_m, ph_intercept_b = load_ph_calibration()
    except RuntimeError as e:
        # ยังไม่ได้สอบเทียบ pH — บอกให้นิสิตไปรัน Week_2 pH calibration ก่อน
        slp.event('ph_calibration_missing', {
            'path': exp.PH_CAL_PATH,
            'error': str(e),
            'hint': 'Run Week_2 01_pH_Sensor/02_calibration_3point.py first',
        })
        return {'aborted': True, 'reason': 'ph_calibration_missing'}

    try:
        # อัตราการไหลของนิสิต (mL/s) จาก Week_2 flow calibration
        flow_rate_ml_s = load_flow_rate()
    except RuntimeError as e:
        # ยังไม่ได้สอบเทียบ flow — บอกให้นิสิตไปรัน Week_2 flow calibration ก่อน
        slp.event('flow_calibration_missing', {
            'path': exp.FLOW_CAL_PATH,
            'error': str(e),
            'hint': 'Run Week_2 02_Pump_Control/01_flow_rate_calibration.py first',
        })
        return {'aborted': True, 'reason': 'flow_calibration_missing'}

    # ชดเชย stop-flow (ถ้าสอบเทียบขั้นที่ 2 แล้ว): ทุกการสตาร์ทปั๊มมีช่วงเสียเปล่า
    # (มอเตอร์หมุนขึ้น + soft-start) — Week_2 04_flow_stepwise_finetune.py วัดค่านี้
    # ไว้เป็น burst_deficit_ml; ไม่มี -> 0.0 (โมเดลเดิม)
    burst_deficit_ml = load_burst_deficit()

    # เวลาเปิดปั๊มต่อ 1 step คำนวณจากอัตราการไหลที่สอบเทียบ (closed-loop on volume)
    # + ชดเชยช่วงเสียเปล่าต่อหยด; clamp ด้วย DOSE_MAX_ON_MS เพื่อความปลอดภัย
    pump_time_ms = pump_time_ms_for_volume(
        exp.DOSE_VOLUME_ML, flow_rate_ml_s, exp.DOSE_MAX_ON_MS,
        burst_deficit_ml=burst_deficit_ml)

    # ปริมาตรที่ "ส่งจริง" ต่อ step จากเวลาปั๊มจริง (delivered volume per step).
    # ปกติ = DOSE_VOLUME_ML แต่ถ้าเวลาปั๊มถูก clamp ที่เพดานความปลอดภัย
    # (ปั๊มช้า/flow ต่ำ) ปริมาตรจริงจะน้อยกว่า — ต้องนับตามจริง ไม่งั้นแกนปริมาตร
    # ของกราฟทั้งเส้นคลาดโดยไม่มีใครรู้ (silent under-dosing skews the volume axis)
    dose_ml_actual = flow_rate_ml_s * (pump_time_ms / 1000.0) - burst_deficit_ml
    if dose_ml_actual < 0:
        dose_ml_actual = 0.0
    if pump_time_ms >= exp.DOSE_MAX_ON_MS and dose_ml_actual < exp.DOSE_VOLUME_ML * 0.99:
        print("!" * 56)
        print(f"คำเตือน: ปั๊มช้า — เวลาเปิดถูกจำกัดที่ {exp.DOSE_MAX_ON_MS} ms")
        print(f"แต่ละหยดจ่ายจริง ~{dose_ml_actual:.3f} mL (ไม่ใช่ {exp.DOSE_VOLUME_ML} mL)")
        print("WARNING: slow pump — dose clamped at the safety ceiling;")
        print(f"each step delivers ~{dose_ml_actual:.3f} mL. Volumes use the ACTUAL value.")
        print("!" * 56)
        slp.event('dose_clamped', {
            'dose_ml_actual': dose_ml_actual,
            'dose_ml_target': exp.DOSE_VOLUME_ML,
            'pump_time_ms': pump_time_ms,
        })

    # แจ้งให้แอปทราบว่ากำลังใช้ค่าสอบเทียบของบอร์ดตัวนี้ (calibration in use — visible)
    slp.event('calibration_loaded', {
        'ph_slope_m': ph_slope_m,
        'ph_intercept_b': ph_intercept_b,
        'flow_rate_ml_s': flow_rate_ml_s,
        'burst_deficit_ml': burst_deficit_ml,
        'pump_time_ms': pump_time_ms,
        'dose_volume_ml': exp.DOSE_VOLUME_ML,
    })

    # --- คอนโซล: สรุปค่าสอบเทียบของ "บอร์ดตัวนี้" ให้นิสิตเห็นชัด ๆ ---
    print("=" * 56)
    print("ไทเทรชันอัตโนมัติ (Automatic Acid-Base Titration)")
    print("=" * 56)
    print("ค่าสอบเทียบของบอร์ดนี้ (This board's calibration):")
    print(f"  pH:   pH = {ph_slope_m:.6f} x mV + {ph_intercept_b:.4f}")
    print(f"  Flow: {flow_rate_ml_s:.4f} mL/s  "
          f"(pump {pump_time_ms} ms/step = {exp.DOSE_VOLUME_ML} mL)")
    if burst_deficit_ml > 0:
        print(f"  Stop-flow: ชดเชย {burst_deficit_ml * 1000:.1f} uL/หยด "
              f"(จาก Week_2 04_flow_stepwise_finetune)")
    else:
        print("  Stop-flow: ยังไม่ปรับละเอียด — แนะนำรัน Week_2")
        print("  04_flow_stepwise_finetune.py เพื่อความแม่นของปริมาตร")
    print("-" * 56)

    # สร้างออบเจ็กต์ helper จากเฟิร์มแวร์ (Create firmware helper objects)
    # หมายเหตุ: ไม่ใช้ slp.ph_probe() — อ่าน ADC ดิบแล้วใช้สมการสอบเทียบของนิสิตเอง
    # Note: NO slp.ph_probe(); we read RAW ADC and apply the student's fit ourselves.
    led = slp.pin(GREEN_LED_PIN)                # ไฟแสดงสถานะ (output)
    led.value(0)
    ui = TitrationUI()                          # จอ TFT (headless-safe)
    ui.splash(ph_slope_m, ph_intercept_b, flow_rate_ml_s)
    buzzer = slp.buzzer(BUZZER_PIN)             # เสียงแจ้งเตือน
    # ESP32 PWM เริ่มทำงานทันทีที่สร้าง (duty ~50%) -> ปิดเสียงทันที ไม่งั้นบี๊บยาว
    # ESP32 PWM starts AUDIBLE on construction (~50% duty) -> silence immediately
    buzzer.off()
    button = slp.pin(BUTTON_1_PIN, input=True)  # ปุ่มเริ่ม local (input-only)

    analysis = TitrationAnalysis()

    # จำนวน step ทั้งหมด คำนวณจากปริมาตรสูงสุด / ปริมาตรต่อ step
    # ใช้ +0.5 ก่อน int() (ปัดเศษ) เพราะการหาร float อาจได้ 49.999.. หรือ
    # 23.999.. ทำให้ int() ตัดเป็นค่าต่ำผิด 1 step (เตือน/หยุดเร็วไป 0.2 mL)
    # Round (not truncate): float division can yield 49.999.. / 23.999.., and
    # bare int() would drop a whole step (alerting / stopping 0.2 mL early).
    total_steps = int(exp.MAX_VOLUME_ML / exp.DOSE_VOLUME_ML + 0.5)
    alert_step = int(exp.ALERT_VOLUME_ML / exp.DOSE_VOLUME_ML + 0.5)

    slp.event('titration_started', {
        'sample_volume_ml': exp.SAMPLE_VOLUME_ML,
        'titrant_conc_m': exp.TITRANT_CONCENTRATION_M,
        'dose_volume_ml': exp.DOSE_VOLUME_ML,
        'total_steps': total_steps,
    })

    # --- เริ่มแบบ local: รอกดปุ่ม BUTTON_1 (optional local start) ---
    if WAIT_FOR_LOCAL_START:
        slp.event('waiting_for_start', {'button': 'BUTTON_1'})
        print()
        print("ตรวจสอบก่อนเริ่ม: ต่อแบตเตอรี่แล้วหรือยัง? (ปั๊มใช้ไฟจากแบตเตอรี่)")
        print("PRE-FLIGHT: battery connected? The pump draws from the battery —")
        print("on USB power alone the board browns out and reboots at the first dose.")
        print(">>> กดปุ่ม 1 (BUTTON_1) บนบอร์ดเพื่อเริ่มไทเทรชัน <<<")
        print(">>> Press BUTTON 1 on the board to START <<<")
        print("(ยกเลิกอัตโนมัติใน 30 วินาทีถ้าไม่กด / auto-cancel in 30 s)")
        ui.prompt_start(30)
        if not wait_for_button(button):
            # หยุดจากแอป หรือหมดเวลารอโดยไม่มีการยืนยัน (ไม่เริ่มเอง)
            print("ยกเลิก: ไม่มีการยืนยันเริ่ม (No start confirmation — cancelled)")
            ui.aborted("No start press")
            slp.event('titration_aborted',
                      {'reason': 'no_start_confirmation_or_stop'})
            return {'aborted': True, 'reason': 'no_start_confirmation_or_stop'}

    # ไฟเขียวติดค้าง = การทดลองกำลังดำเนิน (green steady = experiment running)
    led.value(1)
    print()
    print("เริ่มไทเทรชัน! (Titration started)")
    print(f"หยดครั้งละ {exp.DOSE_VOLUME_ML} mL สูงสุด {exp.MAX_VOLUME_ML} mL "
          f"(step ละ ~{(exp.SETTLE_MS // 1000) + 1} วินาที)")
    print("-" * 56)
    ui.live_init(total_steps)

    def read_temp_c():
        """อ่านอุณหภูมิอย่างปลอดภัย (Read temperature; default 25 C on error)."""
        try:
            return slp.ds18b20(exp.TEMP_PROBE_PIN).read_c()
        except OSError as e:
            # ไม่พบเซ็นเซอร์อุณหภูมิ — แจ้งเตือนแล้วใช้ค่าเริ่มต้น
            slp.event('temp_sensor_warning', {'error': str(e), 'default_c': 25.0})
            return 25.0

    aborted = False

    def read_ph_safe():
        """
        อ่าน pH แบบมัธยฐาน โดยใช้สมการสอบเทียบของนิสิตที่โหลดไว้แล้ว
        Median pH read, APPLYING the student's pre-loaded Week_2 calibration fit.

        การสอบเทียบถูกโหลด (และตรวจว่ามีอยู่) ตั้งแต่ต้นฟังก์ชัน run_titration()
        แล้ว ดังนั้นการอ่านตรงนี้จึงเพียงอ่าน ADC ดิบ -> mV -> ใช้สมการของนิสิต
        Calibration was already loaded (and verified present) at the top of
        run_titration(), so this just reads RAW ADC -> mV -> applies the fit.

        Returns:
            float: ค่า pH มัธยฐาน ในช่วง 0..14 (median student-calibrated pH)
        """
        return read_ph_median(ph_slope_m, ph_intercept_b,
                              exp.PH_SAMPLES_PER_POINT, exp.PH_SAMPLE_GAP_MS)

    try:
        # --- จุดเริ่มต้น (Step 0): อ่านค่าที่ปริมาตร 0 mL ---
        volume = 0.0
        csv_rows = []                    # (volume, pH, temp) ทุกจุดสำหรับไฟล์ .csv
        # --- จุดฐาน (baseline): อ่าน pH เริ่มต้นที่ 0.0 mL ก่อนหยดไทแทรนต์ใด ๆ ---
        # กราฟไทเทรชันทุกเส้นต้องมีจุดเริ่มต้น — ช่วงนี้ "ยังไม่หยด" โดยตั้งใจ
        print("กำลังอ่านค่าเริ่มต้นที่ 0.0 mL (ยังไม่หยดไทแทรนต์)...")
        print("Reading the 0.0 mL baseline (no titrant yet)...")
        ui.live(0.0, 0.0, 0.0, 0, total_steps, "Baseline")
        ph0 = read_ph_safe()
        temp0 = read_temp_c()
        analysis.add_point(volume, ph0)
        csv_rows.append((volume, ph0, temp0))
        ph, temp = ph0, temp0   # ค่าล่าสุดสำหรับจอ TFT ระหว่างรอผลอ่านใหม่
        slp.data('volume_ml', volume, unit=exp.UNIT_VOLUME_ML)
        slp.data('pH', ph0, unit=exp.UNIT_PH)
        slp.data('temp_c', temp0, unit=exp.UNIT_TEMP_C)

        # รอให้ pH เริ่มต้นคงที่ก่อนหยดแรก (settle before first dose)
        if not _settle(exp.SETTLE_MS):
            aborted = True

        alerted = False
        step = 0
        # --- ลูปไทเทรชันหลัก (Main titration loop) ---
        # ตรวจ slp.stop_requested() ทุกลูป + มีขอบเขต step ชัดเจน (ไม่ใช่ while True)
        while not aborted and step < total_steps:
            step += 1

            # หยดไทแทรนต์ 1 step (guarded; pump OFF guaranteed inside)
            # pump_time_ms มาจากอัตราการไหลที่สอบเทียบ -> ปริมาตรที่จ่ายตรงจริง
            dose_one_step(led, pump_time_ms)

            # คำนวณปริมาตรจากจำนวน step เพื่อเลี่ยง floating-point drift
            # ใช้ปริมาตร "ส่งจริง" ต่อ step (delivered per-step volume)
            volume = step * dose_ml_actual

            # --- รายงานปริมาตรทันทีที่หยดเสร็จ (report volume AT DOSE TIME) ---
            # ปริมาตรรู้แน่นอนตั้งแต่หยดจบ ไม่ต้องรอ settle 10 วินาที — ไม่งั้น
            # หยดแรกจะยังโชว์ 0.0 mL ค้างจนอ่าน pH เสร็จ (the first drop showed
            # a stale 0.0 mL for ~11 s because volume streamed only post-read)
            slp.data('volume_ml', volume, unit=exp.UNIT_VOLUME_ML)
            print(f"หยดที่ {step:2d}: ปริมาตรรวม {volume:5.2f} mL "
                  f"(รอค่า pH นิ่ง {exp.SETTLE_MS // 1000} วิ...)")
            ui.live(ph, volume, temp, step, total_steps, "Settling")

            # รอให้ pH คงที่ พร้อมตรวจคำสั่งหยุด (settle with stop check)
            if not _settle(exp.SETTLE_MS):
                aborted = True
                break

            # อ่านเซ็นเซอร์ (median pH + temperature) — ใช้สมการสอบเทียบของนิสิต
            ph = read_ph_safe()
            temp = read_temp_c()
            analysis.add_point(volume, ph)
            csv_rows.append((volume, ph, temp))

            # สตรีม pH/อุณหภูมิหลังค่านิ่ง (volume ถูกส่งไปแล้วตอนหยดเสร็จ)
            slp.data('pH', ph, unit=exp.UNIT_PH)
            slp.data('temp_c', temp, unit=exp.UNIT_TEMP_C)

            # คอนโซล + จอ TFT (console line + live TFT update)
            print(f"step {step:2d}/{total_steps}  V={volume:5.2f} mL  "
                  f"pH={ph:5.2f}  T={temp:.1f}C")
            ui.live(ph, volume, temp, step, total_steps, "Reading OK")

            # เตือนใกล้จุดสมมูล (alert when approaching equivalence)
            if not alerted and step >= alert_step:
                alerted = True
                slp.event('approaching_equivalence', {'volume_ml': volume})
                print("*** ใกล้จุดสมมูล! สังเกตสีอินดิเคเตอร์ให้ดี ***")
                print("*** NEAR EQUIVALENCE POINT - watch the indicator! ***")
                ui.alert()
                # บี๊บ 3 ครั้งให้ได้ยินชัดในห้องแล็บ (three clear beeps —
                # a single short chirp is easy to miss over the pump noise)
                for _ in range(3):
                    buzzer.tone(2000)
                    time.sleep_ms(300)
                    buzzer.off()
                    time.sleep_ms(150)

    finally:
        # --- ความปลอดภัย: ปิดปั๊ม/บัซเซอร์/ไฟ เสมอ (cleanup on every path) ---
        slp.set_actuator(exp.PUMP_ENDPOINT, False)
        buzzer.off()
        led.value(0)

    if aborted:
        # การยกเลิกกลางคันที่นี่มาจากผู้ใช้สั่งหยุดเท่านั้น (กรณีสอบเทียบหายถูกจับ
        # และ return ไปแล้วตั้งแต่ต้นฟังก์ชัน ก่อนหยดไทแทรนต์ใด ๆ)
        # Any abort reaching here is a user stop; missing-calibration aborts
        # were caught and returned at the top, before any dosing.
        print("หยุดโดยผู้ใช้ (Stopped by user) — ปั๊มปิดแล้ว (pump OFF)")
        if csv_rows:
            partial_path = save_titration_csv(csv_rows, None, None, completed=False)
            if partial_path:
                print(f"บันทึกข้อมูลที่เก็บได้แล้วที่ (partial data saved): {partial_path}")
        ui.aborted("User stop")
        slp.event('titration_aborted', {
            'reason': 'stop_requested',
            'points_collected': len(analysis.points),
        })
        return {'aborted': True, 'reason': 'stop_requested',
                'points': len(analysis.points)}

    # --- วิเคราะห์ผล (Analyze): จุดสมมูล + ความเข้มข้นที่ไม่ทราบค่า ---
    eq = analysis.detect_equivalence_point()
    unknown_c = analysis.calculate_unknown_concentration(
        titrant_conc_m=exp.TITRANT_CONCENTRATION_M,
        sample_volume_ml=exp.SAMPLE_VOLUME_ML,
        ratio=exp.STOICHIOMETRIC_RATIO,
    )

    result = {
        'total_steps': step,
        'total_volume_ml': volume,
        'equivalence_volume_ml': eq[0] if eq else None,
        # ค่า pH จุดสมมูลเป็นค่าประมาณ (pH เปลี่ยนหลายหน่วยภายใน 1 step)
        # equivalence pH is an ESTIMATE — pH changes several units per step
        'equivalence_ph_estimate': eq[1] if eq else None,
        'max_dph_dv': analysis.max_derivative if eq else None,
        'unknown_concentration_m': unknown_c,
        'titrant_concentration_m': exp.TITRANT_CONCENTRATION_M,
        'sample_volume_ml': exp.SAMPLE_VOLUME_ML,
        # อัตราส่วนสโตอิชิโอเมตรีที่ใช้คำนวณ (stoichiometry assumed in C calc)
        'stoichiometric_ratio': exp.STOICHIOMETRIC_RATIO,
    }

    # --- คอนโซล: สรุปผลให้ชั้นเรียน (console result summary) ---
    print("=" * 56)
    print("ไทเทรชันเสร็จสิ้น! (TITRATION COMPLETE)")
    print("=" * 56)
    if eq:
        print(f"จุดสมมูล (Equivalence point): {eq[0]:.2f} mL  (pH ~{eq[1]:.2f})")
    else:
        print("ไม่พบจุดสมมูลชัดเจน (No clear equivalence point)")
    if unknown_c is not None:
        print(f"ความเข้มข้นสารตัวอย่าง (Unknown conc.): {unknown_c:.4f} M")
    print(f"ปริมาตรรวม (Total volume): {volume:.2f} mL ใน {step} steps")
    csv_path = save_titration_csv(csv_rows, eq, unknown_c, completed=True)
    if csv_path:
        print(f"บันทึกข้อมูลแล้วที่ (data saved): {csv_path}")
        print("เปิด/ดาวน์โหลดได้จากแอปในโฟลเดอร์ data (open it from the app's data folder)")
        result['csv_path'] = csv_path
    print("ดูกราฟบนแอป MicroPad (Full curve on the MicroPad app)")
    print("=" * 56)
    ui.results(eq[0] if eq else None, unknown_c)

    # เสียงเสร็จสิ้น 2 โน้ต (two-note completion chime)
    buzzer.tone(1000)
    time.sleep_ms(250)
    buzzer.tone(1500)
    time.sleep_ms(250)
    buzzer.off()

    # ส่งผลลัพธ์ไปยังแอป (emit the final result event)
    slp.event('titration_complete', result)
    return result


def _settle(duration_ms):
    """
    รอให้ pH คงที่ พร้อมตรวจคำสั่งหยุดเป็นช่วง ๆ
    Wait `duration_ms`, polling cooperative-stop in small slices.

    Returns:
        bool: True ถ้ารอครบ, False ถ้าแอปสั่งหยุด (stop_requested)
    """
    elapsed = 0
    slice_ms = 100
    while elapsed < duration_ms:
        if slp.stop_requested():
            return False
        time.sleep_ms(slice_ms)
        elapsed += slice_ms
    return True


# ==============================================================================
# จุดเริ่มต้น (Entry point) — รันไฟล์นี้จากแอป MicroPad หรือ Thonny
# ==============================================================================
run_titration()
