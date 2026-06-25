# ==============================================================================
# titration.py - เคมีของการไทเทรชัน (Titration Chemistry — board-independent)
# ==============================================================================
# โมดูลนี้คือ "ส่วนเคมีที่นิสิตแก้ไขได้" ของบทเรียน ไม่มีโค้ดควบคุมฮาร์ดแวร์เลย
# This module is the EDITABLE CHEMISTRY of the lesson. It contains NO hardware
# driver code — ฮาร์ดแวร์ทั้งหมดเป็นของเฟิร์มแวร์ผ่าน scilabpro helpers (slp.*).
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. หาจุดสมมูล (equivalence point) ด้วยวิธีอนุพันธ์ |dpH/dV| สูงสุด
#   2. คำนวณความเข้มข้นที่ไม่ทราบค่าด้วยกฎ C1V1 = C2V2 (พร้อมอัตราส่วนสโตอิชิโอเมตรี)
#   3. เข้าใจว่ากราฟไทเทรชันรูป S บอกอะไรเกี่ยวกับปฏิกิริยากรด-เบส
#
# หลักการทางเคมี (Chemistry Principles):
#   - จุดสมมูลคือจุดที่กรดและเบสทำปฏิกิริยาพอดี (โมลเท่ากันตามสโตอิชิโอเมตรี)
#   - ที่จุดสมมูล การเปลี่ยนแปลง pH ต่อปริมาตร (dpH/dV) มีค่าสูงสุด
#   - C(analyte) = ratio * C(titrant) * V(equivalence) / V(sample)
#
# หมายเหตุการอ่าน + การนำผลสอบเทียบไปใช้ (pH read + APPLYING student calibration):
#   *** หัวใจของบทเรียน (load-bearing pedagogy) ***
#   หัววัด pH ของแต่ละบอร์ดต่างกัน นิสิตจึงสอบเทียบเองใน Week_2 บทเรียนนี้ "ใช้"
#   ผลสอบเทียบนั้น (slope_m, intercept_b) โดยตรงและเห็นได้ชัด ไม่เรียก slp.ph_probe()
#   (ซึ่งจะไปใช้ calibration.json ของแอป/เฟิร์มแวร์ ไม่ใช่ของนิสิต) แทนที่ด้วย:
#     1) อ่าน ADC ดิบจากไดรเวอร์เฟิร์มแวร์ (slp.read_analog('PH'))
#     2) แปลง raw -> mV ด้วยตัวประกอบเดียวกับ Week_2 (exp.RAW_TO_MV = 3300/4095)
#     3) ใช้สมการสอบเทียบของนิสิต: pH = slope_m * mV + intercept_b
#     4) เก็บค่ามัธยฐาน (median-of-N) เพื่อลดสัญญาณรบกวน ADC
#   This module reads RAW ADC from the firmware driver and APPLIES the student's
#   Week_2 fit (pH = slope_m*mV + intercept_b) in visible Python — never ph_probe().
# ==============================================================================

import scilabpro as slp

import experiment as exp


# ==============================================================================
# การอ่าน pH แบบมัธยฐาน (Median pH read) — ลดสัญญาณรบกวน ADC แบบง่าย
# ==============================================================================
# ช่วง pH ที่เป็นไปได้ทางเคมี (chemically plausible pH window, 0..14)
PH_MIN = 0.0
PH_MAX = 14.0


def load_ph_calibration(path=None):
    """
    อ่านผลสอบเทียบ pH ที่นิสิตทำเองใน Week_2 (Load student Week_2 pH calibration)

    อ่านไฟล์ /workspace/data/ph_calibration.txt ที่ Week_2 02_calibration_3point.py
    เขียนไว้ รูปแบบ (เหมือนกันทั้งสองสัปดาห์):
        slope_m,intercept_b,r_squared,cal_temp
        -0.016911,34.9800,0.9985,25.20
    บรรทัดแรกเป็นหัวคอลัมน์ บรรทัดที่สองเป็นค่า — เราอ่านสองค่าแรก (slope_m, b)
    Reads the file Week_2 wrote; we take slope_m and intercept_b from the data row.

    Args:
        path: เส้นทางไฟล์สอบเทียบ (default = exp.PH_CAL_PATH)

    Returns:
        tuple: (slope_m, intercept_b) — สมการ pH = slope_m * mV + intercept_b

    Raises:
        RuntimeError: ถ้าไฟล์หาย/อ่านไม่ได้/รูปแบบผิด (missing/unreadable/malformed)
                      — ผู้เรียกต้องแจ้งให้นิสิตไปรันการสอบเทียบ Week_2 ก่อน
    """
    if path is None:
        path = exp.PH_CAL_PATH
    try:
        with open(path, 'r') as f:
            lines = f.readlines()
    except OSError:
        # ไฟล์สอบเทียบหาย — นิสิตยังไม่ได้สอบเทียบ pH ใน Week_2
        # Calibration file missing — student has not run the Week_2 pH calibration.
        raise RuntimeError('ph_calibration_file_missing')

    # หาบรรทัดข้อมูล (ข้ามหัวคอลัมน์/บรรทัดว่าง) — find the numeric data row
    for line in lines:
        line = line.strip()
        if not line or line.startswith('slope_m'):
            continue
        parts = line.split(',')
        if len(parts) < 2:
            continue
        try:
            slope_m = float(parts[0])
            intercept_b = float(parts[1])
        except ValueError:
            continue
        return slope_m, intercept_b

    # ไม่พบบรรทัดค่าที่ใช้ได้ (no valid data row found)
    raise RuntimeError('ph_calibration_file_malformed')


