# Self-Study Materials / เอกสารศึกษาด้วยตนเอง

**วิชา:** 2302311 Integrated Chemistry Laboratory I / ปฏิบัติการเคมีบูรณาการ 1
**หน่วยงาน:** ภาควิชาเคมี คณะวิทยาศาสตร์ จุฬาลงกรณ์มหาวิทยาลัย
**Department of Chemistry, Faculty of Science, Chulalongkorn University**

---

## วัตถุประสงค์ (Objectives)

เอกสารในโฟลเดอร์นี้เป็นสื่อเสริมสำหรับนิสิตที่ต้องการศึกษาด้วยตนเองหลังจากเรียนในชั้นเรียน
ช่วยเสริมความเข้าใจเรื่อง Object-Oriented Programming (OOP) และการเขียนโปรแกรมควบคุมฮาร์ดแวร์

These supplementary materials help students reinforce OOP concepts and hardware programming skills after the 3-hour class session. Study at your own pace to extend your learning.

---

## ความเชื่อมโยงกับเคมี (Chemistry Connections)

เนื้อหาในโฟลเดอร์นี้เชื่อมโยงกับการทดลองไทเทรชัน (titration) ดังนี้:

| แนวคิดการเขียนโปรแกรม | การประยุกต์ใช้ในเคมี |
|----------------------|---------------------|
| Class/คลาส | จำลองอุปกรณ์ เช่น pH sensor, pump, buzzer |
| Object/ออบเจกต์ | สร้างตัวแทนของอุปกรณ์จริงในโปรแกรม |
| Method/เมธอด | การทำงานของอุปกรณ์ เช่น `read_ph()`, `start_pump()` |
| ADC reading/การอ่านค่า ADC | แปลงแรงดันจาก pH probe เป็นค่า pH (สมการ Nernst) |
| PWM signal/สัญญาณ PWM | ควบคุมความเร็วปั๊มเพื่อเติมสารไทแทรนต์ (titrant) |
| Loop/ลูป | วัด pH อย่างต่อเนื่องระหว่างไทเทรชัน |
| Conditional/เงื่อนไข | ตรวจจับจุดสมมูล (equivalence point) |

---

## โครงสร้างโฟลเดอร์ (Folder Structure)

```
extras/
|-- 01_procedural/      # ตัวอย่างพื้นฐานแบบไม่ใช้ OOP (~1 ชั่วโมง)
|-- 02_advanced_oop/    # แนวคิด OOP ขั้นสูง (~2 ชั่วโมง)
|-- 03_exercises/       # แบบฝึกหัดเพิ่มเติม (~2-3 ชั่วโมง)
|-- 04_hardware/        # โมดูลเฉพาะฮาร์ดแวร์ (~1-2 ชั่วโมง)
|-- 05_reference/       # เอกสารอ้างอิง (ใช้เมื่อต้องการ)
```

---

## คำอธิบายแต่ละโฟลเดอร์ (Folder Descriptions)

### 01_procedural/ - ตัวอย่างพื้นฐานแบบไม่ใช้ OOP (Basic Procedural Examples)

**เวลาที่ใช้ศึกษา:** ประมาณ 1 ชั่วโมง
**Estimated study time:** ~1 hour

เหมาะสำหรับนิสิตที่ต้องการทำความเข้าใจพื้นฐานก่อนเรียน OOP
เปรียบเทียบกับการทำการทดลองแบบทำทีละขั้นตอน (step-by-step) โดยไม่จัดระบบ

| ไฟล์ | คำอธิบาย | ความเชื่อมโยงกับเคมี |
|------|----------|---------------------|
| `01_basic.py` | การกระพริบ LED แบบ Procedural | สัญญาณไฟบอกสถานะเครื่อง |
| `02_basic_loop.py` | การใช้ loop พื้นฐาน | การวัดค่าซ้ำๆ ระหว่างทดลอง |
| `02_toggle.py` | การสลับสถานะ LED | สลับโหมดการทำงาน |
| `03_Potentiometer.py` | การอ่านค่า ADC จาก Potentiometer | จำลองการอ่านค่าจากเซ็นเซอร์ |
| `03_twoLed.py` | ควบคุม LED สองดวง | แสดงสถานะปกติ/เตือน |
| `04_PWM_OUT.py` | การใช้ PWM output | ควบคุมความเร็วปั๊ม |
| `04_twoLed_infiniteLoop.py` | LED กับ infinite loop | การตรวจวัดอย่างต่อเนื่อง |

**แนะนำ:** ศึกษาก่อนเริ่มเรียน OOP เพื่อเข้าใจความแตกต่าง

---

### 02_advanced_oop/ - แนวคิด OOP ขั้นสูง (Advanced OOP Concepts)

