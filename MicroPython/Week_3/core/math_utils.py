# ==============================================================================
# math_utils.py - คลาสคำนวณทางคณิตศาสตร์สำหรับ TitraLab
# (Mathematical Utility Classes for TitraLab)
# ==============================================================================
# โมดูลนี้รวบรวมฟังก์ชันและคลาสทางคณิตศาสตร์สำหรับการวิเคราะห์ข้อมูล
# This module contains mathematical functions and classes for data analysis
#
# วัตถุประสงค์การเรียนรู้ (Learning Objectives):
#   1. เข้าใจหลักการ Linear Regression และการคำนวณ R-squared
#   2. เรียนรู้การประมวลผลข้อมูลสำหรับการสอบเทียบ
#   3. ประยุกต์ใช้สถิติเบื้องต้นในการวิเคราะห์คุณภาพข้อมูล
#
# หลักการ Linear Regression:
#   สมการเส้นตรง: y = mx + b
#   โดย:
#   - m (slope) = covariance(x,y) / variance(x)
#   - b (intercept) = mean(y) - m * mean(x)
#   - R-squared = 1 - (SS_residual / SS_total)
#
# ==============================================================================


class LinearRegression:
    """
    คลาสคำนวณ Linear Regression สำหรับการสอบเทียบ
    (Linear Regression class for calibration)

    ใช้สำหรับ:
        - สอบเทียบ pH sensor (3-point calibration)
        - คำนวณความสัมพันธ์เชิงเส้นระหว่าง mV (x) และ pH (y)
        - ประเมินคุณภาพการสอบเทียบด้วย R-squared

    หลักการทางสถิติ (Statistical Principles):
        Linear regression หาเส้นตรงที่ fit ข้อมูลได้ดีที่สุด
        โดยใช้วิธี least squares minimization

        R-squared (R2) = สัดส่วนของความแปรปรวนที่อธิบายได้
        - R2 = 1.0: perfect fit
        - R2 >= 0.99: excellent (สำหรับ pH calibration)
        - R2 >= 0.95: acceptable
        - R2 < 0.95: poor, ควรสอบเทียบใหม่

    สำหรับ pH calibration (For pH calibration):
        x = mV (แรงดันจาก ADC, voltage from ADC)
        y = pH (ค่า pH ของบัฟเฟอร์, buffer pH values)
        สมการ: pH = slope_m * mV + intercept_b
        Equation: pH = slope_m * mV + intercept_b

    ตัวอย่างการใช้งาน (Usage Example):
        >>> lr = LinearRegression()
        >>> lr.add_point(2068.0, 4.0)   # mV=2068, pH=4.0
        >>> lr.add_point(1650.0, 7.0)   # mV=1650, pH=7.0
        >>> lr.add_point(1290.0, 10.0)  # mV=1290, pH=10.0
        >>> slope, intercept, r_squared = lr.calculate()
        >>> print(f"pH = {slope:.6f} * mV + {intercept:.4f}, R2 = {r_squared:.4f}")
    """

    def __init__(self):
        """
        สร้าง LinearRegression object (Create LinearRegression object)
        """
        # เก็บข้อมูลจุด (x, y) (Store data points)
        self._x_data = []
        self._y_data = []

        # ผลลัพธ์การคำนวณ (Calculation results)
        self._slope = None
        self._intercept = None
        self._r_squared = None
        self._is_calculated = False

    @property
    def slope(self):
        """ค่า slope (m) ของสมการเส้นตรง (Slope of linear equation)"""
        if not self._is_calculated:
            self.calculate()
        return self._slope

    @property
    def intercept(self):
        """ค่า intercept (b) ของสมการเส้นตรง (Intercept of linear equation)"""
        if not self._is_calculated:
            self.calculate()
        return self._intercept

    @property
    def r_squared(self):
        """ค่า R-squared ของการ fit (R-squared of the fit)"""
        if not self._is_calculated:
            self.calculate()
        return self._r_squared

    @property
    def point_count(self):
        """จำนวนจุดข้อมูล (Number of data points)"""
        return len(self._x_data)

    def add_point(self, x, y):
        """
        เพิ่มจุดข้อมูล (Add a data point)

        Args:
            x (float): ค่า x (independent variable) เช่น mV จาก ADC
            y (float): ค่า y (dependent variable) เช่น pH ของบัฟเฟอร์

        หมายเหตุ (Note):
            เมื่อเพิ่มจุดใหม่ ผลการคำนวณเดิมจะถูก invalidate
            Adding new points invalidates previous calculations
        """
        self._x_data.append(float(x))
        self._y_data.append(float(y))
        self._is_calculated = False  # ต้องคำนวณใหม่

        print(f"เพิ่มจุด: ({x:.4f}, {y:.4f}) - รวม {len(self._x_data)} จุด "
              f"(Added point: ({x:.4f}, {y:.4f}) - total {len(self._x_data)} points)")

    def add_points(self, x_list, y_list):
        """
        เพิ่มหลายจุดพร้อมกัน (Add multiple points at once)

        Args:
            x_list (list): รายการค่า x (list of x values)
            y_list (list): รายการค่า y (list of y values)

        Raises:
            ValueError: ถ้าจำนวน x และ y ไม่เท่ากัน
        """
        if len(x_list) != len(y_list):
            raise ValueError(
                f"จำนวน x ({len(x_list)}) และ y ({len(y_list)}) ต้องเท่ากัน "
                f"(x ({len(x_list)}) and y ({len(y_list)}) must have same length)"
            )

        for x, y in zip(x_list, y_list):
            self._x_data.append(float(x))
            self._y_data.append(float(y))

        self._is_calculated = False
        print(f"เพิ่ม {len(x_list)} จุด - รวม {len(self._x_data)} จุด "
              f"(Added {len(x_list)} points - total {len(self._x_data)} points)")

    def clear(self):
        """
        ล้างข้อมูลทั้งหมด (Clear all data)
        """
        self._x_data = []
        self._y_data = []
        self._slope = None
        self._intercept = None
        self._r_squared = None
        self._is_calculated = False
        print("ล้างข้อมูลทั้งหมดแล้ว (All data cleared)")

    def _calculate_mean(self, data):
        """
        คำนวณค่าเฉลี่ย (Calculate mean)

        Args:
            data (list): รายการตัวเลข (list of numbers)

        Returns:
            float: ค่าเฉลี่ย (mean value)
        """
        if len(data) == 0:
            return 0
        return sum(data) / len(data)

    def _calculate_variance(self, data, mean):
        """
        คำนวณความแปรปรวน (Calculate variance)

        สูตร: variance = sum((xi - mean)^2) / n

        Args:
            data (list): รายการตัวเลข
            mean (float): ค่าเฉลี่ย

        Returns:
            float: ความแปรปรวน (variance)
        """
        if len(data) == 0:
            return 0
        return sum((x - mean) ** 2 for x in data) / len(data)

    def _calculate_covariance(self, x_data, y_data, x_mean, y_mean):
        """
        คำนวณ covariance (Calculate covariance)

        สูตร: covariance = sum((xi - x_mean)(yi - y_mean)) / n

        Args:
            x_data (list): รายการค่า x
            y_data (list): รายการค่า y
            x_mean (float): ค่าเฉลี่ย x
            y_mean (float): ค่าเฉลี่ย y

        Returns:
            float: covariance
        """
        if len(x_data) == 0:
            return 0
        n = len(x_data)
        return sum((x - x_mean) * (y - y_mean) for x, y in zip(x_data, y_data)) / n

    def calculate(self):
        """
        คำนวณ linear regression (Calculate linear regression)

        สูตร:
            slope (m) = covariance(x, y) / variance(x)
            intercept (b) = y_mean - slope * x_mean
            R-squared = 1 - (SS_residual / SS_total)

        Returns:
            tuple: (slope, intercept, r_squared)

        Raises:
            ValueError: ถ้ามีจุดน้อยกว่า 2 จุด หรือ variance เป็น 0
        """
        n = len(self._x_data)

        # ตรวจสอบจำนวนจุด (Check number of points)
        if n < 2:
            raise ValueError(
                f"ต้องมีอย่างน้อย 2 จุด แต่มี {n} จุด "
                f"(Need at least 2 points, got {n})"
            )

        # คำนวณค่าเฉลี่ย (Calculate means)
        x_mean = self._calculate_mean(self._x_data)
        y_mean = self._calculate_mean(self._y_data)

        # คำนวณ variance และ covariance
        x_variance = self._calculate_variance(self._x_data, x_mean)
        covariance = self._calculate_covariance(
            self._x_data, self._y_data, x_mean, y_mean
        )

        # ตรวจสอบ variance (Check variance)
        if x_variance == 0:
            raise ValueError(
                "Variance ของ x เป็น 0 - ค่า x ทั้งหมดเหมือนกัน "
                "(x variance is 0 - all x values are the same)"
            )

        # คำนวณ slope และ intercept
        self._slope = covariance / x_variance
        self._intercept = y_mean - self._slope * x_mean

        # คำนวณ R-squared
        # y_pred = predicted y values
        y_pred = [self._slope * x + self._intercept for x in self._x_data]

        # SS_residual = sum of squared residuals
        ss_residual = sum((y - y_p) ** 2 for y, y_p in zip(self._y_data, y_pred))

        # SS_total = sum of squared deviations from mean
        ss_total = sum((y - y_mean) ** 2 for y in self._y_data)

        # R-squared
        if ss_total == 0:
            self._r_squared = 1.0  # Perfect fit ถ้า y ทุกค่าเท่ากัน
        else:
            self._r_squared = 1 - (ss_residual / ss_total)

        self._is_calculated = True

        print(f"ผลการคำนวณ: slope={self._slope:.4f}, intercept={self._intercept:.4f}, "
              f"R2={self._r_squared:.6f}")
        print(f"(Calculation result: slope={self._slope:.4f}, "
              f"intercept={self._intercept:.4f}, R2={self._r_squared:.6f})")

        return self._slope, self._intercept, self._r_squared

    def predict(self, x):
        """
        ทำนายค่า y จาก x (Predict y from x)

        สูตร: y = slope * x + intercept

        Args:
            x (float): ค่า x ที่ต้องการทำนาย

        Returns:
            float: ค่า y ที่ทำนาย (predicted y value)
        """
        if not self._is_calculated:
            self.calculate()

        return self._slope * x + self._intercept

    def predict_inverse(self, y):
        """
        ทำนายค่า x จาก y (Predict x from y - inverse function)

        สูตร: x = (y - intercept) / slope

        Args:
            y (float): ค่า y ที่ต้องการหา x

        Returns:
            float: ค่า x ที่ทำนาย (predicted x value)
        """
        if not self._is_calculated:
            self.calculate()

        if self._slope == 0:
            raise ValueError("ไม่สามารถคำนวณ inverse ได้เมื่อ slope = 0 "
                           "(Cannot calculate inverse when slope = 0)")

        return (y - self._intercept) / self._slope

    def validate(self, threshold=0.99):
        """
        ตรวจสอบคุณภาพของการ fit (Validate fit quality)

        Args:
            threshold (float): ค่า R-squared ขั้นต่ำที่ยอมรับ (minimum acceptable R2)
                               ค่าเริ่มต้น: 0.99

        Returns:
            tuple: (is_valid, message)
                - is_valid (bool): True ถ้าผ่านเกณฑ์
                - message (str): ข้อความอธิบาย
        """
        if not self._is_calculated:
            self.calculate()

        r2_percent = self._r_squared * 100

        if self._r_squared >= threshold:
            return True, f"การสอบเทียบถูกต้อง R2={r2_percent:.2f}% (Calibration valid)"
        elif self._r_squared >= 0.95:
            return False, f"การสอบเทียบยอมรับได้ R2={r2_percent:.2f}% แต่ต่ำกว่าเกณฑ์ (Acceptable but below threshold)"
        else:
            return False, f"การสอบเทียบไม่ผ่าน R2={r2_percent:.2f}% กรุณาสอบเทียบใหม่ (Calibration failed, please recalibrate)"

    def get_equation_string(self):
        """
        รับสมการในรูปแบบ string (Get equation as string)

        Returns:
            str: สมการ เช่น "y = -5.7901x + 16.7690"
        """
        if not self._is_calculated:
            self.calculate()

        sign = "+" if self._intercept >= 0 else "-"
        return f"y = {self._slope:.4f}x {sign} {abs(self._intercept):.4f}"

    def get_summary(self):
        """
        รับสรุปผลการคำนวณ (Get calculation summary)

        Returns:
            dict: สรุปผล
        """
        if not self._is_calculated:
            self.calculate()

        return {
            'n_points': len(self._x_data),
            'slope': self._slope,
            'intercept': self._intercept,
            'r_squared': self._r_squared,
            'r_squared_percent': self._r_squared * 100,
            'equation': self.get_equation_string(),
            'x_data': self._x_data.copy(),
            'y_data': self._y_data.copy()
        }

    def __repr__(self):
        """แสดงข้อมูล LinearRegression"""
        if self._is_calculated:
            return (f"LinearRegression(n={len(self._x_data)}, "
                    f"slope={self._slope:.4f}, intercept={self._intercept:.4f}, "
                    f"R2={self._r_squared:.4f})")
        else:
            return f"LinearRegression(n={len(self._x_data)}, not calculated)"


