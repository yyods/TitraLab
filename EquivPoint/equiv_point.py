#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TitraLab - Titration Curve Analysis Tool (EquivPoint)
เครื่องมือวิเคราะห์เส้นโค้งการไทเทรตและหาจุดสมมูล

Description (คำอธิบาย):
    This script analyzes titration curve data to find the equivalence point
    using spline interpolation and derivative analysis methods.

    สคริปต์นี้วิเคราะห์ข้อมูลเส้นโค้งการไทเทรตเพื่อหาจุดสมมูล
    โดยใช้การประมาณค่าด้วยสไปลน์และการวิเคราะห์อนุพันธ์

Usage (วิธีใช้งาน):
    python equiv_point.py <input_csv_file>

    Example (ตัวอย่าง):
        python equiv_point.py titration_data_R1.csv

Input Format (รูปแบบข้อมูลนำเข้า):
    CSV file with required columns: "Volume (mL)", "pH Value"
    ไฟล์ CSV ต้องมีคอลัมน์: "Volume (mL)", "pH Value"
    (Extra columns like Time(s), Temperature(C) are ignored)
    (คอลัมน์เพิ่มเติม เช่น Time(s), Temperature(C) จะถูกข้ามไป)

    Compatible with TitraLab ESP32 output (titration_data_R*.csv):
    รองรับไฟล์จากบอร์ด TitraLab ESP32 โดยตรง:
    Volume (mL),pH Value,Time(s),Temperature(C)
    0.000,1.188,0.00,25.10
    0.200,1.215,12.50,25.12
    ...

    Minimal format (also works):
    Volume (mL),pH Value
    0.000,1.188
    0.200,1.215
    ...

Output (ผลลัพธ์):
    - 3-panel analysis plot (กราฟวิเคราะห์ 3 ช่อง):
        1. Titration curve with equivalence point marker
        2. First derivative (dpH/dV) with maximum marked
        3. Second derivative (d²pH/dV²) with zero crossings marked
    - Console output with equivalence point volume and pH

Methods (วิธีการวิเคราะห์):
    1. Spline fitting: UnivariateSpline for smooth curve interpolation
    2. First derivative: Maximum |dpH/dV| indicates equivalence point
    3. Second derivative: Zero crossing confirms equivalence point

