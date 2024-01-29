<h1>TitraLab Project README</h1>

<h2>Overview</h2>
TitraLab is a developmental board, ingeniously designed by Associate Professor Dr. Viwat Vchirawongkwin and Professor Dr. Sumrit Wacharasindhu, to enhance the learning experience in the field of chemistry. At its core, TitraLab utilizes the ESP32 microcontroller, renowned for its versatility and robust performance. This project plays a pivotal role in the Integrated Chemistry Laboratory I (2302311) course, particularly in the module titled "Advanced Acid-Base Titrations with Automated Flow System."

<h2>Purpose</h2>
The primary objective of TitraLab is to introduce students to the practical applications of programming in chemical analysis and laboratory automation. It serves as an educational tool in understanding and implementing automated titrations, a fundamental process in analytical chemistry. Through hands-on experience with TitraLab, students gain valuable insights into the integration of hardware and software in scientific research.

<h2>Key Features</h2>
<ul>
  <li>Microcontroller: ESP32</li>
  <li>Programming Compatibility: Arduino IDE and MicroPython</li>
  <li>IDE for MicroPython: Thonny</li>
  <li>Display: 2.4 inch TFT display with ili9341 driver</li>
  <li>Sensors & Indicators:</li>
  <ul>
    <li>Red and Green LEDs for status indication</li>
    <li>DS18B20 temperature sensor</li>
    <li>BNC connector for pH probe attachment</li>
    <li>Integrated circuit for reading millivoltage from the pH probe</li>
  </ul>
  <li>Storage: Micro SD card support</li>
  <li>Sound: Onboard buzzer</li>
</ul>

<h2>Course Structure</h2>
<h3>Week 1: Introduction to TitraLab Programming</h3>
<ul>
    <li>Blink: Understanding the GPIO of ESP32 as OUTPUT, using onboard LEDs</li>
    <li>Button: Learning about the GPIO of ESP32 as INPUT</li>
    <li>DS18B20: Reading temperature with the 1-wire protocol</li>
    <li>SDCard: Reading/writing data to a micro SD card</li>
    <li>TFT Display: Utilizing the ili9341 driver for data display</li>
    <li>Buzzer: Operating the onboard buzzer</li>
</ul>

<h3>Week 2: Theoretical Refreshment and Practical Application</h3>
<ul>
    <li>pH Measurement: Understanding the Nernst equation, using the pH probe connected via BNC</li>
    <li>Linear Regression: Recalling methods and equations</li>
    <li>Practical Goals:</li>
    <ul>
      <li>Calibration of pH probes and understanding millivoltage readings</li>
      <li>Calibration of peristaltic pump flow rate for titration</li>
    </ul>
</ul>

<h3>Week 3: Advanced Titration Practice</h3>
<ul>
    <li>Application: Using senior project code for acid-base titration</li>
    <li>Objective: Conducting titration between HCl and NaOH using TitraLab</li>
    <li>Analysis: Constructing a titration curve to find the equivalence point, compared to phenolphthalein indicator color change</li>
</ul>