# ==============================================================================
# ฟังก์ชันช่วยเหลือ (Helper Functions)
# ==============================================================================

def calculate_linear_regression(x_list, y_list):
    """
    ฟังก์ชันลัดสำหรับคำนวณ linear regression
    Shortcut function for calculating linear regression

    สำหรับ pH calibration: x=mV, y=pH
    For pH calibration: x=mV (from ADC), y=pH (buffer values)

    Args:
        x_list (list): รายการค่า x (เช่น mV จาก ADC)
        y_list (list): รายการค่า y (เช่น pH ของบัฟเฟอร์)

    Returns:
        tuple: (slope, intercept, r_squared)

    ตัวอย่าง (Example):
        >>> voltages_mv = [2068.0, 1650.0, 1290.0]
        >>> phs = [4.0, 7.0, 10.0]
        >>> slope_m, intercept_b, r2 = calculate_linear_regression(voltages_mv, phs)
    """
    lr = LinearRegression()
    lr.add_points(x_list, y_list)
    return lr.calculate()


def calculate_mean(data):
    """
    คำนวณค่าเฉลี่ย (Calculate mean)

    Args:
        data (list): รายการตัวเลข

    Returns:
        float: ค่าเฉลี่ย
    """
    if len(data) == 0:
        return 0
    return sum(data) / len(data)


def calculate_std(data):
    """
    คำนวณส่วนเบี่ยงเบนมาตรฐาน (Calculate standard deviation)

    Args:
        data (list): รายการตัวเลข

    Returns:
        float: ส่วนเบี่ยงเบนมาตรฐาน
    """
    if len(data) == 0:
        return 0
    mean = calculate_mean(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    return variance ** 0.5
