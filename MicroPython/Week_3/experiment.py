# ==============================================================================
# experiment.py - ค่าคงที่ของการทดลองไทเทรชัน (Titration Experiment Constants)
# ==============================================================================
# ไฟล์นี้รวบรวม "ค่าคงที่ของการทดลอง" ไว้ที่เดียว เพื่อให้นิสิตปรับแต่งได้ง่าย
# This file centralizes all EXPERIMENT constants so students can tune them easily.
#
# สำคัญ (IMPORTANT):
#   ไฟล์นี้ไม่มีหมายเลขขา GPIO! การกำหนดขาเป็นหน้าที่ของ routing profile ในเฟิร์มแวร์
#   This file contains NO GPIO pin numbers! Pin assignment is owned by the
#   firmware routing profile (titralab_v1_default). โค้ดบทเรียนอ้างถึงอุปกรณ์
#   ด้วย "ชื่อ endpoint" (เช่น 'CONTROL_1', 'PH') และเลขขาที่จำเป็นต่อ slp helper
#   เท่านั้น (เช่น ds18b20(16)).
#
# การสอบเทียบเป็นของนิสิต (Student-performed calibration — core pedagogy):
#   ไฟล์นี้ชี้ไปยังผลสอบเทียบที่นิสิตทำเองใน Week_2 (PH_CAL_PATH, FLOW_CAL_PATH)
#   บทเรียน "ใช้" ค่าสอบเทียบของบอร์ดตัวเอง ไม่ใช้ค่าคงที่ตายตัว และไม่เรียก
#   slp.ph_probe()/calibration.json (นั่นเป็นความสะดวกของแอป ไม่ใช่ของบทเรียนนี้)
#   This lesson CONSUMES the Week_2 student calibration; it does NOT use
#   slp.ph_probe()/calibration.json and never hard-codes flow rate or slope.
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. แยก "ค่าการทดลอง" (เคมี) ออกจาก "โค้ดควบคุมฮาร์ดแวร์" (Separation of concerns)
#   2. เข้าใจความสัมพันธ์ระหว่างปริมาตรตัวอย่าง จุดสมมูล และกราฟไทเทรชันรูป S
#   3. เห็นว่า "การนำผลสอบเทียบไปใช้" (apply slope_m·mV + b, V/flow_rate) ทำงานอย่างไร
# ==============================================================================

# ==============================================================================
# ชื่อ endpoint ของอุปกรณ์ (Device endpoint names)
# ==============================================================================
# ชื่อเหล่านี้ตรงกับ routing profile ของเฟิร์มแวร์ (titralab_v1_default)
# เฟิร์มแวร์เป็นผู้แปลงชื่อ endpoint -> หมายเลขขา GPIO ให้เอง
# These names match the firmware routing profile; the firmware maps the name
# to the actual GPIO. ใช้ชื่อแทนเลขขา เพื่อไม่ผูกบทเรียนกับการต่อสายจัมเปอร์
PUMP_ENDPOINT = 'CONTROL_1'   # ปั๊มเติมสารไทแทรนต์ (titrant dosing pump)

# ขา GPIO ที่ slp helper ต้องรู้โดยตรง (GPIO that slp helpers need by number)
# pH และ DS18B20 helper รับ "หมายเลขขา" ตาม titralab_v1_default
# (slp.read_analog('PH') อ่าน ADC ดิบของ PH_PROBE / slp.ds18b20(num) ต้องการเลขขา)
PH_PROBE_PIN = 32             # PH_PROBE = GPIO32 (ADC1 — ห้ามใช้ 25)
TEMP_PROBE_PIN = 16           # DS18B20 = GPIO16 (OneWire)

# ชื่อ endpoint ของหัววัด pH สำหรับ slp.read_analog (raw ADC ของ PH_PROBE)
# pH-probe endpoint name for slp.read_analog (raw ADC of PH_PROBE)
PH_ENDPOINT = 'PH'            # ตรงกับ routing profile titralab_v1_default

