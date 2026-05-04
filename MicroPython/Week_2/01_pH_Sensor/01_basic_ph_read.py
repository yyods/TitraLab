# ==============================================================================
# 01_basic_ph_read.py - การวัดเวลาตอบสนองของหัววัด pH (pH Probe Response Time)
# ==============================================================================
# โปรแกรมนี้ใช้วัดเวลาตอบสนอง (Response Time) ของหัววัด pH โดยบันทึกค่า mV
# ทุกวินาทีเป็นเวลา 45 วินาที ขณะย้ายหัววัดระหว่างบัฟเฟอร์ pH 4, 7, และ 10
# This program measures pH probe response time by recording mV readings
# every second for 45 seconds while moving the probe between pH 4, 7, 10 buffers
#
# เวลาที่ใช้สอน (Teaching time): 45-60 นาที
#
# ##############################################################################
# ส่วนที่ 1: เวลาตอบสนองของหัววัด pH คืออะไร? (What is pH Probe Response Time?)
# ##############################################################################
#
# เวลาตอบสนอง (Response Time) คือ เวลาที่หัววัด pH ต้องการเพื่อแสดงค่าที่เสถียร
# หลังจากย้ายจากสารละลายหนึ่งไปยังอีกสารละลายหนึ่ง
#
# Response time is the time a pH probe needs to show a stable reading
# after being moved from one solution to another.
#
# หัววัด pH ทำงานโดยอาศัยการแลกเปลี่ยนไอออน H+ ผ่านเมมเบรนแก้ว ซึ่งต้องใช้เวลา
# pH probes work by H+ ion exchange through a glass membrane, which takes time.
#
# ประสิทธิภาพของหัววัด (Probe Performance):
# +-----------------+---------------------+--------------------------------+
# | สภาพหัววัด      | เวลาตอบสนอง 90%     | ลักษณะกราฟ                     |
# | Probe Condition | 90% Response Time   | Graph Characteristic           |
# +-----------------+---------------------+--------------------------------+
# | ดีมาก           | 5-10 วินาที         | การเปลี่ยนแปลงคมชัด             |
# | (Excellent)     | 5-10 seconds        | Sharp transitions              |
# +-----------------+---------------------+--------------------------------+
# | ปานกลาง         | 15-20 วินาที        | เปลี่ยนแปลงช้า แต่เสถียรได้      |
# | (Moderate)      | 15-20 seconds       | Slow but reaches stability     |
# +-----------------+---------------------+--------------------------------+
# | เสื่อมสภาพ       | 30+ วินาที          | ค่าลอยไม่นิ่ง ไม่เสถียร          |
# | (Degraded)      | 30+ seconds         | Drifting, never stabilizes     |
# +-----------------+---------------------+--------------------------------+
#
# หมายเหตุ: "เวลาตอบสนอง 90%" หมายถึงเวลาที่ค่าเปลี่ยนไป 90% ของการเปลี่ยนแปลงทั้งหมด
# Note: "90% response time" means time to reach 90% of total change
#
# ##############################################################################
# ส่วนที่ 2: ทำไมต้องวัดเวลาตอบสนอง? (Why Measure Response Time?)
# ##############################################################################
#
# 1. ประเมินคุณภาพหัววัด (Assess Probe Quality/Health)
#    - หัววัดใหม่ควรตอบสนองภายใน 10 วินาที
#    - New probes should respond within 10 seconds
#    - หัววัดเก่าหรือเสียหายจะตอบสนองช้ามาก
#    - Old or damaged probes respond very slowly
#
# 2. เข้าใจข้อจำกัดสำหรับการไทเทรต (Understand Limitations for Titration)
#    - ถ้าหัววัดช้า ต้องเติมสารไทแทรนต์ช้าลง มิฉะนั้นจะเลยจุดสมมูล
#    - If probe is slow, must add titrant slowly or will overshoot endpoint
#    - หัววัดที่ตอบสนองช้า 20 วินาที หมายความว่าต้องรอ 20 วินาทีหลังเติมแต่ละครั้ง
#    - A 20-second response means waiting 20 seconds after each addition
#
# 3. ตัดสินใจเปลี่ยนหัววัด (Decide When to Replace Probe)
#    - หัววัดที่ไม่เสถียรภายใน 45 วินาที ควรเปลี่ยนใหม่
#    - Probes not stabilizing within 45 seconds should be replaced
#    - การใช้หัววัดเสื่อมสภาพจะทำให้ผลการทดลองไม่แม่นยำ
#    - Using degraded probes leads to inaccurate results
#
# 4. เปรียบเทียบระหว่างหัววัด (Compare Between Probes)
#    - นิสิตสามารถเปรียบเทียบกราฟระหว่างกลุ่มได้
#    - Students can compare graphs between groups
#    - หัววัดจากผู้ผลิตต่างกันอาจมีคุณสมบัติต่างกัน
#    - Different manufacturers may have different characteristics
#
# ##############################################################################
# ส่วนที่ 3: ค่าที่คาดหวังกับวงจร LMC6482 (Expected Values with LMC6482 Circuit)
# ##############################################################################
#
# วงจร LMC6482 op-amp บนบอร์ด TitraLab เลื่อนสัญญาณ +1650 mV เพื่อให้ ADC อ่านได้
# The LMC6482 op-amp circuit on TitraLab board offsets signal by +1650 mV
# so the ADC can read the full pH range (both acidic and basic).
#
# ปัญหา: หัววัด pH ให้แรงดันบวก (กรด) และลบ (เบส) แต่ ADC อ่านได้เฉพาะ 0-3.3V
# Problem: pH probe outputs positive (acid) and negative (base) voltages,
#          but ESP32 ADC can only read 0-3.3V
#
# วิธีแก้: เลื่อนสัญญาณขึ้น 1650 mV (ครึ่งหนึ่งของ 3.3V)
# Solution: Offset the signal by +1650 mV (half of 3.3V)
#
#     E_measured = E_probe + 1650 mV
#
# ค่าที่คาดหวังที่ 25C (Expected values at 25C):
# +-----------+---------------+------------------+------------------------+
# | บัฟเฟอร์  | E_probe (mV)  | E_measured (mV)  | ช่วงค่าที่ยอมรับ       |
# | Buffer    | From probe    | After offset     | Acceptable range       |
# +-----------+---------------+------------------+------------------------+
# | pH 4      | +177 mV       | ~1827 mV         | 1780-1870 mV           |
# | (กรด/acid)| (acidic)      |                  |                        |
# +-----------+---------------+------------------+------------------------+
# | pH 7      | 0 mV          | ~1650 mV         | 1600-1700 mV           |
# | (กลาง)    | (neutral)     | (midpoint)       |                        |
# +-----------+---------------+------------------+------------------------+
# | pH 10     | -177 mV       | ~1473 mV         | 1420-1520 mV           |
# | (เบส/base)| (basic)       |                  |                        |
# +-----------+---------------+------------------+------------------------+
#
# ที่มาของค่า 177 mV: จากสมการ Nernst ที่ 25C
# Origin of 177 mV: From Nernst equation at 25C
#   Delta_E = (pH difference) x 59.16 mV/pH = 3 x 59.16 = 177.5 mV
#
# ความแตกต่างระหว่างบัฟเฟอร์ (Voltage differences between buffers):
#   pH 4 -> pH 7:  ~177 mV  (ลดลง / decreases)
#   pH 7 -> pH 10: ~177 mV  (ลดลงอีก / decreases more)
#
# หมายเหตุ: ค่าจริงอาจต่างจากทฤษฎีได้ 10-20% ขึ้นกับสภาพหัววัดและการสอบเทียบ
# Note: Actual values may differ 10-20% from theory depending on probe
#       condition and calibration state
#
# ##############################################################################
# ส่วนที่ 4: วิธีอ่านกราฟผลการทดลอง (How to Interpret the Results Plot)
# ##############################################################################
#
# หลังการทดลอง นิสิตจะนำไฟล์ CSV ไป plot กราฟ Time (s) vs Voltage (mV)
# After the experiment, students will plot Time (s) vs Voltage (mV)
#
# รูปแบบกราฟที่ดี (Good Response Pattern):
#
#        mV
#        ^
#  1827 -|____              <-- pH 4: เสถียรเร็ว (stabilizes quickly)
#        |    \
#        |     \_______     <-- การเปลี่ยนแปลงคมชัด (sharp transition)
#  1650 -|            |
#        |            \____
#        |                 \_____ <-- pH 10: เสถียรเร็ว (stabilizes quickly)
#  1473 -|                      |
#        |________________________|____> Time (s)
#        0    15    30    45
#
# ลักษณะที่ดี (Good characteristics):
# - การเปลี่ยนแปลงเกิดขึ้นเร็ว (< 5 วินาที) / Fast transitions (< 5 seconds)
# - ค่าเสถียรและราบเรียบ / Stable, flat plateaus
# - ค่าใกล้เคียงทฤษฎี / Values close to theoretical
#
# รูปแบบกราฟที่แสดงปัญหา (Problematic Patterns):
#
# 1. การเปลี่ยนแปลงช้า (Slow Transition):
#    ลักษณะ: เส้นโค้งเอียงมาก ใช้เวลานานกว่าจะเสถียร (10-20 วินาที)
#    Pattern: Gradual slope, takes long to stabilize (10-20 seconds)
#    สาเหตุ: หัววัดเสื่อมสภาพ หรือเมมเบรนสกปรก
#    Cause: Degraded probe or dirty membrane
#    วิธีแก้: ทำความสะอาดหัววัด หรือเปลี่ยนใหม่
#    Solution: Clean probe or replace
#
# 2. ค่าลอยไม่นิ่ง (Drifting/Unstable):
#    ลักษณะ: ค่าขึ้นลงไม่หยุด แม้รอนาน ไม่มี plateau ราบ
#    Pattern: Values keep fluctuating, no flat plateau
#    สาเหตุ: หัววัดเสียหาย หรือสารละลายภายในแห้ง/หมด
#    Cause: Damaged probe or dried/depleted internal solution
#    วิธีแก้: เปลี่ยนหัววัดใหม่
#    Solution: Replace probe
#
# 3. Overshoot แล้วกลับ (Overshoot then Return):
#    ลักษณะ: ค่าเกินเป้าหมายแล้วค่อยๆ กลับมา
#    Pattern: Value overshoots target then slowly returns
#    หมายเหตุ: นี่เป็นพฤติกรรมปกติสำหรับหัววัดบางรุ่น
#    Note: This is NORMAL behavior for some probes
#    ไม่จำเป็นต้องแก้ไข แต่ต้องรอให้ค่าเสถียรก่อนอ่าน
#    No fix needed, but must wait for stabilization before reading
#
# 4. ไม่ตอบสนอง (No Response):
#    ลักษณะ: ค่าไม่เปลี่ยนแม้ย้ายบัฟเฟอร์ เส้นตรงราบ
#    Pattern: Value doesn't change when moving between buffers
#    สาเหตุ: หัววัดเสียหายรุนแรง หรือการเชื่อมต่อหลุด
#    Cause: Severely damaged probe or disconnection
#    วิธีแก้: ตรวจสอบการเชื่อมต่อ หรือเปลี่ยนหัววัด
#    Solution: Check connections or replace probe
#
# ##############################################################################
# ส่วนที่ 5: ขั้นตอนการทดลอง (Experimental Procedure)
# ##############################################################################
#
# อุปกรณ์ที่ต้องเตรียม (Materials needed):
#   - บัฟเฟอร์ pH 4 (สีแดง) - ประมาณ 50 mL ในบีกเกอร์
#   - บัฟเฟอร์ pH 7 (สีเหลืองหรือเขียว) - ประมาณ 50 mL ในบีกเกอร์
#   - บัฟเฟอร์ pH 10 (สีน้ำเงิน) - ประมาณ 50 mL ในบีกเกอร์
#   - น้ำ DI ในขวดฉีด สำหรับล้างหัววัด
#   - กระดาษทิชชูหรือ Kimwipes สำหรับซับหัววัด
#
# การจัดวาง (Setup arrangement):
#   [pH 4] --- [DI Water] --- [pH 7] --- [DI Water] --- [pH 10]
#              (ขวดฉีด)                    (ขวดฉีด)
#
# ขั้นตอน (Steps):
#
# ขั้นที่ 1: เตรียมบัฟเฟอร์ 3 บีกเกอร์ วางเรียงกัน
#           Prepare 3 beakers with buffers, arrange in a row
#
# ขั้นที่ 2: จุ่มหัววัดในบัฟเฟอร์ pH 4 รอ 30 วินาทีให้เสถียรก่อนเริ่มบันทึก
#           Immerse probe in pH 4 buffer, wait 30s to stabilize before recording
#           ** สำคัญ: ต้องรอให้เสถียรก่อนเริ่ม ไม่งั้นกราฟจะไม่ถูกต้อง **
#           ** Important: Must wait for stability, otherwise graph will be wrong **
#
# ขั้นที่ 3: กดปุ่ม 1 เพื่อเริ่มบันทึก (โปรแกรมบันทึก 45 วินาที)
#           Press Button 1 to start recording (program records for 45 seconds)
#
# ขั้นที่ 4: ทำตามลำดับเวลาต่อไปนี้ (Follow this time sequence):
#
#    วินาทีที่ 0-15:   อยู่ใน pH 4 (ไม่ต้องทำอะไร รอดูค่า)
#                      Stay in pH 4 (just observe the stable reading)
#
#    ประมาณวินาทีที่ 15: เปลี่ยนจาก pH 4 ไป pH 7
#                        Change from pH 4 to pH 7
#                        ขั้นตอน: ยก -> ฉีด DI 2-3 ครั้ง -> ซับเบาๆ -> จุ่ม pH 7
#                        Steps: Lift -> Rinse DI 2-3x -> Blot gently -> Dip pH 7
#                        ** ทำให้เร็ว ใช้เวลาไม่เกิน 3-5 วินาที **
#                        ** Do quickly, within 3-5 seconds **
#
#    วินาทีที่ 15-30:  อยู่ใน pH 7 (สังเกตการเปลี่ยนแปลง)
#                      Stay in pH 7 (observe the transition)
#
#    ประมาณวินาทีที่ 30: เปลี่ยนจาก pH 7 ไป pH 10
#                        Change from pH 7 to pH 10
#                        ขั้นตอนเดียวกัน: ยก -> ฉีด DI -> ซับ -> จุ่ม pH 10
#                        Same steps: Lift -> Rinse DI -> Blot -> Dip pH 10
#
#    วินาทีที่ 30-45:  อยู่ใน pH 10 (สังเกตการเปลี่ยนแปลง)
#                      Stay in pH 10 (observe the transition)
#
# ขั้นที่ 5: โปรแกรมจะหยุดบันทึกอัตโนมัติที่ 45 วินาที และบันทึกไฟล์ CSV
#           Program stops automatically at 45s and saves CSV file
#
# ขั้นที่ 6: ดาวน์โหลดไฟล์ CSV ผ่าน Thonny IDE ไปยังคอมพิวเตอร์
#           Download CSV file via Thonny IDE to computer
#           วิธี: Files panel -> คลิกขวาที่ไฟล์ -> Download to...
#           Method: Files panel -> Right-click file -> Download to...
#
# ขั้นที่ 7: Plot กราฟ Time vs Voltage ด้วย Excel, Python, หรือซอฟต์แวร์อื่น
#           Plot Time vs Voltage using Excel, Python, or other software
#
# ##############################################################################
# ส่วนที่ 6: เทคนิคการล้างหัววัด (Probe Rinsing Technique)
# ##############################################################################
#
# การล้างที่ถูกต้องสำคัญมากสำหรับการวัดเวลาตอบสนอง
# Proper rinsing is CRITICAL for accurate response time measurement.
#
# วิธีที่ถูกต้อง (Correct Method):
#   1. ยกหัววัดขึ้นจากบัฟเฟอร์ (Lift probe from buffer)
#   2. ฉีดน้ำ DI ให้ไหลผ่านหัววัด 2-3 ครั้ง (Squirt DI water 2-3 times)
#      ** ไม่ต้องแช่ในน้ำ DI ** (Don't soak in DI water)
#   3. ซับเบาๆ ด้วยกระดาษทิชชู (Gently blot with tissue)
#      ** ไม่ถูแรงๆ ** (Don't rub hard)
#   4. จุ่มในบัฟเฟอร์ถัดไปทันที (Immediately dip in next buffer)
#   รวมเวลา: ไม่เกิน 5 วินาที (Total time: under 5 seconds)
#
# วิธีที่ผิด (Incorrect Methods):
#   X แช่ในน้ำ DI นาน -> ทำให้สารละลายภายในหัววัดเจือจาง
#     (Soaking in DI) -> Dilutes internal solution
#   X ถูหัววัดแรงๆ -> อาจทำลายเมมเบรนแก้วที่บอบบาง
#     (Rubbing hard) -> May damage delicate glass membrane
#   X ไม่ล้างเลย -> บัฟเฟอร์ปนเปื้อนกัน ทำให้ค่า pH บัฟเฟอร์เปลี่ยน
#     (No rinsing) -> Cross-contamination changes buffer pH
#
# ##############################################################################
# ส่วนที่ 7: หลักการทางเคมี - สมการ Nernst (Chemistry: Nernst Equation)
# ##############################################################################
#
# หัววัด pH ให้สัญญาณแรงดันไฟฟ้า (mV) ตามสมการ Nernst:
# pH probes output voltage (mV) according to the Nernst equation:
#
#     E_probe = E0 - (2.303RT/nF) x pH
#
# โดย (where):
#   E_probe = ศักย์ไฟฟ้าจากหัววัด (mV) - ค่าบวกสำหรับกรด, ลบสำหรับเบส
#             (Potential from probe - positive for acid, negative for base)
#   E0      = ศักย์ไฟฟ้ามาตรฐาน (mV) - ค่าที่ pH = 0
#             (Standard potential at pH = 0)
#   R       = ค่าคงที่ของก๊าซ = 8.314 J/(mol.K)
#             (Gas constant)
#   T       = อุณหภูมิสัมบูรณ์ (K) = Celsius + 273.15
#             (Absolute temperature)
#   n       = จำนวนอิเล็กตรอนที่ถ่ายเท = 1 สำหรับ H+
#             (Number of electrons = 1 for H+)
#   F       = ค่าคงที่ฟาราเดย์ = 96485 C/mol
#             (Faraday constant)
#
# ความชันทฤษฎี (Theoretical slope) ที่อุณหภูมิต่างๆ:
#   20C (293.15K): -58.17 mV/pH
#   25C (298.15K): -59.16 mV/pH  <- ค่าที่ใช้บ่อยในห้องปฏิบัติการ
#   30C (303.15K): -60.15 mV/pH
#
# ความแตกต่างแรงดันระหว่าง pH ที่ต่างกัน 3 หน่วย (เช่น pH 4 vs pH 7):
# Voltage difference for 3 pH units (e.g., pH 4 vs pH 7):
#   Delta_E = 3 x 59.16 = 177.5 mV (ที่ 25C / at 25C)
#
# ##############################################################################
# วัตถุประสงค์การเรียนรู้ (Learning Objectives)
# ##############################################################################
#
# ทางเคมี (Chemistry):
# 1. เข้าใจว่าหัววัด pH ไม่ได้ตอบสนองทันที แต่ต้องใช้เวลา
#    (Understand that pH probes don't respond instantly - they need time)
# 2. เรียนรู้ว่าสภาพของหัววัดส่งผลต่อความเร็วในการตอบสนอง
#    (Learn that probe condition affects response speed)
# 3. เชื่อมโยงเวลาตอบสนองกับอัตราการเติมสารไทแทรนต์ในการไทเทรต
#    (Connect response time to titrant addition rate in titration)
# 4. เข้าใจการประยุกต์สมการ Nernst ในการวัด pH จริง
#    (Understand Nernst equation application in real pH measurement)
#
# ทางโปรแกรม (Programming):
# 1. การใช้ ADC (Analog-to-Digital Converter) อ่านค่าจากเซ็นเซอร์ pH
#    (Using ADC to read pH sensor values)
# 2. ใช้ Timer และ Interrupt สำหรับการบันทึกข้อมูลอัตโนมัติทุกวินาที
#    (Using Timer and Interrupt for automatic data recording every second)
# 3. การบันทึกข้อมูลการทดลองลงไฟล์ CSV สำหรับวิเคราะห์ภายหลัง
#    (Saving experimental data to CSV file for later analysis)
# 4. การออกแบบ User Interface ด้วยปุ่มกดและจอแสดงผล
#    (Designing User Interface with buttons and display)
#
# ##############################################################################
# Hardware Configuration
# ##############################################################################
#
# นิสิตเลือกขา GPIO เองตามการต่อสายจัมเปอร์
# Students choose GPIO pins based on their own jumper wire connections
#
# สำหรับตัวอย่างนี้ (For this example):
# - MY_PH_PIN (GPIO 32): PH_PROBE - ต้องเป็นขาที่รองรับ ADC
#                        Must be ADC-capable pin
# - MY_BTN1_PIN (GPIO 34): BUTTON_1 - input-only pin เหมาะสำหรับปุ่ม
#                          Input-only pin, perfect for buttons
#
# GPIO ที่รองรับ ADC (ADC-capable GPIOs):
#   ADC1: GPIO 32, 33, 34, 35, 36, 39 (แนะนำ - ไม่ conflict กับ WiFi)
#   ADC2: GPIO 25, 26, 27 (หลีกเลี่ยงถ้าใช้ WiFi)
#
# TFT Display (FIXED - ต่อบน PCB แล้ว ไม่ต้องต่อสาย):
#   GPIO 14: SCK, GPIO 13: MOSI, GPIO 27: DC, GPIO 15: CS, GPIO 0: RST
#
# ==============================================================================

