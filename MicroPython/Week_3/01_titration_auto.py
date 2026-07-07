# ==============================================================================
# 01_titration_auto.py - บทเรียนไทเทรชันกรด-เบสอัตโนมัติ (Acid-Base Titration)
# ==============================================================================
# รันไฟล์นี้จากแอป MicroPad (ปุ่ม Run) หรือ Thonny — แท็บเล็ตเป็นจอแสดงผลหลัก
# Run this file from the MicroPad app (Run button) or Thonny; the tablet is
# the display (no on-board TFT menu).
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
    load_flow_rate,
    pump_time_ms_for_volume,
)

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
        led: ออบเจ็กต์ LED สถานะ หรือ None (status LED object or None)
        pump_time_ms: เวลาเปิดปั๊มที่คำนวณจาก flow_rate แล้ว clamp (computed on-time, ms)
    """
    if led is not None:
        led.value(1)  # ไฟเขียวติด = กำลังหยด (green on = dosing)
    try:
        # เปิดปั๊ม — max_on_ms คือเพดานความปลอดภัยจากเฟิร์มแวร์ (hardware guard)
        slp.set_actuator(exp.PUMP_ENDPOINT, True, max_on_ms=exp.DOSE_MAX_ON_MS)
        time.sleep_ms(pump_time_ms)
    finally:
        # ปิดปั๊มอย่างชัดเจนทุกเส้นทาง (explicit OFF on every path)
        slp.set_actuator(exp.PUMP_ENDPOINT, False)
        if led is not None:
            led.value(0)


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

    # เวลาเปิดปั๊มต่อ 1 step คำนวณจากอัตราการไหลที่สอบเทียบ (closed-loop on volume)
    # clamp ด้วย DOSE_MAX_ON_MS เพื่อความปลอดภัย (computed + clamped pump-on time)
    pump_time_ms = pump_time_ms_for_volume(
        exp.DOSE_VOLUME_ML, flow_rate_ml_s, exp.DOSE_MAX_ON_MS)

    # แจ้งให้แอปทราบว่ากำลังใช้ค่าสอบเทียบของบอร์ดตัวนี้ (calibration in use — visible)
    slp.event('calibration_loaded', {
        'ph_slope_m': ph_slope_m,
        'ph_intercept_b': ph_intercept_b,
        'flow_rate_ml_s': flow_rate_ml_s,
        'pump_time_ms': pump_time_ms,
        'dose_volume_ml': exp.DOSE_VOLUME_ML,
    })

    # สร้างออบเจ็กต์ helper จากเฟิร์มแวร์ (Create firmware helper objects)
    # หมายเหตุ: ไม่ใช้ slp.ph_probe() — อ่าน ADC ดิบแล้วใช้สมการสอบเทียบของนิสิตเอง
    # Note: NO slp.ph_probe(); we read RAW ADC and apply the student's fit ourselves.
    led = slp.pin(GREEN_LED_PIN)                # ไฟแสดงสถานะ (output)
    led.value(0)
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
        if not wait_for_button(button):
            # หยุดจากแอป หรือหมดเวลารอโดยไม่มีการยืนยัน (ไม่เริ่มเอง)
            slp.event('titration_aborted',
                      {'reason': 'no_start_confirmation_or_stop'})
            return {'aborted': True, 'reason': 'no_start_confirmation_or_stop'}

    # ไฟเขียวติดค้าง = การทดลองกำลังดำเนิน (green steady = experiment running)
    led.value(1)

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
        ph0 = read_ph_safe()
        temp0 = read_temp_c()
        analysis.add_point(volume, ph0)
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
            # ปริมาตรนี้ "ส่งจริง" เพราะ pump_time_ms คำนวณจาก flow_rate ของบอร์ดนี้
            volume = step * exp.DOSE_VOLUME_ML

            # รอให้ pH คงที่ พร้อมตรวจคำสั่งหยุด (settle with stop check)
            if not _settle(exp.SETTLE_MS):
                aborted = True
                break

            # อ่านเซ็นเซอร์ (median pH + temperature) — ใช้สมการสอบเทียบของนิสิต
            ph = read_ph_safe()
            temp = read_temp_c()
            analysis.add_point(volume, ph)

            # สตรีมทุกค่าไปยังแอป MicroPad (stream every reading to the app)
            slp.data('volume_ml', volume, unit=exp.UNIT_VOLUME_ML)
            slp.data('pH', ph, unit=exp.UNIT_PH)
            slp.data('temp_c', temp, unit=exp.UNIT_TEMP_C)

            # เตือนใกล้จุดสมมูล (alert when approaching equivalence)
            if not alerted and step >= alert_step:
                alerted = True
                slp.event('approaching_equivalence', {'volume_ml': volume})
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