# ==============================================================================
# ไฟล์สอบเทียบที่นิสิตทำเองใน Week_2 (Student-performed Week_2 calibration files)
# ==============================================================================
# *** หัวใจของบทเรียน (load-bearing pedagogy) ***
# อุปกรณ์ TitraLab เป็นของราคาประหยัดและแตกต่างกันในแต่ละบอร์ด นิสิตจึง "ต้อง"
# สอบเทียบเอง บทเรียนนี้ "ใช้" ผลสอบเทียบของบอร์ดตัวเอง ไม่ใช่ค่าคงที่ตายตัว
# TitraLab devices are low-cost and vary unit-to-unit, so students MUST calibrate
# them; this lesson CONSUMES each board's own calibration, never a hard-coded value.
#
#   • Week_2 (ผู้สร้าง/producer): สคริปต์สอบเทียบเขียนไฟล์เหล่านี้
#   • Week_3 (ผู้ใช้/consumer):  บทเรียนนี้อ่านไฟล์เหล่านี้มาใช้ (อย่างเห็นได้ชัด)
#
# เส้นทางถาวรใน workspace (persistent paths; survive reboot, same path both weeks)
PH_CAL_PATH = '/workspace/data/ph_calibration.txt'     # slope_m,intercept_b,r_squared,cal_temp
FLOW_CAL_PATH = '/workspace/data/flow_calibration.txt'  # บรรทัด flow_rate=<mL/s>

# ตัวประกอบแปลง ADC ดิบ -> มิลลิโวลต์ (raw ADC -> mV conversion factor)
# ต้องตรงกับ Week_2 02_calibration_3point.py: voltage_mv = adc_value * 3300 / 4095
# MUST match Week_2 exactly, otherwise applying slope_m/intercept_b gives wrong pH.
#   ADC 12-bit (0-4095), Vref = 3300 mV (ATTN_11DB, 0-3.3V)
ADC_MAX_VALUE = 4095          # ค่า ADC สูงสุด 12-bit (Week_2 ใช้ 4095)
ADC_REFERENCE_MV = 3300       # แรงดันอ้างอิง 3.3V = 3300 mV (Week_2 ใช้ 3300)
RAW_TO_MV = ADC_REFERENCE_MV / ADC_MAX_VALUE   # = 3300/4095 ≈ 0.8059 mV ต่อ 1 นับ ADC

# ==============================================================================
# พารามิเตอร์การไทเทรชัน (Titration parameters)
# ==============================================================================
# ใช้ปริมาตรคงที่ต่อ step เพื่อให้ทุกจุดบนกราฟห่างเท่ากัน ง่ายต่อการวิเคราะห์
# Fixed dose volume per step keeps every curve point equally spaced.
DOSE_VOLUME_ML = 0.2          # ปริมาตรไทแทรนต์ต่อ step (mL per dose step)

# ปริมาตรสารตัวอย่าง (analyte sample volume)
SAMPLE_VOLUME_ML = 5.0        # mL ของสารตัวอย่าง (analyte placed in the cell)

# ปริมาตรไทเทรตสูงสุด = 2 เท่าของปริมาตรตัวอย่าง เพื่อให้ได้กราฟรูป S ที่สมบูรณ์
# Max titration volume = 2x sample volume → complete S-curve past equivalence.
MAX_VOLUME_ML = 2 * SAMPLE_VOLUME_ML   # = 10.0 mL

# ==============================================================================
# ความเข้มข้นเชิงนาม (Nominal concentrations) — ใช้ในการคำนวณ C1V1 = C2V2
# ==============================================================================
# สารไทแทรนต์ (titrant) คือสารละลายในปั๊มที่ทราบความเข้มข้นแน่นอน
# สารตัวอย่าง (analyte) คือสารที่ต้องการหาความเข้มข้น (ค่านี้เป็นค่าเชิงนาม
# สำหรับเปรียบเทียบ/ตรวจสอบ — ค่าจริงจะคำนวณจากจุดสมมูลที่วัดได้)
TITRANT_CONCENTRATION_M = 0.1    # mol/L ความเข้มข้นไทแทรนต์ที่ทราบ (e.g. NaOH 0.1 M)
ANALYTE_NOMINAL_M = 0.1          # mol/L ความเข้มข้นตัวอย่างเชิงนาม (e.g. HCl ~0.1 M)