from ili9341 import Display, color565
from xglcd_font import XglcdFont
from machine import Pin, SPI, ADC, Timer
import time

# ==============================================================================
# ค่าคงที่สำหรับการตั้งค่า (Configuration Constants)
# ==============================================================================
# ระยะเวลาบันทึกข้อมูล (Recording duration)
# นิสิตสามารถเปลี่ยนค่านี้ได้ตามการทดลอง
RECORDING_DURATION_S = 45    # 45 วินาที (45 seconds)

# ค่า offset จากวงจร LMC6482 (LMC6482 circuit offset)
# ค่านี้ใช้อ้างอิงเพื่อให้นิสิตเข้าใจว่าทำไม pH 7 อ่านได้ ~1650 mV
OFFSET_MV = 1650.0           # แรงดัน offset ที่ pH 7 = 3.3V / 2

# ==============================================================================
# การตั้งค่าขา GPIO (GPIO Pin Configuration)
# ==============================================================================
# นิสิตกำหนดขา GPIO ตามการต่อสายจัมเปอร์ของตนเอง
# Students define GPIO pins based on their own jumper wire connections

# === นิสิตกำหนดขา GPIO ที่นี่ (Student defines GPIO pins here) ===

# pH Sensor: ต้องการ ADC -> เลือก GPIO ที่รองรับ ADC
# แนะนำ ADC1 (32, 33, 34, 35, 36, 39) เพราะไม่ conflict กับ WiFi
MY_PH_PIN = 32               # ตัวอย่าง: เลือก GPIO32 สำหรับ PH_PROBE