def load_flow_rate(path=None):
    """
    อ่านอัตราการไหลที่นิสิตสอบเทียบเองใน Week_2 (Load student Week_2 flow rate)

    อ่านไฟล์ /workspace/data/flow_calibration.txt ที่ Week_2
    01_flow_rate_calibration.py เขียนไว้ บรรทัดสุดท้ายคือ:
        flow_rate=0.2772
    (mL/s) — เราข้ามบรรทัดคอมเมนต์ (#) แล้วอ่านค่าหลัง 'flow_rate='
    Reads the file Week_2 wrote; takes the value after 'flow_rate='.

    Args:
        path: เส้นทางไฟล์สอบเทียบ (default = exp.FLOW_CAL_PATH)

    Returns:
        float: อัตราการไหล (mL/s) > 0

    Raises:
        RuntimeError: ถ้าไฟล์หาย/อ่านไม่ได้/รูปแบบผิด/ค่าผิด (missing/malformed)
                      — ผู้เรียกต้องแจ้งให้นิสิตไปรันการสอบเทียบ flow ใน Week_2 ก่อน
    """
    if path is None:
        path = exp.FLOW_CAL_PATH
    try:
        with open(path, 'r') as f:
            lines = f.readlines()
    except OSError:
        # ไฟล์สอบเทียบหาย — นิสิตยังไม่ได้สอบเทียบอัตราการไหลใน Week_2
        # Flow calibration file missing — student has not run the Week_2 flow calibration.
        raise RuntimeError('flow_calibration_file_missing')

    for line in lines:
        line = line.strip()
        # ข้ามคอมเมนต์และบรรทัดว่าง (skip comment/blank lines Week_2 writes)
        if not line or line.startswith('#'):
            continue
        if line.startswith('flow_rate='):
            try:
                flow_rate = float(line.split('=')[1])
            except (ValueError, IndexError):
                continue
            if flow_rate > 0:
                return flow_rate

    # ไม่พบ flow_rate ที่ใช้ได้ (no valid flow_rate found)
    raise RuntimeError('flow_calibration_file_malformed')


def pump_time_ms_for_volume(volume_ml, flow_rate_ml_s, max_on_ms):
    """
    คำนวณเวลาเปิดปั๊ม (ms) จากปริมาตรเป้าหมายและอัตราการไหลที่สอบเทียบ
    Compute pump-on time (ms) from target volume and the calibrated flow rate.

    *** closed-loop บนปริมาตร (closed-loop on volume) ***
    หลักการ (Model — same as Week_2 pump validation):
        pump_time_s  = volume_ml / flow_rate_ml_s
        pump_time_ms = round(pump_time_s * 1000)
    เวลาที่ได้จะถูก "clamp" ไม่ให้เกิน max_on_ms เพื่อความปลอดภัย (กันปั๊มค้างเปิด
    หากไฟล์สอบเทียบให้ flow_rate ต่ำผิดปกติ เช่น ปั๊มเกือบตัน)
    The result is clamped to max_on_ms as a hard safety ceiling.

    Args:
        volume_ml: ปริมาตรที่ต้องการจ่ายต่อ step (mL per dose step)
        flow_rate_ml_s: อัตราการไหลที่สอบเทียบ (mL/s, > 0)
        max_on_ms: เพดานเวลาเปิดปั๊มเพื่อความปลอดภัย (clamp ceiling, ms)

    Returns:
        int: เวลาเปิดปั๊ม (ms) ในช่วง 1..max_on_ms
    """
    # ป้องกันหารด้วยศูนย์ (guard divide-by-zero; loader already enforces > 0)
    if flow_rate_ml_s <= 0:
        return max_on_ms
    pump_ms = int(round(volume_ml / flow_rate_ml_s * 1000))
    # clamp เพดานความปลอดภัย (clamp to the hard safety ceiling)
    if pump_ms > max_on_ms:
        pump_ms = max_on_ms
    # อย่างน้อย 1 ms เพื่อให้สั่งเปิดปั๊มได้จริง (at least 1 ms so the pump actually fires)
    if pump_ms < 1:
        pump_ms = 1
    return pump_ms