**เวลาที่ใช้ศึกษา:** ประมาณ 2 ชั่วโมง
**Estimated study time:** ~2 hours

เนื้อหาขั้นสูงสำหรับเตรียมพร้อมสัปดาห์ที่ 2 เรียนรู้การใช้หลาย objects ทำงานร่วมกัน
เปรียบเสมือนการประกอบอุปกรณ์หลายชิ้นเข้าด้วยกันเป็นระบบไทเทรชันอัตโนมัติ

| ไฟล์ | คำอธิบาย | ความเชื่อมโยงกับเคมี |
|------|----------|---------------------|
| `02a_two_objects.py` | การใช้หลาย Objects ทำงานร่วมกัน | ใช้ LED + Button ด้วยกัน |
| `02b_adding_buzzer.py` | เพิ่ม Buzzer เข้ากับระบบ | เสียงเตือนเมื่อใกล้จุดสมมูล |
| `02c_titration_alert_system.py` | ระบบแจ้งเตือนสำหรับไทเทรชัน | ระบบตรวจจับจุดสมมูล |
| `02_buzzer_class.py` | คลาสสำหรับ Buzzer พร้อมเสียงต่างๆ | เสียงแจ้งเตือนหลายรูปแบบ |
| `03_preparing_for_week2.py` | เตรียมพร้อมสำหรับสัปดาห์ที่ 2 | พื้นฐาน Inheritance |
| `06_adc_sensor_class.py` | คลาสสำหรับเซ็นเซอร์ ADC | อ่านค่า pH probe |
| `06_comparing_styles.py` | เปรียบเทียบ Procedural vs OOP | เข้าใจข้อดีของ OOP |

**แนะนำ:** ศึกษาหลังจากเข้าใจเนื้อหาหลักของ Week 1 แล้ว

---

### 03_exercises/ - แบบฝึกหัดเพิ่มเติม (Additional Practice Exercises)

**เวลาที่ใช้ศึกษา:** ประมาณ 2-3 ชั่วโมง
**Estimated study time:** ~2-3 hours

แบบฝึกหัดสำหรับฝึกฝนเพิ่มเติม มีทั้งไฟล์โจทย์ (_starter) และเฉลย (_solution)
การฝึกเขียนโค้ดเหมือนกับการฝึกทำการทดลอง ยิ่งฝึกมากยิ่งชำนาญ

**ไฟล์อยู่ใน:** `03_exercises/exercises/`

| ไฟล์ | คำอธิบาย | ความเชื่อมโยงกับเคมี |
|------|----------|---------------------|
| `ex01_status_led_starter.py` | โจทย์: สร้างคลาส StatusLED | ไฟแสดงสถานะการทดลอง |
| `ex01_status_led_solution.py` | เฉลย: คลาส StatusLED | - |
| `ex02_potentiometer_starter.py` | โจทย์: สร้างคลาส Potentiometer | จำลอง pH sensor |
| `ex02_potentiometer_solution.py` | เฉลย: คลาส Potentiometer | - |
| `ex03_temp_sensor_starter.py` | โจทย์: สร้างคลาส TemperatureSensor | การแก้ค่า pH ตามอุณหภูมิ |
| `ex03_temp_sensor_solution.py` | เฉลย: คลาส TemperatureSensor | - |

**วิธีใช้:**
1. เปิดไฟล์ `_starter.py` และลองทำโจทย์
2. ถ้าติดปัญหา ดูคำใบ้ในไฟล์
3. เปรียบเทียบกับ `_solution.py` หลังจากทำเสร็จ

---

### 04_hardware/ - โมดูลเฉพาะฮาร์ดแวร์ (Hardware-Specific Modules)

**เวลาที่ใช้ศึกษา:** ประมาณ 1-2 ชั่วโมง
**Estimated study time:** ~1-2 hours

ตัวอย่างการใช้งานฮาร์ดแวร์เฉพาะทางบนบอร์ด TitraLab
แต่ละโฟลเดอร์ย่อยมีตัวอย่างสำหรับอุปกรณ์แต่ละชนิด

#### Buzzer/ - ลำโพง Buzzer

| ไฟล์ | คำอธิบาย | ความเชื่อมโยงกับเคมี |
|------|----------|---------------------|
| `01_song.py` | เล่นเพลงด้วย Buzzer | เสียงแจ้งเตือนจุดสมมูล |

#### DS18B20/ - เซ็นเซอร์อุณหภูมิ

| ไฟล์ | คำอธิบาย | ความเชื่อมโยงกับเคมี |
|------|----------|---------------------|
| `01_readTemp.py` | อ่านอุณหภูมิพื้นฐาน | วัดอุณหภูมิสารละลาย |
| `02_temp_sensor_class.py` | คลาส TemperatureSensor แบบละเอียด | ชดเชยค่า pH ตามอุณหภูมิ |