# อัตราส่วนสโตอิชิโอเมตรี (stoichiometric mole ratio = mol analyte : mol titrant)
# ใช้ในสูตร: C_analyte = ratio * C_titrant * V_eq / V_sample
#
#   • กรด 1 โปรตอน + เบส 1:1 (เช่น HCl + NaOH)           -> ratio = 1.0
#   • กรดไดโปรติก analyte + เบส (เช่น H2SO4 + 2 NaOH)      -> ratio = 0.5
#       เพราะ H2SO4 1 โมล ทำปฏิกิริยากับ NaOH 2 โมล
#       (1 mol diprotic analyte consumes 2 mol titrant -> 1/2 = 0.5)
#   • เบส 1 ตำแหน่ง analyte + กรดไดโปรติก titrant          -> ratio = 2.0
#
# บทเรียนนี้ตั้งเป้ากรณี 1:1 (HCl + NaOH). หากใช้สโตอิชิโอเมตรีอื่น
# ต้องแก้ค่านี้ให้ตรง (มิฉะนั้นความเข้มข้นที่คำนวณได้จะผิด)
# This lesson targets the 1:1 case; change this value for other stoichiometries
# or the computed concentration WILL be wrong.
STOICHIOMETRIC_RATIO = 1.0       # mol analyte ต่อ mol titrant (1:1 acid-base)

# ==============================================================================
# เวลาหน่วง (Settle / timing delays) — หน่วยมิลลิวินาที (milliseconds)
# ==============================================================================
# pH probe ต้องการเวลา 10-20 วินาทีจึงจะเสถียรหลังเติมไทแทรนต์แต่ละครั้ง
# The pH probe needs 10-20 s to stabilize after each dose.
SETTLE_MS = 10000             # รอให้ pH คงที่หลังหยดแต่ละครั้ง (settle after each dose)

# ==============================================================================
# เวลาเปิดปั๊ม — มาจากการสอบเทียบ ไม่ใช่ค่าคงที่ตายตัว (pump-on time is CALIBRATED)
# ==============================================================================
# *** ไม่มี DOSE_ON_MS แบบฮาร์ดโค้ดอีกต่อไป ***  เวลาเปิดปั๊มต่อ step คำนวณสด
# จากอัตราการไหลที่สอบเทียบของบอร์ดตัวเอง (อ่านจาก FLOW_CAL_PATH) แบบ closed-loop
# บนปริมาตร:   pump_time_ms = round(DOSE_VOLUME_ML / flow_rate_ml_s * 1000)
# ดังนั้นปริมาตรที่รายงาน (step * DOSE_VOLUME_ML) จึงเป็นปริมาตรที่ "ส่งจริง"
# There is NO hard-coded DOSE_ON_MS anymore. The pump-on time per step is derived
# LIVE from this board's calibrated flow rate (closed-loop on volume), so the
# reported volume equals the DELIVERED volume.

# เพดานเวลาเปิดปั๊มเพื่อความปลอดภัย (hard safety ceiling for any single dose)
# ส่งเป็น max_on_ms ของ slp.set_actuator เสมอ และ "clamp" เวลาที่คำนวณได้ไม่ให้
# เกินค่านี้ เผื่อกรณีไฟล์สอบเทียบให้ flow_rate ต่ำผิดปกติ (เช่น ปั๊มเกือบตัน)
# Always passed as max_on_ms AND used to clamp the computed time, in case a bad
# calibration file yields an abnormally low flow rate (e.g. a nearly clogged pump).
DOSE_MAX_ON_MS = 1500         # ปั๊มจะถูกตัด/clamp ไม่เกินค่านี้ (firmware guard ceiling)

# ==============================================================================
# การหาจุดสมมูล / การเตือน (Equivalence detection / alerts)
# ==============================================================================
# จำนวนการอ่าน pH ต่อ 1 จุด แล้วใช้ค่ามัธยฐาน (median-of-N) เพื่อลดสัญญาณรบกวน
# Number of pH samples per data point; the median rejects spurious ADC reads.
PH_SAMPLES_PER_POINT = 5      # อ่าน pH 5 ครั้งต่อจุด แล้วใช้ค่ามัธยฐาน
PH_SAMPLE_GAP_MS = 200        # หน่วงระหว่างการอ่าน pH แต่ละครั้ง (ms)

# ปริมาตรเตือนใกล้จุดสมมูล (volume at which to alert "approaching equivalence")
# สำหรับ HCl 0.1M 5mL + NaOH 0.1M จุดสมมูล ~5.0 mL → เตือนล่วงหน้าที่ 4.80 mL
ALERT_VOLUME_ML = 4.80        # เตือนนิสิตให้เตรียมสังเกตที่ปริมาตรนี้

# หน่วยที่ใช้สตรีมข้อมูลไปยังแอป MicroPad (units for slp.data streaming)
UNIT_PH = 'pH'
UNIT_TEMP_C = 'C'
UNIT_VOLUME_ML = 'mL'