def read_ph_median(slope_m, intercept_b, samples=5, gap_ms=200):
    """
    อ่าน ADC ดิบ -> mV -> ใช้สมการสอบเทียบของนิสิต -> คืนค่า pH มัธยฐาน
    Read RAW ADC, convert to mV, APPLY the student fit, return the median pH.

    ขั้นตอน (Steps — calibration APPLICATION made visible):
      1. อ่าน ADC ดิบ N ครั้งจากไดรเวอร์เฟิร์มแวร์ (raw counts 0..4095)
      2. raw -> mV ด้วย exp.RAW_TO_MV (= 3300/4095 ตรงกับ Week_2)
      3. pH = slope_m * mV + intercept_b  (สมการสอบเทียบของนิสิตเอง)
      4. จำกัด (clamp) ค่า pH ให้อยู่ 0..14 แล้วคืนค่ามัธยฐาน

    ใช้มัธยฐานแทนค่าเฉลี่ยเพราะทนต่อค่าผิดปกติ (outlier) จาก ADC ได้ดีกว่า
    Median is robust against occasional ADC spikes (better than mean here).

    Args:
        slope_m: ความชันสอบเทียบ (pH/mV) จาก Week_2 (student calibration slope)
        intercept_b: จุดตัดแกน pH จาก Week_2 (student calibration intercept)
        samples: จำนวนครั้งที่อ่าน (number of reads; coerced to an odd int >= 1)
        gap_ms:  หน่วงระหว่างการอ่าน (ms between reads)

    Returns:
        float: ค่า pH มัธยฐาน ในช่วง 0..14 (median student-calibrated pH, clamped)
    """
    import time
    # อ่านอย่างน้อย 1 ครั้ง และใช้จำนวนคี่เพื่อให้มัธยฐานเป็นค่าจริงค่าเดียว
    # At least 1 read; force odd N so the median is a single observed value.
    n = int(samples)
    if n < 1:
        n = 1
    if n % 2 == 0:
        n += 1

    readings = []
    for i in range(n):
        # อ่าน ADC ดิบจากไดรเวอร์เฟิร์มแวร์ (raw ADC counts from the firmware driver)
        # ไดรเวอร์เป็นของเฟิร์มแวร์ (raw read) — การสอบเทียบเป็น Python ที่นิสิตเห็น
        raw = _read_ph_raw()
        # raw -> mV ด้วยตัวประกอบเดียวกับ Week_2 (same factor as Week_2)
        mv = raw * exp.RAW_TO_MV
        # ใช้สมการสอบเทียบของนิสิต: pH = slope_m * mV + intercept_b
        value = slope_m * mv + intercept_b
        # จำกัดค่าให้อยู่ในช่วงที่เป็นไปได้ทางเคมี (clamp to 0..14) กันค่าทำลายอนุพันธ์
        if value < PH_MIN:
            value = PH_MIN
        elif value > PH_MAX:
            value = PH_MAX
        readings.append(value)
        if i < n - 1:
            time.sleep_ms(gap_ms)
    readings.sort()
    return readings[len(readings) // 2]


def _read_ph_raw():
    """
    อ่านค่า ADC ดิบของหัววัด pH จากไดรเวอร์เฟิร์มแวร์ (read RAW pH ADC counts)

    ใช้ slp.read_analog('PH') เป็นหลัก (ไดรเวอร์ raw ADC ตาม routing profile)
    ถ้าเฟิร์มแวร์รุ่นนั้นไม่มี read_analog จะถอยไปใช้
    slp.pin(exp.PH_PROBE_PIN, input=True).analog_read() ซึ่งให้ค่า raw เช่นกัน
    Prefer slp.read_analog('PH'); fall back to the pin's analog_read().

    Returns:
        int: ค่า ADC ดิบ 0..4095 (raw 12-bit ADC counts)
    """
    if hasattr(slp, 'read_analog'):
        return slp.read_analog(exp.PH_ENDPOINT)
    # ทางเลือกสำรอง: อ่าน ADC ดิบผ่าน pin helper (fallback raw read via pin helper)
    return slp.pin(exp.PH_PROBE_PIN, input=True).analog_read()


# ==============================================================================
# คลาสวิเคราะห์การไทเทรชัน (Titration analysis — pure-Python chemistry)
# ==============================================================================
class TitrationAnalysis:
    """
    เก็บข้อมูล (ปริมาตร, pH) และวิเคราะห์หาจุดสมมูล + ความเข้มข้นที่ไม่ทราบค่า
    Collects (volume, pH) points and analyzes equivalence point + unknown
    concentration. คลาสนี้ไม่ยุ่งกับฮาร์ดแวร์เลย ทดสอบได้บนเครื่องคอมพิวเตอร์

    การใช้งาน (Usage):
        ta = TitrationAnalysis()
        ta.add_point(0.0, 2.1)
        ta.add_point(0.2, 2.2)
        ...
        eq = ta.detect_equivalence_point()          # (volume, pH) หรือ None
        c  = ta.calculate_unknown_concentration(...) # mol/L หรือ None
    """

    def __init__(self):
        # รายการจุดข้อมูล (volume_ml, ph) — ข้อมูลดิบของกราฟไทเทรชัน
        self.points = []            # list of (volume_ml, ph)
        self.equivalence_point = None   # (volume_ml, ph) ที่จุดสมมูล
        self.max_derivative = 0.0       # |dpH/dV| สูงสุดที่พบ

    def add_point(self, volume_ml, ph):
        """เพิ่มจุดข้อมูล (Add a (volume, pH) data point to the curve)."""
        self.points.append((float(volume_ml), float(ph)))

    def reset(self):
        """ล้างข้อมูลทั้งหมดเพื่อเริ่มการไทเทรตใหม่ (Clear all collected data)."""
        self.points = []
        self.equivalence_point = None
        self.max_derivative = 0.0

    def derivative_at(self, index):
        """
        คำนวณอนุพันธ์ dpH/dV ณ จุดที่กำหนด (Compute dpH/dV at a given index)

        สูตร (Formula): dpH/dV = (pH[i] - pH[i-1]) / (V[i] - V[i-1])

        Returns:
            float: ค่าอนุพันธ์ (0.0 ถ้า index ไม่ถูกต้องหรือ ΔV เล็กเกินไป)
        """
        if index < 1 or index >= len(self.points):
            return 0.0
        v_now, ph_now = self.points[index]
        v_prev, ph_prev = self.points[index - 1]
        delta_v = v_now - v_prev
        # ป้องกันหารด้วยศูนย์ — threshold 0.01 mL ปลอดภัยจาก floating-point error
        # Guard against divide-by-zero; 0.01 mL is safe vs float noise.
        if abs(delta_v) < 0.01:
            return 0.0
        return (ph_now - ph_prev) / delta_v

    def detect_equivalence_point(self):
        """
        หาจุดสมมูลด้วยวิธีอนุพันธ์ (Detect equivalence point by max |dpH/dV|)

        หลักการ (Principle): จุดสมมูลคือจุดที่ |dpH/dV| สูงสุด เพราะ pH เปลี่ยน
        อย่างรวดเร็วที่สุดเมื่อกรด/เบสทำปฏิกิริยาหมดพอดี

        จุดสำคัญทางตัวเลข (Numerical note):
            derivative_at(i) คือความชันของ "ช่วง" ระหว่างจุด i-1 กับ i ดังนั้น
            ความชันนั้นเป็นตัวแทนของ "จุดกึ่งกลางช่วง" ไม่ใช่ปลายช่วง การคืนปลาย
            ช่วง (จุด i) จะลำเอียงสูงไปครึ่ง step เราจึงประมาณจุดสมมูลด้วย
            "เซนทรอยด์ถ่วงน้ำหนักด้วยความชัน" ของกึ่งกลางช่วงที่ชันสุดและช่วง
            ข้างเคียง ซึ่ง (ก) ไม่ลำเอียง (ข) จัดการกรณีจุดสมมูลตกพอดีบนจุดกริด
            (ความชันสองช่วงเท่ากัน) ได้ และ (ค) เข้าใกล้คำตอบ spline-argmax ของ
            เครื่องมือ EquivPoint บนเดสก์ท็อป
            A backward difference at i is the slope of segment (i-1, i), which
            belongs to that segment's MIDPOINT — returning point i alone biases
            the volume high by half a dose step. We instead estimate the
            equivalence volume as the slope-magnitude-weighted centroid of the
            steepest segment's midpoint and its two neighbours: this is
            unbiased, handles the on-grid tie (two equal-slope segments), and
            approximates the desktop EquivPoint spline-argmax inflection.

        Returns:
            tuple | None: (volume_ml, ph) ที่จุดสมมูล หรือ None ถ้าข้อมูลไม่พอ.
                          หมายเหตุ: ค่า pH ที่คืนเป็นค่าประมาณ (pH เปลี่ยนหลาย
                          หน่วยภายใน 1 step) — ใช้ volume เป็นหลักในการคำนวณ
                          ความเข้มข้น.
        """
        if len(self.points) < 3:
            return None

        # หาช่วงที่ชันที่สุด (find the steepest segment by max |dpH/dV|)
        max_abs = 0.0
        eq_index = -1
        for i in range(1, len(self.points)):
            d = abs(self.derivative_at(i))
            # ใช้ > (strict) เพื่อให้ผลแน่นอน: เมื่อความชันเท่ากัน เลือกช่วงแรก
            # (ปริมาตรต่ำกว่า) เป็นพฤติกรรมที่กำหนดไว้ — deterministic on ties.
            if d > max_abs:
                max_abs = d
                eq_index = i

        if eq_index < 0:
            return None

        # max_derivative เก็บความชันสูงสุดจริง (the teaching concept: peak |dpH/dV|)
        self.max_derivative = max_abs

        # ประมาณปริมาตร/pH จุดสมมูลด้วยเซนทรอยด์ถ่วงน้ำหนักด้วยความชัน
        # over the steepest segment and its immediate neighbours.
        lo = eq_index - 1 if eq_index - 1 >= 1 else 1
        hi = eq_index + 1 if eq_index + 1 <= len(self.points) - 1 else len(self.points) - 1
        num_v = 0.0
        num_ph = 0.0
        den = 0.0
        for i in range(lo, hi + 1):
            w = abs(self.derivative_at(i))
            v_mid = (self.points[i - 1][0] + self.points[i][0]) / 2.0
            ph_mid = (self.points[i - 1][1] + self.points[i][1]) / 2.0
            num_v += w * v_mid
            num_ph += w * ph_mid
            den += w

        if den > 0.0:
            eq_volume = num_v / den
            eq_ph = num_ph / den
        else:
            # ทุกช่วงแบน (degenerate) — คืนกึ่งกลางช่วงที่เลือกไว้
            eq_volume = (self.points[eq_index - 1][0] + self.points[eq_index][0]) / 2.0
            eq_ph = (self.points[eq_index - 1][1] + self.points[eq_index][1]) / 2.0

        self.equivalence_point = (eq_volume, eq_ph)
        return self.equivalence_point

    def calculate_unknown_concentration(self, titrant_conc_m, sample_volume_ml,
                                        ratio=1.0, equivalence_volume_ml=None):
        """
        คำนวณความเข้มข้นที่ไม่ทราบค่าด้วยกฎ C1V1 = C2V2
        Calculate the unknown analyte concentration via C1V1 = C2V2.

        หลักการทางเคมี (Chemistry):
            ที่จุดสมมูล: mol(titrant) * ratio = mol(analyte)
            C_titrant * V_eq * ratio = C_analyte * V_sample
            =>  C_analyte = ratio * C_titrant * V_eq / V_sample
        โดย ratio = อัตราส่วนโมล analyte:titrant (1.0 สำหรับกรดแก่-เบสแก่ 1:1)

        Args:
            titrant_conc_m: ความเข้มข้นไทแทรนต์ที่ทราบ (mol/L)
            sample_volume_ml: ปริมาตรสารตัวอย่าง (mL)
            ratio: อัตราส่วนสโตอิชิโอเมตรี mol analyte ต่อ mol titrant
            equivalence_volume_ml: ปริมาตรที่จุดสมมูล (mL); ถ้า None จะใช้ค่าที่
                                   ตรวจพบจาก detect_equivalence_point()

        Returns:
            float | None: ความเข้มข้นที่ไม่ทราบค่า (mol/L) หรือ None ถ้าหาจุดสมมูลไม่ได้
        """
        # ใช้ปริมาตรจุดสมมูลที่ตรวจพบ ถ้าไม่ได้ระบุมาโดยตรง
        if equivalence_volume_ml is None:
            if self.equivalence_point is None:
                self.detect_equivalence_point()
            if self.equivalence_point is None:
                return None
            equivalence_volume_ml = self.equivalence_point[0]

        if sample_volume_ml <= 0:
            return None

        # C_analyte = ratio * C_titrant * V_eq / V_sample
        return ratio * titrant_conc_m * equivalence_volume_ml / sample_volume_ml

    def curve(self):
        """คืนข้อมูลกราฟ (Return (volumes, phs) lists for plotting/inspection)."""
        volumes = [p[0] for p in self.points]
        phs = [p[1] for p in self.points]
        return volumes, phs