Author: TitraLab Team
Course: Integrated Chemistry Laboratory I (2302311)
Institution: Chulalongkorn University
Version: 2.0
"""

import sys
import io
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline
import pandas as pd

# ==============================================================================
# ตั้งค่าการเข้ารหัส UTF-8 สำหรับ Windows Console
# (Set UTF-8 encoding for Windows Console)
# ==============================================================================
if sys.platform == 'win32':
    # ตั้งค่า stdout/stderr ให้รองรับ UTF-8 บน Windows
    # (Configure stdout/stderr to support UTF-8 on Windows)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ==============================================================================
# ฟังก์ชันตรวจสอบและโหลดข้อมูล (Data validation and loading functions)
# ==============================================================================

def validate_csv_file(filepath):
    """
    ตรวจสอบว่าไฟล์ CSV มีอยู่และมีรูปแบบที่ถูกต้อง
    Validate that CSV file exists and has correct format.

    Parameters (พารามิเตอร์):
        filepath: Path to the CSV file (พาธไปยังไฟล์ CSV)

    Returns (ส่งคืน):
        pandas.DataFrame: Validated data (ข้อมูลที่ผ่านการตรวจสอบ)

    Raises (ข้อผิดพลาด):
        FileNotFoundError: If file doesn't exist (ถ้าไม่พบไฟล์)
        ValueError: If required columns are missing (ถ้าไม่มีคอลัมน์ที่ต้องการ)
    """
    # ใช้ pathlib สำหรับความเข้ากันได้ข้ามแพลตฟอร์ม
    # (Use pathlib for cross-platform compatibility)
    data_path = Path(filepath).resolve()

    # ตรวจสอบว่าไฟล์มีอยู่หรือไม่ (Check if file exists)
    if not data_path.exists():
        print(f"\n{'='*60}")
        print("ข้อผิดพลาด: ไม่พบไฟล์ (Error: File not found)")
        print(f"{'='*60}")
        print(f"ไฟล์: {data_path}")
        print(f"File: {data_path}")
        print("\nกรุณาตรวจสอบว่าไฟล์มีอยู่และพาธถูกต้อง")
        print("Please verify that the file exists and the path is correct.")
        print(f"{'='*60}\n")
        raise FileNotFoundError(f"File not found: {data_path}")

    # ลองโหลดไฟล์ CSV (Try to load CSV file)
    # comment='#' ข้ามบรรทัดที่ขึ้นต้นด้วย # (เช่น summary จาก ESP32)
    # comment='#' skips lines starting with # (e.g., summary from ESP32)
    try:
        data = pd.read_csv(data_path, comment='#')
    except pd.errors.EmptyDataError:
        print(f"\n{'='*60}")
        print("ข้อผิดพลาด: ไฟล์ CSV ว่างเปล่า (Error: CSV file is empty)")
        print(f"{'='*60}")
        print(f"ไฟล์: {data_path}")
        print("\nกรุณาตรวจสอบว่าไฟล์มีข้อมูล")
        print("Please verify that the file contains data.")
        print(f"{'='*60}\n")
        raise ValueError("CSV file is empty")
    except Exception as e:
        print(f"\n{'='*60}")
        print("ข้อผิดพลาด: ไม่สามารถอ่านไฟล์ CSV ได้")
        print("Error: Unable to read CSV file")
        print(f"{'='*60}")
        print(f"รายละเอียด (Details): {str(e)}")
        print(f"{'='*60}\n")
        raise

    # ตรวจสอบคอลัมน์ที่จำเป็น (Check required columns)
    required_columns = ['Volume (mL)', 'pH Value']
    missing_columns = [col for col in required_columns if col not in data.columns]

    if missing_columns:
        print(f"\n{'='*60}")
        print("ข้อผิดพลาด: ไม่พบคอลัมน์ที่จำเป็น")
        print("Error: Required columns not found")
        print(f"{'='*60}")
        print(f"คอลัมน์ที่ขาดหาย (Missing columns): {missing_columns}")
        print(f"คอลัมน์ที่พบ (Found columns): {list(data.columns)}")
        print("\nรูปแบบที่ถูกต้อง (Correct format):")
        print("Volume (mL),pH Value")
        print("0.000,1.188")
        print("0.200,1.215")
        print("...")
        print("\nหรือจาก TitraLab ESP32 (or from TitraLab ESP32):")
        print("Volume (mL),pH Value,Time(s),Temperature(C)")
        print("0.000,1.188,0.00,25.10")
        print(f"{'='*60}\n")
        raise ValueError(f"Missing required columns: {missing_columns}")

    # ตรวจสอบว่ามีข้อมูลเพียงพอ (Check if there's enough data)
    if len(data) < 5:
        print(f"\n{'='*60}")
        print("ข้อผิดพลาด: ข้อมูลไม่เพียงพอ (Error: Insufficient data)")
        print(f"{'='*60}")
        print(f"จำนวนจุดข้อมูล (Number of data points): {len(data)}")
        print("ต้องการอย่างน้อย 5 จุดสำหรับการวิเคราะห์")
        print("At least 5 data points are required for analysis.")
        print(f"{'='*60}\n")
        raise ValueError("Insufficient data points (minimum 5 required)")

    # ตรวจสอบค่า NaN (Check for NaN values)
    nan_count = data[required_columns].isna().sum().sum()
    if nan_count > 0:
        print(f"\n{'='*60}")
        print("คำเตือน: พบค่าว่าง (Warning: Empty values found)")
        print(f"{'='*60}")
        print(f"จำนวนค่าว่าง (NaN count): {nan_count}")
        print("กำลังลบแถวที่มีค่าว่าง...")
        print("Removing rows with empty values...")
        data = data.dropna(subset=required_columns)
        print(f"จำนวนข้อมูลที่เหลือ (Remaining data points): {len(data)}")
        print(f"{'='*60}\n")

    return data


def find_ph7_crossing(volume, pH):
    """
    หาจุดที่ pH = 7.0 โดยใช้ linear interpolation จากข้อมูลดิบ
    Find where pH = 7.0 using linear interpolation from raw data.

    สำหรับการไทเทรตกรดแก่-เบสแก่ (เช่น HCl + NaOH) จุดสมมูลทางทฤษฎีคือ pH = 7.0
    For strong acid-strong base titrations (e.g., HCl + NaOH),
    the theoretical equivalence point is at pH = 7.0

    Parameters (พารามิเตอร์):
        volume: numpy array of volumes (อาร์เรย์ปริมาตร)
        pH: numpy array of pH values (อาร์เรย์ค่า pH)

    Returns (ส่งคืน):
        dict or None: {'volume': float, 'ph': 7.0} or None if not found
    """
    for i in range(len(pH) - 1):
        # ตรวจสอบว่า pH = 7 อยู่ระหว่างจุดสองจุดนี้หรือไม่
        # (Check if pH = 7 is between these two points)
        if (pH[i] < 7.0 and pH[i+1] > 7.0) or (pH[i] > 7.0 and pH[i+1] < 7.0):
            # Linear interpolation หาปริมาตรที่ pH = 7
            # (Linear interpolation to find volume at pH = 7)
            v_at_ph7 = volume[i] + (7.0 - pH[i]) * (volume[i+1] - volume[i]) / (pH[i+1] - pH[i])
            return {
                'volume': float(v_at_ph7),
                'pH': 7.0,
                'v_before': float(volume[i]),
                'pH_before': float(pH[i]),
                'v_after': float(volume[i+1]),
                'pH_after': float(pH[i+1])
            }
    return None


def find_equivalence_point(volume, pH, smoothing_factor=1.0):
    """
    หาจุดสมมูลโดยใช้วิธีอนุพันธ์อันดับหนึ่งและอันดับสอง
    Find equivalence point using first and second derivative methods.

    Parameters (พารามิเตอร์):
        volume: numpy array of titrant volumes (อาร์เรย์ปริมาตรสารไทแทรนต์)
        pH: numpy array of pH values (อาร์เรย์ค่า pH)
        smoothing_factor: Spline smoothing parameter (พารามิเตอร์ปรับความเรียบ)

    Returns (ส่งคืน):
        dict: Dictionary containing analysis results
              - 'spline': fitted spline object
              - 'spline_1st': first derivative spline
              - 'spline_2nd': second derivative spline
              - 'volumes_fine': fine volume grid for plotting
              - 'equiv_volume': equivalence point volume (mL)
              - 'equiv_pH': pH at equivalence point
              - 'max_derivative': maximum |dpH/dV| value
              - 'zero_crossings': indices of second derivative zero crossings
              - 'ph7_crossing': volume where pH = 7.0 (for strong acid-base)
    """
    # สร้างสไปลน์จากข้อมูล (Fit spline to data)
    spline = UnivariateSpline(volume, pH, s=smoothing_factor)

    # คำนวณอนุพันธ์อันดับหนึ่ง (Calculate first derivative)
    spline_1st = spline.derivative(n=1)

    # คำนวณอนุพันธ์อันดับสอง (Calculate second derivative)
    spline_2nd = spline.derivative(n=2)

    # สร้างตารางปริมาตรละเอียดสำหรับการวิเคราะห์
    # (Generate fine volume grid for analysis)
    volumes_fine = np.linspace(volume.min(), volume.max(), 600)

    # คำนวณอนุพันธ์อันดับหนึ่งที่จุดละเอียด
    # (Calculate first derivative at fine points)
    first_derivative_values = spline_1st(volumes_fine)

    # หาจุดที่อนุพันธ์อันดับหนึ่งมีค่าสูงสุด (ค่าสัมบูรณ์)
    # (Find where absolute first derivative is maximum)
    abs_derivative = np.abs(first_derivative_values)
    max_idx = np.argmax(abs_derivative)
    equiv_volume = volumes_fine[max_idx]
    max_derivative = first_derivative_values[max_idx]

    # หาค่า pH ที่จุดสมมูล (Find pH at equivalence point)
    equiv_pH = float(spline(equiv_volume))

    # หาจุดที่อนุพันธ์อันดับสองเปลี่ยนเครื่องหมาย (zero crossings)
    # (Find where second derivative changes sign)
    second_derivative_values = spline_2nd(volumes_fine)
    all_zero_crossings = np.where(np.diff(np.sign(second_derivative_values)))[0]

    # กรองเฉพาะจุดตัดศูนย์ที่ใกล้กับจุดสมมูลที่หาได้จากอนุพันธ์อันดับหนึ่ง
    # (Filter only zero crossings near the equivalence point from first derivative)
    # หาจุดที่ใกล้ที่สุดกับจุดสมมูล (Find closest zero crossing to equivalence point)
    if len(all_zero_crossings) > 0:
        distances = np.abs(volumes_fine[all_zero_crossings] - equiv_volume)
        closest_idx = np.argmin(distances)
        # เก็บเฉพาะจุดตัดศูนย์ที่อยู่ภายในช่วง +/- 1 mL จากจุดสมมูล
        # (Keep only zero crossings within +/- 1 mL of equivalence point)
        relevant_crossings = [c for c in all_zero_crossings
                              if abs(volumes_fine[c] - equiv_volume) < 1.0]
        if not relevant_crossings:
            # ถ้าไม่มีจุดในช่วง ให้ใช้จุดที่ใกล้ที่สุด
            # (If no crossings in range, use the closest one)
            relevant_crossings = [all_zero_crossings[closest_idx]]
        zero_crossings = np.array(relevant_crossings)
    else:
        zero_crossings = all_zero_crossings

    # หาจุดที่ pH = 7 สำหรับการไทเทรตกรดแก่-เบสแก่
    # (Find pH = 7 crossing for strong acid-strong base titrations)
    ph7_crossing = find_ph7_crossing(volume, pH)

    return {
        'spline': spline,
        'spline_1st': spline_1st,
        'spline_2nd': spline_2nd,
        'volumes_fine': volumes_fine,
        'equiv_volume': equiv_volume,
        'equiv_pH': equiv_pH,
        'max_derivative': max_derivative,
        'zero_crossings': zero_crossings,
        'all_zero_crossings': all_zero_crossings,  # เก็บไว้สำหรับการอ้างอิง
        'first_derivative_values': first_derivative_values,
        'second_derivative_values': second_derivative_values,
        'ph7_crossing': ph7_crossing  # จุดที่ pH = 7 (สำหรับกรดแก่-เบสแก่)
    }


def create_analysis_plot(volume, pH, results, output_path=None):
    """
    สร้างกราฟวิเคราะห์ 3 ช่อง พร้อมป้ายกำกับสองภาษา
    Create 3-panel analysis plot with bilingual labels.

    Parameters (พารามิเตอร์):
        volume: numpy array of original volume data
        pH: numpy array of original pH data
        results: dictionary from find_equivalence_point()
        output_path: optional path to save the figure
    """
    # ตั้งค่าฟอนต์สำหรับภาษาไทย (อาจต้องปรับตามระบบ)
    # (Set font for Thai language - may need adjustment per system)
    plt.rcParams['font.family'] = ['TH Sarabun New', 'Tahoma', 'DejaVu Sans', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False

    # ดึงผลลัพธ์จากการวิเคราะห์ (Extract results)
    spline = results['spline']
    volumes_fine = results['volumes_fine']
    equiv_volume = results['equiv_volume']
    equiv_pH = results['equiv_pH']
    first_derivative_values = results['first_derivative_values']
    second_derivative_values = results['second_derivative_values']
    zero_crossings = results['zero_crossings']
    ph7_crossing = results.get('ph7_crossing')  # จุดที่ pH = 7 (ถ้ามี)

    # สร้างรูปขนาด 12x10 นิ้ว (Create figure 12x10 inches)
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))

    # ตั้งชื่อหลักของกราฟ (Set main title)
    # ใช้ pH = 7 crossing ถ้าเป็นกรดแก่-เบสแก่
    if ph7_crossing:
        title_vol = ph7_crossing['volume']
        title_ph = 7.0
        fig.suptitle(
            f'Titration Curve Analysis / การวิเคราะห์เส้นโค้งไทเทรชัน\n'
            f'Equivalence Point (pH=7) / จุดสมมูล: {title_vol:.2f} mL, pH = {title_ph:.2f}',
            fontsize=14, fontweight='bold'
        )
    else:
        fig.suptitle(
            f'Titration Curve Analysis / การวิเคราะห์เส้นโค้งไทเทรชัน\n'
            f'Equivalence Point / จุดสมมูล: {equiv_volume:.2f} mL, pH = {equiv_pH:.2f}',
            fontsize=14, fontweight='bold'
        )

    # ===== Panel 1: Titration Curve / เส้นโค้งไทเทรชัน =====
    ax1 = axes[0]

    # พล็อตข้อมูลดิบ (Plot raw data)
    ax1.plot(volume, pH, 'o', markersize=6, color='blue',
             label='Data Points / ข้อมูลจริง', alpha=0.7)

    # พล็อตเส้นโค้งสไปลน์ (Plot spline curve)
    ax1.plot(volumes_fine, spline(volumes_fine), '-', linewidth=2, color='darkblue',
             label='Spline Fit / เส้นโค้งสไปลน์')

    # ทำเครื่องหมายจุดสมมูล (Mark equivalence point)
    if ph7_crossing:
        # สำหรับกรดแก่-เบสแก่: แสดงจุด pH = 7 เป็นจุดหลัก (สีเขียว)
        # (For strong acid-base: show pH = 7 as primary point in green)
        ph7_vol = ph7_crossing['volume']
        ax1.axvline(x=ph7_vol, color='green', linestyle='-', linewidth=2, alpha=0.9)
        ax1.axhline(y=7.0, color='green', linestyle='-', linewidth=2, alpha=0.9)
        ax1.plot(ph7_vol, 7.0, 'g*', markersize=25,
                 label=f'pH=7 Point / จุด pH=7 ({ph7_vol:.2f} mL)', zorder=10)

        # คำอธิบายจุด pH = 7 (Annotation for pH = 7 point)
        ax1.annotate(
            f'V = {ph7_vol:.2f} mL\npH = 7.00\n(Theoretical)',
            xy=(ph7_vol, 7.0),
            xytext=(ph7_vol + 1.0, 7.0 + 2.0),
            fontsize=10,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.9),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2', color='green')
        )

        # แสดงจุดจากวิธี derivative ด้วย (สีแดงอ่อน) เพื่อเปรียบเทียบ
        # (Also show derivative method point in light red for comparison)
        ax1.axvline(x=equiv_volume, color='red', linestyle='--', linewidth=1, alpha=0.5)
        ax1.plot(equiv_volume, equiv_pH, 'r*', markersize=12, alpha=0.5,
                 label=f'Derivative / อนุพันธ์ ({equiv_volume:.2f} mL)')
    else:
        # กรณีทั่วไป: แสดงจุดจากวิธี derivative
        ax1.axvline(x=equiv_volume, color='red', linestyle='--', linewidth=1.5, alpha=0.8)
        ax1.axhline(y=equiv_pH, color='red', linestyle='--', linewidth=1.5, alpha=0.8)
        ax1.plot(equiv_volume, equiv_pH, 'r*', markersize=20,
                 label=f'Equiv. Point / จุดสมมูล ({equiv_volume:.2f} mL)')

        # เพิ่มคำอธิบายจุดสมมูล (Add equivalence point annotation)
        ax1.annotate(
            f'V = {equiv_volume:.2f} mL\npH = {equiv_pH:.2f}',
            xy=(equiv_volume, equiv_pH),
            xytext=(equiv_volume + 0.5, equiv_pH - 1.5),
            fontsize=10,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.8),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2')
        )

    ax1.set_xlabel('Volume (mL) / ปริมาตร (mL)', fontsize=11)
    ax1.set_ylabel('pH Value / ค่า pH', fontsize=11)
    ax1.set_title('Titration Curve / เส้นโค้งไทเทรชัน', fontsize=12, fontweight='bold')
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.set_xlim(volume.min() - 0.2, volume.max() + 0.2)

    # ===== Panel 2: First Derivative / อนุพันธ์อันดับหนึ่ง =====
    ax2 = axes[1]

    # พล็อตอนุพันธ์อันดับหนึ่ง (Plot first derivative)
    ax2.plot(volumes_fine, first_derivative_values, '-', linewidth=2, color='green',
             label='dpH/dV / อนุพันธ์อันดับหนึ่ง')

    # ทำเครื่องหมายจุดสูงสุด (Mark maximum)
    max_idx = np.argmax(np.abs(first_derivative_values))
    max_derivative = first_derivative_values[max_idx]
    ax2.axvline(x=equiv_volume, color='red', linestyle='--', linewidth=1.5, alpha=0.8)
    ax2.plot(equiv_volume, max_derivative, 'r*', markersize=15,
             label=f'Maximum / ค่าสูงสุด ({equiv_volume:.2f} mL)')

    ax2.set_xlabel('Volume (mL) / ปริมาตร (mL)', fontsize=11)
    ax2.set_ylabel('dpH/dV', fontsize=11)
    ax2.set_title('First Derivative / อนุพันธ์อันดับหนึ่ง (dpH/dV)', fontsize=12, fontweight='bold')
    ax2.legend(loc='best', fontsize=9)
    ax2.grid(True, linestyle='--', alpha=0.7)
    ax2.set_xlim(volume.min() - 0.2, volume.max() + 0.2)

    # ===== Panel 3: Second Derivative / อนุพันธ์อันดับสอง =====
    ax3 = axes[2]

    # พล็อตอนุพันธ์อันดับสอง (Plot second derivative)
    ax3.plot(volumes_fine, second_derivative_values, '-', linewidth=2, color='purple',
             label='d²pH/dV² / อนุพันธ์อันดับสอง')

    # พล็อตเส้นศูนย์ (Plot zero line)
    ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

    # ทำเครื่องหมายจุดที่อนุพันธ์อันดับสองเท่ากับศูนย์
    # (Mark zero crossings of second derivative)
    for i, crossing in enumerate(zero_crossings):
        volume_at_crossing = volumes_fine[crossing]
        ax3.axvline(x=volume_at_crossing, color='red', linestyle='--', linewidth=1.5, alpha=0.8)

        # ป้ายกำกับปริมาตร (Volume label)
        y_min, y_max = ax3.get_ylim() if ax3.get_ylim()[0] != ax3.get_ylim()[1] else (-1, 1)
        label_y_position = 0.1 * (y_max - y_min) if y_max != y_min else 0.1
        ax3.text(volume_at_crossing, label_y_position, f'{volume_at_crossing:.2f} mL',
                 color='red', fontsize=10, fontweight='bold', ha='center', va='bottom',
                 bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))

    ax3.set_xlabel('Volume (mL) / ปริมาตร (mL)', fontsize=11)
    ax3.set_ylabel('d²pH/dV²', fontsize=11)
    ax3.set_title('Second Derivative / อนุพันธ์อันดับสอง (d²pH/dV²) - Zero Crossings / จุดตัดศูนย์',
                  fontsize=12, fontweight='bold')
    ax3.legend(loc='best', fontsize=9)
    ax3.grid(True, linestyle='--', alpha=0.7)
    ax3.set_xlim(volume.min() - 0.2, volume.max() + 0.2)

    # ปรับระยะห่างระหว่างกราฟ (Adjust spacing between plots)
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    # บันทึกรูปถ้าระบุพาธ (Save figure if path specified)
    if output_path:
        output_file = Path(output_path)
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"\nบันทึกกราฟที่ (Graph saved to): {output_file}")

    return fig


def print_summary(results, data_file):
    """
    พิมพ์สรุปผลการวิเคราะห์ในรูปแบบสองภาษา
    Print analysis summary in bilingual format.

    Parameters (พารามิเตอร์):
        results: dictionary from find_equivalence_point()
        data_file: path to the input data file
    """
    equiv_volume = results['equiv_volume']
    equiv_pH = results['equiv_pH']
    max_derivative = results['max_derivative']
    zero_crossings = results['zero_crossings']
    volumes_fine = results['volumes_fine']

    print("\n" + "="*70)
    print("TITRATION ANALYSIS SUMMARY / สรุปผลการวิเคราะห์ไทเทรชัน")
    print("="*70)
    print(f"\nInput File / ไฟล์ข้อมูล: {data_file}")

    print("\n" + "-"*70)
    print("EQUIVALENCE POINT RESULTS / ผลการหาจุดสมมูล")
    print("-"*70)

    print(f"\n  Method 1: First Derivative Maximum / วิธีอนุพันธ์อันดับหนึ่งสูงสุด")
    print(f"  ----------------------------------------------------------------")
    print(f"  Volume at Equivalence Point / ปริมาตรจุดสมมูล: {equiv_volume:.3f} mL")
    print(f"  pH at Equivalence Point / ค่า pH ที่จุดสมมูล:  {equiv_pH:.3f}")
    print(f"  Maximum dpH/dV / ค่า dpH/dV สูงสุด:           {max_derivative:.3f}")

    if len(zero_crossings) > 0:
        print(f"\n  Method 2: Second Derivative Zero Crossings / วิธีอนุพันธ์อันดับสองเท่ากับศูนย์")
        print(f"  ----------------------------------------------------------------")
        for i, crossing in enumerate(zero_crossings, 1):
            volume_at_crossing = volumes_fine[crossing]
            print(f"  Zero Crossing #{i} / จุดตัดศูนย์ที่ {i}: {volume_at_crossing:.3f} mL")

    # แสดงผลการหาจุด pH = 7 (สำหรับกรดแก่-เบสแก่)
    # (Show pH = 7 crossing result for strong acid-strong base)
    ph7_crossing = results.get('ph7_crossing')
    if ph7_crossing:
        print(f"\n  Method 3: pH = 7 Crossing (Strong Acid-Base) / จุดที่ pH = 7 (กรดแก่-เบสแก่)")
        print(f"  ----------------------------------------------------------------")
        print(f"  *** RECOMMENDED for HCl + NaOH / แนะนำสำหรับ HCl + NaOH ***")
        print(f"  Volume at pH = 7.00 / ปริมาตรที่ pH = 7.00: {ph7_crossing['volume']:.3f} mL")
        print(f"  (Interpolated between V={ph7_crossing['v_before']:.2f} mL, pH={ph7_crossing['pH_before']:.2f}")
        print(f"   and V={ph7_crossing['v_after']:.2f} mL, pH={ph7_crossing['pH_after']:.2f})")

    print("\n" + "-"*70)
    print("INTERPRETATION / การตีความผล")
    print("-"*70)

    # แสดงผลตามประเภทการไทเทรต
    if ph7_crossing:
        # กรดแก่-เบสแก่: ใช้ pH = 7 crossing
        print(f"""
  FOR STRONG ACID-STRONG BASE TITRATION (HCl + NaOH):
  สำหรับการไทเทรตกรดแก่-เบสแก่ (HCl + NaOH):

  >>> Equivalence Point / จุดสมมูล: {ph7_crossing['volume']:.3f} mL (pH = 7.00) <<<

  This is the theoretical equivalence point where [H+] = [OH-].
  นี่คือจุดสมมูลทางทฤษฎีที่ [H+] = [OH-]

  Note: The derivative method gives V = {equiv_volume:.2f} mL, pH = {equiv_pH:.2f}
  หมายเหตุ: วิธีอนุพันธ์ให้ค่า V = {equiv_volume:.2f} mL, pH = {equiv_pH:.2f}
  (Difference due to spline interpolation through sparse data in steep region)
  (ความแตกต่างเกิดจากการประมาณค่าสไปลน์ในบริเวณที่ข้อมูลห่างกัน)