#### SDCard/ - การ์ด SD

| ไฟล์ | คำอธิบาย | ความเชื่อมโยงกับเคมี |
|------|----------|---------------------|
| `01_test_SDCard.py` | อ่าน-เขียนข้อมูลลง SD Card | บันทึกข้อมูล titration curve |

#### TFT/ - จอแสดงผล TFT

| ไฟล์ | คำอธิบาย | ความเชื่อมโยงกับเคมี |
|------|----------|---------------------|
| `01_test_display.py` | ทดสอบจอ TFT พื้นฐาน | แสดงค่า pH แบบ real-time |
| `02_temperature.py` | แสดงอุณหภูมิบนจอ | แสดงข้อมูลระหว่างทดลอง |

#### DAC/ - Digital-to-Analog Converter [Optional/เสริม]

**หมายเหตุ:** เนื้อหาเสริม ไม่จำเป็นต้องใช้ในหลักสูตรหลัก

| ไฟล์ | คำอธิบาย | ความเชื่อมโยงกับเคมี |
|------|----------|---------------------|
| `01_dac_basics.py` | พื้นฐาน DAC - กำหนดระดับแรงดัน | สัญญาณอ้างอิงสำหรับสอบเทียบ |
| `02_dac_waveform.py` | สร้างคลื่นสัญญาณต่างๆ | ใช้ใน Cyclic Voltammetry |

---

### 05_reference/ - เอกสารอ้างอิง (Reference Materials)

**เวลาที่ใช้ศึกษา:** ใช้เมื่อต้องการ
**Estimated study time:** Use as needed

เอกสารอ้างอิงสำหรับทบทวนและค้นหาข้อมูลเมื่อติดปัญหา

| ไฟล์ | คำอธิบาย |
|------|----------|
| `01_self_explained.py` | อธิบาย `self` อย่างละเอียด - หัวใจสำคัญของ OOP |
| `07_common_mistakes.py` | ข้อผิดพลาดที่พบบ่อยใน OOP พร้อมวิธีแก้ไข |

---

## ตารางอ้างอิงขา GPIO ของบอร์ด TitraLab (GPIO Pin Reference)

ขา GPIO มาตรฐานสำหรับบอร์ด TitraLab (อ้างอิงจาก `pins.py`):

### LEDs - ไฟ LED แสดงสถานะ

| ขา GPIO | ค่าคงที่ | คำอธิบาย |
|---------|---------|----------|
| GPIO2 | `LED_RED` | LED สีแดง (Red LED) |
| GPIO4 | `LED_GREEN` | LED สีเขียว (Green LED) |

### Buttons - ปุ่มกด (Input only, ไม่มี internal pull-up)

| ขา GPIO | ค่าคงที่ | คำอธิบาย |
|---------|---------|----------|
| GPIO34 | `BUTTON1` | ปุ่มกด 1 (Button 1) |
| GPIO35 | `BUTTON2` | ปุ่มกด 2 (Button 2) |
| GPIO39 | `BUTTON3` | ปุ่มกด 3 (Button 3) |

### Sensors - เซ็นเซอร์

| ขา GPIO | ค่าคงที่ | คำอธิบาย |
|---------|---------|----------|
| GPIO16 | `DS18B20_PIN` | เซ็นเซอร์อุณหภูมิ DS18B20 (OneWire) |
| GPIO25 | `PH_PIN` | เซ็นเซอร์ pH (ADC input) |
| GPIO32 | `POT1_PIN` | Potentiometer 1 (ADC) |
| GPIO33 | `POT2_PIN` | Potentiometer 2 (ADC) |

### Actuators - อุปกรณ์ขับเคลื่อน (PWM output)

| ขา GPIO | ค่าคงที่ | คำอธิบาย |
|---------|---------|----------|
| GPIO26 | `BUZZER_PIN` | ลำโพง Buzzer (PWM) |
| GPIO21 | `PUMP_PIN` | ปั๊มสำหรับไทเทรชัน (PWM) |

### SD Card (SoftSPI)

| ขา GPIO | ค่าคงที่ | คำอธิบาย |
|---------|---------|----------|
| GPIO19 | `SD_MISO` | SD Card MISO |
| GPIO23 | `SD_MOSI` | SD Card MOSI |
| GPIO18 | `SD_SCK` | SD Card Clock |
| GPIO5 | `SD_CS` | SD Card Chip Select |

### TFT Display (SPI Bus 1)

| ขา GPIO | ค่าคงที่ | คำอธิบาย |
|---------|---------|----------|
| GPIO14 | `TFT_SCK` | TFT SPI Clock |
| GPIO13 | `TFT_MOSI` | TFT SPI Data |
| GPIO27 | `TFT_DC` | TFT Data/Command |
| GPIO15 | `TFT_CS` | TFT Chip Select |
| GPIO0 | `TFT_RST` | TFT Reset |

