# ==============================================================================
# 04_flow_stepwise_finetune.py - ปรับละเอียดอัตราการไหลแบบ stop-flow
# Stepwise (stop-flow) fine-tune for the pump calibration
# ==============================================================================
# ทำไมต้องมีขั้นนี้ (Why this stage exists):
#   การสอบเทียบใน 01_flow_rate_calibration.py วัดอัตราการไหลแบบ "ไหลต่อเนื่อง"
#   แต่การไทเทรตจริง (Week_3) หยดแบบ "หยุด-ไหล" (stop-flow) เป็นช่วงสั้น ๆ
#   ทุกครั้งที่ปั๊มสตาร์ท จะมีช่วง "เสียเปล่า" (มอเตอร์หมุนขึ้น, ท่อยืดหยุ่น,
#   soft-start ของเฟิร์มแวร์) ทำให้แต่ละหยดจ่ายน้อยกว่าที่คำนวณ — สะสมทั้งการ
#   ไทเทรตอาจคลาดถึง ~0.4 mL ซึ่งยอมรับไม่ได้ในเคมีวิเคราะห์
#
#   Continuous calibration amortizes the START-UP DEFICIT (motor spin-up,
#   tubing elasticity, firmware soft-start) over one long run. Stop-flow
#   dosing pays that deficit ON EVERY BURST. This lesson MEASURES it:
#
#       V(t_on) = flow_ss x t_on - V_deficit          (two-parameter pump model)
#
#   ขั้นตอน: หยด N ครั้งด้วยโปรไฟล์เดียวกับการไทเทรตจริง -> นิสิตอ่านปริมาตร
#   จริงจากกระบอกตวง -> คำนวณ V_deficit ต่อหยด -> บันทึกเพิ่มในไฟล์สอบเทียบ
#   (burst_deficit_ml) — Week_3 จะชดเชยเวลาเปิดปั๊มให้อัตโนมัติ
#
# ลำดับบทเรียน (Lesson order):
#   01_flow_rate_calibration.py  -> flow_rate (ไหลต่อเนื่อง)
#   04_flow_stepwise_finetune.py -> burst_deficit_ml (ไฟล์นี้)
#   03_pump_validate_stepwise.py -> ตรวจสอบว่า stop-flow ตรงเป้าแล้ว
#
# สำคัญ: บทเรียนนี้ขับปั๊มผ่าน slp.set_actuator (เส้นทางเดียวกับการไทเทรต
# Week_3 รวม soft-start ของเฟิร์มแวร์) — ไม่ใช่ PWM ตรงแบบ 01/02/03 — เพื่อวัด
# ช่วงเสียเปล่าของ "ระบอบการทำงานจริง" (calibrate in the regime you operate!)
# ต่อแบตเตอรี่ก่อนใช้ปั๊มเสมอ (Battery required for the pump.)
# ==============================================================================

import time

import scilabpro as slp

# ==============================================================================
# ค่าคงที่ (Constants)
# ==============================================================================
CAL_PATH = '/workspace/data/flow_calibration.txt'
PUMP_ENDPOINT = 'CONTROL_1'
DOSE_VOLUME_ML = 0.2      # ปริมาตรต่อหยดเหมือน Week_3 (same as the titration)
N_BURSTS = 25             # จำนวนหยด -> คาดหวังรวม 5.0 mL (expected 5.0 mL)
PAUSE_MS = 1500           # หยุดระหว่างหยด (pause between bursts)
MAX_ON_MS = 1800          # เพดานความปลอดภัยต่อหยด (per-burst safety ceiling)