""")
    else:
        # กรณีทั่วไป หรือ กรดอ่อน-เบสแก่
        print(f"""
  The equivalence point is at approximately {equiv_volume:.2f} mL.
  จุดสมมูลอยู่ที่ประมาณ {equiv_volume:.2f} mL

  At this point, the pH is {equiv_pH:.2f}.
  ที่จุดนี้ ค่า pH เท่ากับ {equiv_pH:.2f}

  Note: For weak acid-strong base titrations, pH at equivalence > 7.
  หมายเหตุ: สำหรับกรดอ่อน-เบสแก่ ค่า pH ที่จุดสมมูลจะมากกว่า 7
""")

    print("="*70)
    print("END OF ANALYSIS / สิ้นสุดการวิเคราะห์")
    print("="*70 + "\n")


def print_usage():
    """
    พิมพ์วิธีการใช้งานสคริปต์
    Print script usage instructions.
    """
    print("\n" + "="*70)
    print("TitraLab EquivPoint - Titration Curve Analysis Tool")
    print("เครื่องมือวิเคราะห์เส้นโค้งไทเทรชัน")
    print("="*70)
    print("\nUsage / วิธีใช้งาน:")
    print("    python equiv_point.py <input_csv_file> [options]")
    print("\nOptions / ตัวเลือก:")
    print("    --save, -s     บันทึกกราฟเป็นไฟล์ PNG (Save plot as PNG file)")
    print("    --output, -o   ระบุชื่อไฟล์ output (Specify output filename)")
    print("\nExamples / ตัวอย่าง:")
    print("    python equiv_point.py titration_data_R1.csv")
    print("    python equiv_point.py titration_data_R1.csv --save")
    print("    python equiv_point.py titration_data_R1.csv -s -o data.png")
    print("\nRequired CSV Format / รูปแบบ CSV ที่ต้องการ:")
    print("    Volume (mL),pH Value")
    print("    0.000,1.188")
    print("    0.200,1.215")
    print("    ...")
    print("\n    TitraLab ESP32 format (also supported / รองรับไฟล์จาก ESP32):")
    print("    Volume (mL),pH Value,Time(s),Temperature(C)")
    print("    0.000,1.188,0.00,25.10")
    print("    0.200,1.215,12.50,25.12")
    print("\nNote / หมายเหตุ:")
    print("    - The CSV must have headers: 'Volume (mL)' and 'pH Value'")
    print("    - ไฟล์ CSV ต้องมีหัวคอลัมน์: 'Volume (mL)' และ 'pH Value'")
    print("    - Extra columns are ignored (คอลัมน์เพิ่มเติมจะถูกข้ามไป)")
    print("="*70 + "\n")


# ==============================================================================
# โปรแกรมหลัก (Main program)
# ==============================================================================

def main():
    """
    ฟังก์ชันหลักสำหรับรันการวิเคราะห์ไทเทรชัน
    Main function to run titration analysis.
    """
    # ตรวจสอบว่ามีไฟล์ข้อมูลให้มาหรือไม่
    # (Check if data file was provided)
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    # รับพาธไฟล์จาก command line (Get file path from command line)
    data_file = sys.argv[1]

    # ตรวจสอบ flags (Check for flags)
    # --save หรือ -s: บันทึกกราฟเป็นไฟล์ PNG
    # --output หรือ -o: ระบุชื่อไฟล์เอง
    save_plot = '--save' in sys.argv or '-s' in sys.argv

    # หาชื่อไฟล์ output ถ้าระบุด้วย --output หรือ -o
    # (Find output filename if specified with --output or -o)
    output_path = None
    if save_plot:
        # ใช้ชื่อไฟล์เดียวกับ input แต่เปลี่ยนเป็น .png
        # (Use same filename as input but change to .png)
        input_path = Path(data_file)
        output_path = input_path.with_suffix('.png')

        # ตรวจสอบว่าระบุ --output หรือไม่
        # (Check if --output is specified)
        for i, arg in enumerate(sys.argv):
            if arg in ['--output', '-o'] and i + 1 < len(sys.argv):
                output_path = Path(sys.argv[i + 1])
                break

    print("\n" + "="*70)
    print("TitraLab EquivPoint - Starting Analysis")
    print("กำลังเริ่มการวิเคราะห์...")
    print("="*70)

    try:
        # ตรวจสอบและโหลดข้อมูล (Validate and load data)
        print(f"\nกำลังโหลดข้อมูลจาก (Loading data from): {data_file}")
        data = validate_csv_file(data_file)

        # ดึงข้อมูลปริมาตรและ pH (Extract volume and pH data)
        volume = data['Volume (mL)'].values
        pH = data['pH Value'].values

        print(f"จำนวนจุดข้อมูล (Number of data points): {len(volume)}")
        print(f"ช่วงปริมาตร (Volume range): {volume.min():.2f} - {volume.max():.2f} mL")
        print(f"ช่วง pH (pH range): {pH.min():.2f} - {pH.max():.2f}")

        # วิเคราะห์หาจุดสมมูล (Find equivalence point)
        print("\nกำลังวิเคราะห์... (Analyzing...)")
        results = find_equivalence_point(volume, pH, smoothing_factor=1.0)

        # พิมพ์สรุปผล (Print summary)
        print_summary(results, data_file)

        # สร้างและแสดงกราฟ (Create and display plot)
        print("กำลังสร้างกราฟ... (Creating plot...)")
        fig = create_analysis_plot(volume, pH, results, output_path=output_path)

        # แสดงกราฟ (Show plot) - ถ้าไม่ได้บันทึกไฟล์อย่างเดียว
        # (Show plot - unless only saving to file)
        if not save_plot:
            plt.show()
        else:
            plt.close(fig)  # ปิดกราฟหลังบันทึก (Close plot after saving)

        print("\nการวิเคราะห์เสร็จสมบูรณ์ (Analysis complete)")

    except FileNotFoundError:
        sys.exit(1)
    except ValueError as e:
        print(f"\nข้อผิดพลาดข้อมูล (Data error): {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nหยุดโปรแกรมโดยผู้ใช้ (Program stopped by user)")
        sys.exit(0)
    except Exception as e:
        print(f"\n{'='*60}")
        print("ข้อผิดพลาดที่ไม่คาดคิด (Unexpected error)")
        print(f"{'='*60}")
        print(f"รายละเอียด (Details): {str(e)}")
        print("\nกรุณาตรวจสอบข้อมูลและลองใหม่อีกครั้ง")
        print("Please check your data and try again.")
        print(f"{'='*60}\n")
        sys.exit(1)


# เรียกใช้โปรแกรมหลัก (Run main program)
if __name__ == "__main__":
    main()