**หมายเหตุ:**
- ห้ามใช้ GPIO16 สำหรับ LED (สงวนไว้สำหรับ DS18B20)
- ห้ามใช้ GPIO5 สำหรับ LED/PWM (สงวนไว้สำหรับ SD Card CS)

---

## เส้นทางการเรียนรู้ที่แนะนำ (Suggested Learning Path)

### สถานการณ์ที่ 1: ยังไม่เข้าใจ OOP (New to OOP)
```
1. เริ่มที่ 01_procedural/       --> ทำความเข้าใจโค้ดพื้นฐาน (~1 ชม.)
2. กลับไปศึกษา core/            --> เข้าใจแนวคิด OOP (~2 ชม.)
3. ลองทำ 03_exercises/          --> ฝึกฝนด้วยตนเอง (~2-3 ชม.)
```

### สถานการณ์ที่ 2: เข้าใจ OOP แล้ว ต้องการฝึกเพิ่ม (Want more practice)
```
1. ทำ 03_exercises/              --> ฝึกฝนทุกแบบฝึกหัด (~2-3 ชม.)
2. ศึกษา 02_advanced_oop/        --> เรียนรู้แนวคิดขั้นสูง (~2 ชม.)
```

### สถานการณ์ที่ 3: ต้องการสร้างโปรเจกต์ (Building a project)
```
1. ศึกษา 04_hardware/            --> เลือกฮาร์ดแวร์ที่ต้องการ (~1-2 ชม.)
2. ใช้ 05_reference/             --> ค้นหาข้อมูลเมื่อติดปัญหา
```

### สถานการณ์ที่ 4: เตรียมพร้อมสำหรับ Week 2 (Preparing for Week 2)
```
1. ทบทวน 05_reference/           --> แก้ไขข้อผิดพลาดที่พบบ่อย
2. ศึกษา 02_advanced_oop/        --> เข้าใจ Inheritance เบื้องต้น (~2 ชม.)
```

---

## ลิงก์ด่วนไปยังไฟล์สำคัญ (Quick Links to Key Files)

| หัวข้อ | ไฟล์ | คำอธิบาย |
|--------|------|----------|
| OOP Introduction | `../core/01_intro_oop.py` | แนะนำแนวคิด OOP |
| LED Class พื้นฐาน | `../core/02_led_class.py` | ตัวอย่าง Class แรก |
| Button Class | `../core/03_button_class.py` | การจัดการปุ่มกดแบบ OOP |
| Temperature Sensor | `../core/04_temp_sensor_class.py` | คลาสเซ็นเซอร์อุณหภูมิ |
| Display Basics | `../core/05_display_basics.py` | พื้นฐานการแสดงผลบนจอ TFT |
| Combined Example | `../core/06_combined_example.py` | ตัวอย่างการใช้หลายคลาสร่วมกัน |
| อธิบาย self | `./05_reference/01_self_explained.py` | เข้าใจ self อย่างลึกซึ้ง |
| ข้อผิดพลาดที่พบบ่อย | `./05_reference/07_common_mistakes.py` | หลีกเลี่ยงข้อผิดพลาด |
| เปรียบเทียบ Styles | `./02_advanced_oop/06_comparing_styles.py` | Procedural vs OOP |
| ADC Sensor Class | `./02_advanced_oop/06_adc_sensor_class.py` | การอ่านค่า ADC แบบ OOP |

---

## คำแนะนำสำหรับการศึกษาด้วยตนเอง (Self-Study Tips)

1. **ลงมือทำจริง** - อย่าแค่อ่านโค้ด ให้พิมพ์และรันโค้ดด้วยตัวเอง
2. **แก้ไขและทดลอง** - ลองเปลี่ยนค่าต่างๆ เพื่อดูผลลัพธ์
3. **ทำแบบฝึกหัดก่อนดูเฉลย** - พยายามทำเองก่อน แล้วค่อยเปรียบเทียบ
4. **จดบันทึก** - เขียนสิ่งที่เรียนรู้และข้อสงสัย
5. **ถามเมื่อไม่เข้าใจ** - ติดต่อผู้สอนหรือเพื่อนร่วมชั้น
6. **เชื่อมโยงกับเคมี** - นึกถึงการประยุกต์ใช้ในการทดลองไทเทรชัน

---

## ความช่วยเหลือเพิ่มเติม (Additional Help)

หากมีข้อสงสัย สามารถ:
- ศึกษา README.md หลักของ Week 1: `../README.md`
- ดูตัวอย่างใน `../core/`
- ติดต่อผู้สอนในคาบเรียนหรือช่องทางที่กำหนด

---

**ขอให้สนุกกับการเรียนรู้!**
**Happy Learning!**