# Button: ต้องการ INPUT -> GPIO ใดก็ได้ (input-only pins ดีมาก)
# GPIO 34, 35, 39 เป็น input-only - เหมาะสำหรับปุ่มกด
MY_BTN1_PIN = 34             # ตัวอย่าง: เลือก GPIO34 สำหรับ BUTTON_1

# ==============================================================================
# การตั้งค่า ADC สำหรับเซ็นเซอร์ pH (ADC Setup for pH Sensor)
# ==============================================================================
# ADC (Analog-to-Digital Converter) แปลงสัญญาณแอนะล็อกเป็นดิจิทัล
# ATTN_11DB ตั้งค่าให้อ่านแรงดัน 0-3.3V (ความละเอียด 12-bit: 0-4095)
adc = ADC(Pin(MY_PH_PIN))
adc.atten(ADC.ATTN_11DB)

# ==============================================================================
# การตั้งค่าปุ่มกด (Button Setup)
# ==============================================================================
# หมายเหตุ: GPIO34 เป็น input-only pin ไม่รองรับ internal pull-up/pull-down
# Note: GPIO34 is input-only, does NOT support internal pull-up/pull-down
# บอร์ด TitraLab มี external pull-up ผ่าน Schmitt trigger (74HC14D) แล้ว
button_1 = Pin(MY_BTN1_PIN, Pin.IN)

