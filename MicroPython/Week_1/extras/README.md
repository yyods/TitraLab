# Self-Study Materials / เอกสารศึกษาด้วยตนเอง

## ภาพรวม (Overview)

เอกสารในโฟลเดอร์นี้เป็นสื่อเสริมสำหรับศึกษาด้วยตนเองหลังจากเรียนในชั้นเรียน 3 ชั่วโมง
สามารถเรียนรู้ตามความเร็วของตนเองได้

These materials supplement the 3-hour class session.
Study at your own pace to reinforce and extend your learning.

---

## โครงสร้างโฟลเดอร์ (Folder Structure)

```
extras/
|-- 01_procedural/      # ตัวอย่างพื้นฐานแบบไม่ใช้ OOP
|-- 02_advanced_oop/    # แนวคิด OOP ขั้นสูง
|-- 03_exercises/       # แบบฝึกหัดเพิ่มเติม
|-- 04_hardware/        # โมดูลเฉพาะฮาร์ดแวร์
|-- 05_reference/       # เอกสารอ้างอิง
```

---

## คำอธิบายแต่ละโฟลเดอร์ (Folder Descriptions)

### 01_procedural/ - ตัวอย่างพื้นฐานแบบไม่ใช้ OOP (Basic Examples WITHOUT OOP)

เหมาะสำหรับนักศึกษาที่ต้องการทำความเข้าใจพื้นฐานก่อนเรียน OOP

| ไฟล์ | คำอธิบาย |
|------|----------|
| `led_blink_basic.py` | การกระพริบ LED แบบ Procedural |
| `button_read_basic.py` | การอ่านค่าปุ่มกดพื้นฐาน |
| `potentiometer_adc.py` | การอ่านค่า ADC จาก Potentiometer |

**แนะนำ:** ศึกษาก่อนเริ่มเรียน OOP เพื่อเข้าใจความแตกต่าง

---

### 02_advanced_oop/ - แนวคิด OOP ขั้นสูง (Advanced OOP Concepts)

เนื้อหาขั้นสูงสำหรับเตรียมพร้อมสัปดาห์ที่ 2

| ไฟล์ | คำอธิบาย |
|------|----------|
| `multiple_objects.py` | การใช้หลาย Objects ทำงานร่วมกัน |
| `inheritance_preview.py` | ตัวอย่างเบื้องต้นของ Inheritance (เตรียมสำหรับ Week 2) |
| `adc_sensor_class.py` | คลาสสำหรับเซ็นเซอร์ ADC |
| `buzzer_class.py` | คลาสสำหรับ Buzzer พร้อมเสียงต่างๆ |

**แนะนำ:** ศึกษาหลังจากเข้าใจเนื้อหาหลักของ Week 1 แล้ว

---

### 03_exercises/ - แบบฝึกหัดเพิ่มเติม (Additional Practice Exercises)

แบบฝึกหัดสำหรับฝึกฝนเพิ่มเติม มีทั้งไฟล์โจทย์และเฉลย

| ไฟล์ | คำอธิบาย |
|------|----------|
| `ex01_status_led_starter.py` | โจทย์: สร้างคลาส StatusLED |
| `ex01_status_led_solution.py` | เฉลย: คลาส StatusLED |
| `ex02_potentiometer_starter.py` | โจทย์: สร้างคลาส Potentiometer |
| `ex02_potentiometer_solution.py` | เฉลย: คลาส Potentiometer |
| `ex03_temp_sensor_starter.py` | โจทย์: สร้างคลาส TemperatureSensor |
| `ex03_temp_sensor_solution.py` | เฉลย: คลาส TemperatureSensor |

**วิธีใช้:**
1. เปิดไฟล์ `_starter.py` และลองทำโจทย์
2. ถ้าติดปัญหา ดูคำใบ้ในไฟล์
3. เปรียบเทียบกับ `_solution.py` หลังจากทำเสร็จ

---

### 04_hardware/ - โมดูลเฉพาะฮาร์ดแวร์ (Hardware-Specific Modules)

ตัวอย่างการใช้งานฮาร์ดแวร์เฉพาะทาง

| ไฟล์ | คำอธิบาย |
|------|----------|
| `ds18b20_detailed.py` | ตัวอย่างละเอียดสำหรับเซ็นเซอร์อุณหภูมิ DS18B20 |
| `sdcard_usage.py` | การอ่าน-เขียนข้อมูลลง SD Card |
| `tft_advanced.py` | การแสดงผลขั้นสูงบนจอ TFT |
| `buzzer_sounds.py` | เสียงและเพลงต่างๆ สำหรับ Buzzer |

