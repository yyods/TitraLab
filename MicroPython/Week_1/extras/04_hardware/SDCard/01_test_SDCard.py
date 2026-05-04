# ==============================================================================
# 01_test_SDCard.py - การทดสอบ SD Card (SD Card Test)
# ==============================================================================
# โปรแกรมนี้สาธิตการอ่าน-เขียนข้อมูลลง SD Card ผ่าน SPI
# This program demonstrates reading and writing data to SD Card via SPI
# ==============================================================================

import os
from machine import Pin, SoftSPI
from sdcard import SDCard

# ==============================================================================
# การกำหนดขา SPI สำหรับ SD Card ของ TitraLab
# SPI Pin assignment for TitraLab SD Card
# ==============================================================================
# MISO -> GPIO 19 (Master In Slave Out - รับข้อมูลจาก SD Card)
# MOSI -> GPIO 23 (Master Out Slave In - ส่งข้อมูลไป SD Card)
# SCK  -> GPIO 18 (Serial Clock - สัญญาณนาฬิกา)
# CS   -> GPIO 5  (Chip Select - เลือก SD Card)
# ==============================================================================

# สร้าง SoftSPI สำหรับ SD Card
# Create SoftSPI for SD Card
spisd = SoftSPI(baudrate=1000000, miso=Pin(19), mosi=Pin(23), sck=Pin(18))

# สร้าง SDCard object
# Create SDCard object
sd = SDCard(spisd, Pin(5))

print("=" * 50)
print("ทดสอบ SD Card (SD Card Test)")
print("=" * 50)

# แสดง root directory ก่อน mount
# Show root directory before mounting
print(f"Root directory ก่อน mount: {os.listdir()}")
print(f"Root directory before mount: {os.listdir()}")

try:
    # สร้าง VfsFat filesystem และ mount SD Card
    # Create VfsFat filesystem and mount SD Card
    vfs = os.VfsFat(sd)
    os.mount(vfs, '/sd')
    print("Mount SD Card สำเร็จ (SD Card mounted successfully)")

    # แสดง root directory หลัง mount
    # Show root directory after mounting
    print(f"Root directory หลัง mount: {os.listdir()}")

    # เปลี่ยนไปยัง directory ของ SD Card
    # Change to SD Card directory
    os.chdir('sd')
    print(f"ไฟล์ใน SD Card (Files in SD Card): {os.listdir()}")

    # ==============================================================================
    # ทดสอบเขียนไฟล์ (Test writing file)
    # ==============================================================================
    filename = 'test.txt'

    # เปิดไฟล์แบบ append และเขียนข้อความ
    # Open file in append mode and write text
    with open(filename, "a") as f:
        f.write('ทดสอบเขียนจาก MicroPython!\n')
        f.write('File created by MicroPython!\n')
    print(f"เขียนไฟล์ {filename} สำเร็จ (File {filename} written successfully)")

    # ==============================================================================
    # ทดสอบอ่านไฟล์ (Test reading file)
    # ==============================================================================
    with open(filename, "r") as f:
        content = f.read()
        print(f"\nเนื้อหาในไฟล์ (File content):\n{content}")

    print("=" * 50)
    print("ทดสอบเสร็จสิ้น (Test completed)")

    # กลับไป root directory
    # Return to root directory
    os.chdir('/')

    # หมายเหตุ: ถ้าต้องการ unmount ให้เปิดใช้บรรทัดด้านล่าง
    # Note: Uncomment the line below if you want to unmount
    # os.umount("/sd")

except OSError as e:
    print(f"เกิดข้อผิดพลาด (Error): {e}")
    print("กรุณาตรวจสอบว่าใส่ SD Card แล้ว (Please check if SD Card is inserted)")