# ==============================================================================
# การตั้งค่าจอแสดงผล TFT ILI9341 (TFT Display Setup)
# ==============================================================================
# ขา TFT เป็นขาที่ต่อบน PCB แล้ว (FIXED pins - hardwired on PCB)
spi = SPI(1, baudrate=10000000, sck=Pin(14), mosi=Pin(13))
display = Display(spi, cs=Pin(15), dc=Pin(27), rst=Pin(0),
                  width=240, height=320, rotation=90)

# โหลดฟอนต์ (Load font)
font = XglcdFont("fonts/EspressoDolce18x24.c", 18, 24)

# ==============================================================================
# ฟังก์ชันหาหมายเลขไฟล์ถัดไป (Find Next Available File Number)
# ==============================================================================
def find_next_file_number():
    """
    หาหมายเลขไฟล์ถัดไปที่ยังไม่มีอยู่ (Find next file number that doesn't exist)

    ป้องกันการเขียนทับไฟล์เก่าเมื่อรีสตาร์ทโปรแกรม
    Prevents overwriting old files when program restarts

    Returns:
        int: หมายเลขไฟล์ถัดไป (Next available file number)
    """
    import os

    # หาไฟล์ที่มีอยู่แล้ว (Find existing files)
    max_num = 0
    try:
        files = os.listdir()
        for f in files:
            if f.startswith("response_time_R") and f.endswith(".csv"):
                # ดึงหมายเลขจากชื่อไฟล์ (Extract number from filename)
                # response_time_R1.csv -> 1
                try:
                    num_str = f[15:-4]  # ตัด "response_time_R" และ ".csv"
                    num = int(num_str)
                    if num > max_num:
                        max_num = num
                except:
                    pass
    except:
        pass

    return max_num  # จะถูก +1 ใน start_recording()