def load_flow_rate():
    """อ่าน flow_rate จากไฟล์สอบเทียบขั้นที่ 1 (ต้องทำ 01 ก่อน)."""
    try:
        with open(CAL_PATH, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('flow_rate='):
                    return float(line.split('=')[1])
    except OSError:
        pass
    return None


def save_deficit(flow_rate, deficit_ml, dead_time_ms):
    """เขียน burst_deficit_ml เพิ่มในไฟล์สอบเทียบ (คงค่า flow_rate เดิมไว้).

    รูปแบบไฟล์ยังเข้ากันได้ย้อนหลัง: ผู้อ่านเดิมที่รู้จักแค่ flow_rate=
    ยังใช้งานได้ (additive key, backward compatible).
    """
    lines = []
    try:
        with open(CAL_PATH, 'r') as f:
            for line in f:
                # ตัดค่า deficit เก่าออก (จะเขียนใหม่ด้านล่าง)
                if not line.strip().startswith('burst_deficit_ml='):
                    lines.append(line.rstrip('\n'))
    except OSError:
        lines = [f'flow_rate={flow_rate:.4f}']
    lines.append('# stop-flow fine-tune (04): per-burst start-up deficit')
    lines.append(f'# dead_time ~ {dead_time_ms:.0f} ms/burst at this flow rate')
    lines.append(f'burst_deficit_ml={deficit_ml:.4f}')
    with open(CAL_PATH, 'w') as f:
        f.write('\n'.join(lines) + '\n')


def run_finetune():
    print('=' * 60)
    print('ปรับละเอียดอัตราการไหลแบบ stop-flow (Stepwise Fine-tune)')
    print('=' * 60)

    flow = load_flow_rate()
    if flow is None or flow <= 0:
        print('ไม่พบ flow_rate — รัน 01_flow_rate_calibration.py ก่อน')
        print('(No flow_rate found - run 01_flow_rate_calibration.py first)')
        return

    # อ้างสิทธิ์ควบคุม (เส้นทางเดียวกับ Week_3) — จัดการกรณีแท็บเล็ตถือ lease
    try:
        slp.claim_controller()
    except OSError:
        print('ควบคุมบอร์ดไม่ได้: แอป MicroPad ถืออำนาจควบคุมอยู่')
        print('ปิด/ตัดการเชื่อมต่อแอป แล้วรันใหม่ หรือสั่งรันจากแอปแทน')
        print('(The app holds the controller lease - close it or run from the app)')
        return

    burst_ms = round(DOSE_VOLUME_ML / flow * 1000)
    if burst_ms > MAX_ON_MS:
        burst_ms = MAX_ON_MS
    expected_ml = N_BURSTS * flow * (burst_ms / 1000.0)

    print(f'flow_rate (ไหลต่อเนื่อง): {flow:.4f} mL/s')
    print(f'จะหยด {N_BURSTS} ครั้ง ครั้งละ {burst_ms} ms '
          f'(โปรไฟล์เดียวกับการไทเทรต Week_3)')
    print(f'ปริมาตรคาดหวังตามโมเดลไหลต่อเนื่อง: {expected_ml:.2f} mL')
    print('-' * 60)
    print('เตรียม: กระบอกตวง 10 mL ใต้ปลายท่อ + ไล่อากาศในท่อให้เต็ม (primed)')
    print('ตรวจสอบ: ต่อแบตเตอรี่แล้ว (ปั๊มใช้ไฟจากแบตเตอรี่)')
    print('Place a 10 mL graduated cylinder; ensure the line is primed and')
    print('the BATTERY is connected. Press Enter to start.')
    try:
        input('พร้อมแล้วกด Enter (Ready? press Enter): ')
    except Exception:
        pass  # บนเส้นทางที่ input ใช้ไม่ได้ ให้เริ่มเลย (fallback: start)

    # --- หยด N ครั้งแบบ "ไม่ชดเชย" เพื่อวัดช่วงเสียเปล่า (uncompensated) ---
    for i in range(1, N_BURSTS + 1):
        if slp.stop_requested():
            slp.set_actuator(PUMP_ENDPOINT, False)
            print('หยุดโดยผู้ใช้ (Stopped) — ปั๊มปิดแล้ว')
            return
        try:
            slp.set_actuator(PUMP_ENDPOINT, True, max_on_ms=MAX_ON_MS)
            time.sleep_ms(burst_ms)
        finally:
            slp.set_actuator(PUMP_ENDPOINT, False)
        print(f'หยดที่ {i:2d}/{N_BURSTS}')
        time.sleep_ms(PAUSE_MS)

    print('-' * 60)
    print('อ่านปริมาตรจริงจากกระบอกตวง (อ่านที่ก้นเมนิสคัส ระดับสายตา)')
    print('Read the ACTUAL volume from the cylinder (bottom of meniscus).')

    measured = None
    for _ in range(3):
        try:
            text = input('ปริมาตรที่วัดได้ (mL) / measured volume: ').strip()
            measured = float(text)
            break
        except (ValueError, TypeError):
            print('กรอกตัวเลข เช่น 3.60 (Enter a number, e.g. 3.60)')
        except Exception:
            break
    if measured is None or measured <= 0:
        print('ไม่ได้ค่าที่ใช้ได้ — ยกเลิก ไม่บันทึก (no usable value - aborted)')
        return

    # --- คำนวณช่วงเสียเปล่าต่อหยด (per-burst start-up deficit) ---
    deficit_ml = (expected_ml - measured) / N_BURSTS
    dead_time_ms = deficit_ml / flow * 1000.0

    print('=' * 60)
    print(f'คาดหวัง (Expected): {expected_ml:.2f} mL')
    print(f'วัดจริง (Measured): {measured:.2f} mL')
    print(f'ส่วนขาดรวม (Total shortfall): {expected_ml - measured:+.2f} mL')
    print(f'ช่วงเสียเปล่าต่อหยด (Per-burst deficit): {deficit_ml * 1000:.1f} uL')
    print(f'  = เวลาเสียเปล่า ~{dead_time_ms:.0f} ms ต่อการสตาร์ทปั๊ม 1 ครั้ง')

    if deficit_ml < 0:
        # วัดได้มากกว่าคาด — ผิดปกติ (ฟองอากาศ/อ่านผิด) ไม่บันทึกค่าติดลบ
        print('ผิดปกติ: วัดได้มากกว่าคาด — ตรวจฟองอากาศ/การอ่าน แล้วลองใหม่')
        print('(Measured MORE than expected - check bubbles/reading; not saved)')
        return
    if deficit_ml > DOSE_VOLUME_ML * 0.3:
        print('ผิดปกติ: ส่วนขาดเกิน 30% ของหยด — ตรวจท่อ/แบตเตอรี่ แล้วลองใหม่')
        print('(Deficit > 30% of the dose - check tubing/battery; not saved)')
        return

    save_deficit(flow, deficit_ml, dead_time_ms)
    print(f'บันทึกแล้ว (Saved): burst_deficit_ml={deficit_ml:.4f} -> {CAL_PATH}')
    print('ต่อไป: รัน 03_pump_validate_stepwise.py เพื่อยืนยันว่าตรงเป้า')
    print('(Next: run 03_pump_validate_stepwise.py to confirm on-target)')
    print('Week_3 จะชดเชยเวลาเปิดปั๊มให้อัตโนมัติจากค่านี้')


run_finetune()