**แนะนำ:** ใช้เมื่อต้องการสร้างโปรเจกต์ที่ใช้ฮาร์ดแวร์เหล่านี้

---

### 05_reference/ - เอกสารอ้างอิง (Reference Materials)

เอกสารอ้างอิงสำหรับทบทวนและค้นหาข้อมูล

| ไฟล์ | คำอธิบาย |
|------|----------|
| `common_mistakes.py` | ข้อผิดพลาดที่พบบ่อยใน OOP พร้อมตัวอย่าง |
| `self_explained.py` | อธิบาย `self` อย่างละเอียด |
| `procedural_vs_oop.py` | เปรียบเทียบ Procedural vs OOP |

---

## เส้นทางการเรียนรู้ที่แนะนำ (Suggested Learning Path)

### สถานการณ์ที่ 1: ยังไม่เข้าใจ OOP
```
1. เริ่มที่ 01_procedural/  --> ทำความเข้าใจโค้ดพื้นฐาน
2. กลับไปศึกษา 00_OOP_Basics/ --> เข้าใจแนวคิด OOP
3. ลองทำ 03_exercises/       --> ฝึกฝนด้วยตนเอง
```

### สถานการณ์ที่ 2: เข้าใจ OOP แล้ว ต้องการฝึกเพิ่ม
```
1. ทำ 03_exercises/          --> ฝึกฝนทุกแบบฝึกหัด
2. ศึกษา 02_advanced_oop/    --> เรียนรู้แนวคิดขั้นสูง
```

### สถานการณ์ที่ 3: ต้องการสร้างโปรเจกต์
```
1. ศึกษา 04_hardware/        --> เลือกฮาร์ดแวร์ที่ต้องการ
2. ใช้ 05_reference/         --> ค้นหาข้อมูลเมื่อติดปัญหา
```

### สถานการณ์ที่ 4: เตรียมพร้อมสำหรับ Week 2
```
1. ทบทวน 05_reference/       --> แก้ไขข้อผิดพลาดที่พบบ่อย
2. ศึกษา 02_advanced_oop/    --> เข้าใจ Inheritance เบื้องต้น
```

---

## ลิงก์ด่วนไปยังไฟล์สำคัญ (Quick Links to Key Files)

| หัวข้อ | ไฟล์ | คำอธิบาย |
|--------|------|----------|
| เปรียบเทียบ Procedural vs OOP | `../01_Blink/06_comparing_styles.py` | เห็นความแตกต่างชัดเจน |
| LED Class พื้นฐาน | `../01_Blink/05_led_class.py` | ตัวอย่าง Class แรก |
| Button Class | `../02_Button/05_button_class.py` | การจัดการปุ่มกดแบบ OOP |
| ADC Sensor Class | `../02_Button/06_adc_sensor_class.py` | การอ่านค่า ADC แบบ OOP |
| Buzzer Class | `../06_Buzzer/02_buzzer_class.py` | การควบคุม Buzzer แบบ OOP |
| Temperature Sensor | `../03_DS18B20/02_temp_sensor_class.py` | คลาสเซ็นเซอร์อุณหภูมิ |
| ข้อผิดพลาดที่พบบ่อย | `../01_Blink/07_common_mistakes.py` | หลีกเลี่ยงข้อผิดพลาด |
| อธิบาย self | `../00_OOP_Basics/01_self_explained.py` | เข้าใจ self อย่างลึกซึ้ง |

---

## คำแนะนำสำหรับการศึกษาด้วยตนเอง (Self-Study Tips)

1. **ลงมือทำจริง** - อย่าแค่อ่านโค้ด ให้พิมพ์และรันโค้ดด้วยตัวเอง
2. **แก้ไขและทดลอง** - ลองเปลี่ยนค่าต่างๆ เพื่อดูผลลัพธ์
3. **ทำแบบฝึกหัดก่อนดูเฉลย** - พยายามทำเองก่อน แล้วค่อยเปรียบเทียบ
4. **จดบันทึก** - เขียนสิ่งที่เรียนรู้และข้อสงสัย
5. **ถามเมื่อไม่เข้าใจ** - ติดต่อผู้สอนหรือเพื่อนร่วมชั้น

---

## ความช่วยเหลือเพิ่มเติม (Additional Help)

หากมีข้อสงสัย สามารถ:
- ศึกษา README.md หลักของ Week 1: `../README.md`
- ดูตัวอย่างใน `../00_OOP_Basics/`
- ติดต่อผู้สอนในคาบเรียนหรือช่องทางที่กำหนด

---

**ขอให้สนุกกับการเรียนรู้!**
**Happy Learning!**