# ==============================================================================
# ตัวแปรสถานะ (State Variables)
# ==============================================================================
recording = False            # สถานะการบันทึก (Recording state)
data_buffer = []             # บัฟเฟอร์เก็บข้อมูล [(time_s, voltage_mV), ...]
recording_round = find_next_file_number()  # เริ่มจากหมายเลขที่มีอยู่แล้ว (Start from existing number)
timer = None                 # Timer object
start_time = 0               # เวลาเริ่มบันทึก (Recording start time)
elapsed_seconds = 0          # เวลาที่ผ่านไป (Elapsed time)

# ค่าแสดงผลปัจจุบัน - ใช้ตรวจสอบการเปลี่ยนแปลง
current_voltage_display = None
current_time_display = None
current_status_display = None

# ==============================================================================
# สีสำหรับแสดงผล (Display Colors)
# ==============================================================================
COLOR_WHITE = color565(255, 255, 255)
COLOR_YELLOW = color565(255, 251, 104)
COLOR_GREEN = color565(100, 255, 100)
COLOR_RED = color565(255, 100, 100)
COLOR_CYAN = color565(100, 255, 255)
COLOR_BLACK = color565(0, 0, 0)

# ==============================================================================
# ฟังก์ชันอ่านแรงดันไฟฟ้า (Read Voltage Function)
# ==============================================================================
def read_voltage_mv():
    """
    อ่านค่า ADC และแปลงเป็นมิลลิโวลต์ (mV)
    Read ADC value and convert to millivolts (mV)

    หมายเหตุวงจร LMC6482 (LMC6482 Circuit Note):
    - ค่าที่อ่านได้รวม offset 1650 mV จากวงจร op-amp แล้ว
    - The reading already includes 1650 mV offset from op-amp circuit

    ค่าที่คาดหวัง (Expected values):
    - pH 4:  ~1827 mV (กรด/Acidic - สูงกว่า offset)
    - pH 7:  ~1650 mV (กลาง/Neutral - ใกล้ offset)
    - pH 10: ~1473 mV (เบส/Basic - ต่ำกว่า offset)

    การคำนวณ (Calculation):
    - ADC 12-bit: 0-4095
    - แรงดันอ้างอิง: 3300 mV (3.3V)
    - voltage_mv = (ADC_value / 4095) x 3300

    Returns:
        float: แรงดันไฟฟ้าเป็น mV (Voltage in mV)
    """
    adc_value = adc.read()
    voltage_mv = adc_value * 3300 / 4095
    return voltage_mv

# ==============================================================================
# ฟังก์ชันแสดงผลหน้าจอ (Display Functions)
# ==============================================================================
def draw_header():
    """
    วาดหัวข้อหน้าจอ (Draw screen header)
    """
    # หัวข้อหลัก (Main title)
    title = "Response Time Test"
    title_x = 160 - int(font.measure_text(title, spacing=1) / 2)
    display.draw_text(title_x, 10, title, font, COLOR_WHITE,
                      background=COLOR_BLACK, landscape=False, spacing=1)

    # เส้นแบ่ง (Divider line)
    display.draw_hline(10, 40, 300, COLOR_YELLOW)

    # ป้ายกำกับ Voltage (Voltage label)
    label_v = "Voltage:"
    label_v_x = 160 - int(font.measure_text(label_v, spacing=1) / 2)
    display.draw_text(label_v_x, 55, label_v, font, COLOR_YELLOW,
                      background=COLOR_BLACK, landscape=False, spacing=1)

    # ป้ายกำกับ Time (Time label)
    label_t = "Time:"
    label_t_x = 160 - int(font.measure_text(label_t, spacing=1) / 2)
    display.draw_text(label_t_x, 130, label_t, font, COLOR_YELLOW,
                      background=COLOR_BLACK, landscape=False, spacing=1)

    # ป้ายกำกับ Status (Status label)
    label_s = "Status:"
    label_s_x = 160 - int(font.measure_text(label_s, spacing=1) / 2)
    display.draw_text(label_s_x, 195, label_s, font, COLOR_YELLOW,
                      background=COLOR_BLACK, landscape=False, spacing=1)


def show_voltage(voltage_mv):
    """
    แสดงค่าแรงดันไฟฟ้าบนจอ TFT (Display voltage on TFT)

    Args:
        voltage_mv: ค่าแรงดัน (mV)
    """
    global current_voltage_display

    mv_rounded = round(voltage_mv, 1)

    # อัปเดตเฉพาะเมื่อค่าเปลี่ยน (Update only when value changes)
    if mv_rounded != current_voltage_display:
        current_voltage_display = mv_rounded

        # ลบค่าเก่า (Clear old value)
        clear_text = "        "  # 8 spaces to clear
        clear_x = 160 - int(font.measure_text("9999.9 mV", spacing=1) / 2)
        display.draw_text(clear_x, 85, clear_text + " mV", font, COLOR_BLACK,
                          background=COLOR_BLACK, landscape=False, spacing=1)

        # แสดงค่าใหม่ (Draw new value)
        mv_text = f"{mv_rounded:.1f} mV"
        mv_x = 160 - int(font.measure_text(mv_text, spacing=1) / 2)
        display.draw_text(mv_x, 85, mv_text, font, COLOR_CYAN,
                          background=COLOR_BLACK, landscape=False, spacing=1)


def show_time(elapsed, total):
    """
    แสดงเวลาที่ผ่านไปบนจอ TFT (Display elapsed time on TFT)

    Args:
        elapsed: เวลาที่ผ่านไป (วินาที)
        total: เวลาทั้งหมด (วินาที)
    """
    global current_time_display

    time_key = (elapsed, total)

    # อัปเดตเฉพาะเมื่อค่าเปลี่ยน (Update only when value changes)
    if time_key != current_time_display:
        current_time_display = time_key

        # ลบค่าเก่า (Clear old value)
        clear_text = "           "  # spaces to clear
        clear_x = 160 - int(font.measure_text("99 / 99 s", spacing=1) / 2)
        display.draw_text(clear_x, 160, clear_text, font, COLOR_BLACK,
                          background=COLOR_BLACK, landscape=False, spacing=1)

        # แสดงค่าใหม่ (Draw new value)
        time_text = f"{elapsed} / {total} s"
        time_x = 160 - int(font.measure_text(time_text, spacing=1) / 2)
        display.draw_text(time_x, 160, time_text, font, COLOR_WHITE,
                          background=COLOR_BLACK, landscape=False, spacing=1)


def show_status(status_text, color, hint_text=""):
    """
    แสดงสถานะบนจอ TFT (Display status on TFT)

    Args:
        status_text: ข้อความสถานะ (Status text)
        color: สีของข้อความ (Text color)
        hint_text: ข้อความคำแนะนำ (Hint text)
    """
    global current_status_display

    status_key = (status_text, hint_text)

    # อัปเดตเฉพาะเมื่อค่าเปลี่ยน (Update only when value changes)
    if status_key != current_status_display:
        current_status_display = status_key

        # ลบสถานะเก่า (Clear old status)
        clear_text = "              "  # spaces to clear
        clear_x = 10
        display.draw_text(clear_x, 220, clear_text, font, COLOR_BLACK,
                          background=COLOR_BLACK, landscape=False, spacing=1)

        # แสดงสถานะใหม่ (Draw new status)
        status_x = 160 - int(font.measure_text(status_text, spacing=1) / 2)
        display.draw_text(status_x, 220, status_text, font, color,
                          background=COLOR_BLACK, landscape=False, spacing=1)

        # ลบคำแนะนำเก่า (Clear old hint)
        display.draw_text(10, 260, "                    ", font, COLOR_BLACK,
                          background=COLOR_BLACK, landscape=False, spacing=1)

        # แสดงคำแนะนำใหม่ (Draw new hint)
        if hint_text:
            hint_x = 160 - int(font.measure_text(hint_text, spacing=1) / 2)
            display.draw_text(hint_x, 260, hint_text, font, COLOR_WHITE,
                              background=COLOR_BLACK, landscape=False, spacing=1)

# ==============================================================================
# ฟังก์ชันบันทึกข้อมูล (Recording Functions)
# ==============================================================================
def record_data_callback(t):
    """
    Callback function สำหรับ Timer - บันทึกค่าทุกวินาที
    Timer callback - records value every second

    Args:
        t: Timer object (ไม่ได้ใช้แต่ต้องรับ parameter)
    """
    global data_buffer, recording, elapsed_seconds

    if not recording:
        return

    # เพิ่มตัวนับเวลา (Increment time counter)
    # ใช้ counter แทน time.time() เพราะแม่นยำกว่า
    # Using counter instead of time.time() for accuracy
    elapsed_seconds += 1

    # อ่านค่าแรงดันไฟฟ้า (Read voltage)
    voltage_mv = read_voltage_mv()

    # บันทึกข้อมูล (Record data)
    data_buffer.append((elapsed_seconds, voltage_mv))

    # แสดงผลบนจอ (Update display)
    show_voltage(voltage_mv)
    show_time(elapsed_seconds, RECORDING_DURATION_S)

    # แสดงใน console (Print to console)
    print(f"Time: {elapsed_seconds:3d} s | Voltage: {voltage_mv:7.1f} mV")

    # ตรวจสอบว่าครบเวลาหรือยัง (Check if duration reached)
    if elapsed_seconds >= RECORDING_DURATION_S:
        stop_recording()


def start_recording():
    """
    เริ่มการบันทึกข้อมูล (Start data recording)
    """
    global recording, data_buffer, start_time, recording_round, timer, elapsed_seconds

    if recording:
        return  # กำลังบันทึกอยู่แล้ว (Already recording)

    # รีเซ็ตตัวแปร (Reset variables)
    recording = True
    data_buffer = []
    start_time = time.time()
    elapsed_seconds = 0
    recording_round += 1

    # แสดงสถานะ (Show status)
    show_status("RECORDING", COLOR_RED, "[Press BTN1 to stop]")
    show_time(0, RECORDING_DURATION_S)

    print("")
    print("=" * 50)
    print(f"START Recording Round {recording_round}")
    print(f"Duration: {RECORDING_DURATION_S} seconds")
    print("=" * 50)

    # บันทึกข้อมูลแรกที่ t=0 ทันที (Record first data point at t=0 immediately)
    # Timer callback จะเริ่มทำงานหลังจาก 1 วินาที ดังนั้นต้องบันทึก t=0 ก่อน
    # Timer callback fires after 1 second, so we must record t=0 first
    voltage_mv = read_voltage_mv()
    data_buffer.append((0, voltage_mv))
    show_voltage(voltage_mv)
    print(f"Time:   0 s | Voltage: {voltage_mv:7.1f} mV")

    # เริ่ม Timer (Start timer) - จะบันทึก t=1, t=2, ... ต่อไป
    timer = Timer(0)
    timer.init(period=1000, mode=Timer.PERIODIC, callback=record_data_callback)


def stop_recording():
    """
    หยุดการบันทึกและบันทึกข้อมูลลงไฟล์ (Stop recording and save to file)
    """
    global recording, timer

    if not recording:
        return  # ไม่ได้กำลังบันทึก (Not recording)

    recording = False

    # หยุด Timer (Stop timer)
    if timer:
        timer.deinit()
        timer = None

    # บันทึกไฟล์ (Save file)
    save_data_to_csv()

    # แสดงสถานะ (Show status)
    show_status("STOPPED", COLOR_GREEN, "[Press BTN1 to start]")

    print("=" * 50)
    print(f"STOP Recording Round {recording_round}")
    print(f"Total data points: {len(data_buffer)}")
    print("=" * 50)
    print("")


def save_data_to_csv():
    """
    บันทึกข้อมูลลงไฟล์ CSV (Save data to CSV file)

    รูปแบบไฟล์ (File format):
    Time(s),Voltage(mV)
    0,1650.3
    1,1651.2
    ...

    นิสิตนำไฟล์ไปวิเคราะห์บนคอมพิวเตอร์เพื่อ:
    1. พล็อตกราฟ Time vs Voltage
    2. สังเกตการเปลี่ยนแปลงเมื่อย้ายหัววัดระหว่างบัฟเฟอร์
    3. วัดเวลาตอบสนองจากกราฟ
    """
    if not data_buffer:
        print("ไม่มีข้อมูลให้บันทึก (No data to save)")
        return

    filename = f"response_time_R{recording_round}.csv"

    try:
        with open(filename, 'w') as f:
            # เขียนหัวข้อคอลัมน์ (Write column headers)
            f.write("Time(s),Voltage(mV)\n")

            # เขียนข้อมูล (Write data)
            for time_s, voltage_mv in data_buffer:
                f.write(f"{time_s},{voltage_mv:.1f}\n")

        print(f"บันทึกสำเร็จ (Saved): {filename}")
        print(f"จำนวนข้อมูล (Data points): {len(data_buffer)}")

        # แสดงข้อมูลสรุป (Show summary)
        voltages = [v for _, v in data_buffer]
        print(f"Voltage Min: {min(voltages):.1f} mV")
        print(f"Voltage Max: {max(voltages):.1f} mV")

    except Exception as e:
        print(f"ข้อผิดพลาดในการบันทึก (Save error): {e}")

# ==============================================================================
# การจัดการปุ่มกด (Button Handling)
# ==============================================================================
# ตัวแปร debounce สำหรับปุ่ม (Debounce variable for button)
last_button_time = 0
DEBOUNCE_MS = 300  # หน่วงเวลา 300 ms เพื่อป้องกันการกดซ้ำ


def button_callback(pin):
    """
    Callback function เมื่อกดปุ่ม (Button press callback)

    จัดการ debounce และสลับสถานะการบันทึก
    Handle debounce and toggle recording state

    Args:
        pin: Pin object ที่เรียก callback
    """
    global last_button_time

    current_time = time.ticks_ms()

    # ตรวจสอบ debounce (Check debounce)
    if time.ticks_diff(current_time, last_button_time) < DEBOUNCE_MS:
        return

    last_button_time = current_time

    # ตรวจสอบว่าปุ่มถูกกด (Check if button is pressed)
    # หมายเหตุ: วงจร Schmitt trigger (74HC14D) ทำให้สัญญาณเป็น active-low
    if pin.value() == 0:
        if not recording:
            start_recording()
        else:
            stop_recording()

# ==============================================================================
# โปรแกรมหลัก (Main Program)
# ==============================================================================
print("")
print("=" * 60)
print("pH Probe Response Time Measurement")
print("การวัดเวลาตอบสนองของหัววัด pH")
print("=" * 60)
print("")
print("วิธีการทดลอง (Procedure):")
print("1. กดปุ่ม 1 เพื่อเริ่มบันทึก (Press Button 1 to start)")
print("2. จุ่มหัววัดใน pH 4 ประมาณ 15 วินาที (pH 4 for ~15s)")
print("3. ย้ายไป pH 7 ประมาณ 15 วินาที (pH 7 for ~15s)")
print("4. ย้ายไป pH 10 ประมาณ 15 วินาที (pH 10 for ~15s)")
print("5. โปรแกรมจะหยุดอัตโนมัติหลัง 45 วินาที (Auto-stop after 45s)")
print("")
print(f"ระยะเวลาบันทึก (Recording duration): {RECORDING_DURATION_S} s")
print(f"ค่า offset วงจร LMC6482: {OFFSET_MV:.0f} mV (pH 7 reference)")
print("")
print("ค่า mV ที่คาดหวัง (Expected mV values):")
print("  pH 4  (Acidic):  ~1800-1850 mV")
print("  pH 7  (Neutral): ~1600-1700 mV")
print("  pH 10 (Basic):   ~1450-1500 mV")
print("")
print("=" * 60)
print("")

# ตั้งค่า interrupt สำหรับปุ่มกด (Setup button interrupt)
button_1.irq(trigger=Pin.IRQ_FALLING, handler=button_callback)

# ล้างหน้าจอและวาดหัวข้อ (Clear display and draw header)
display.clear(COLOR_BLACK)
draw_header()

# แสดงสถานะเริ่มต้น (Show initial status)
show_status("STOPPED", COLOR_GREEN, "[Press BTN1 to start]")
show_time(0, RECORDING_DURATION_S)

# ==============================================================================
# Main Loop - อัปเดตหน้าจอ (Main Loop - Update display)
# ==============================================================================
try:
    while True:
        # อ่านและแสดงค่าแรงดันแบบ real-time (Read and show voltage in real-time)
        if not recording:
            voltage_mv = read_voltage_mv()
            show_voltage(voltage_mv)

        # หน่วงเวลาเล็กน้อย (Small delay)
        time.sleep_ms(200)

except KeyboardInterrupt:
    print("")
    print("หยุดโปรแกรม (Program stopped by user)")

finally:
    # ทำความสะอาด resources (Cleanup resources)
    if timer:
        timer.deinit()
        print("Timer released")

    # หยุด interrupt (Disable interrupt)
    button_1.irq(handler=None)
    print("Button interrupt disabled")

    print("Cleanup complete")
