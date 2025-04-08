#!/usr/bin/python3

import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline
import pandas as pd

# Check if the data file was provided as a command-line argument
if len(sys.argv) < 2:
    print("Usage: python <script_name>.py data_file.csv")
    sys.exit(1)  # Exit the script if no argument is provided

# The first command-line argument is the script name, so the second one is your data file
data_file = sys.argv[1]

# Load data from the specified CSV file
data = pd.read_csv(data_file)
volume = data['Volume (mL)'].values
pH = data['pH Value'].values

# Fit a spline to the data
spline = UnivariateSpline(volume, pH, s=1.0)  # Adjust the smoothing factor as needed

# First derivative of the spline (dpH/dVolume)
spline_derivative = spline.derivative()

# Second derivative of the spline (d^2pH/dVolume^2)
spline_second_derivative = spline.derivative(n=2)

# Generate fine volumes for plotting
volumes_fine = np.linspace(volume.min(), volume.max(), 600)

# Find where the second derivative changes sign
second_derivative_values = spline_second_derivative(volumes_fine)
zero_crossings = np.where(np.diff(np.sign(second_derivative_values)))[0]

# Plotting
plt.figure(figsize=(12, 8))

# Original data and spline
plt.subplot(3, 1, 1)
plt.plot(volume, pH, 'o', label='Original Data')
plt.plot(volumes_fine, spline(volumes_fine), label='Spline Fit')
plt.title('Original Data and Spline Fit')
plt.legend()

# First derivative
plt.subplot(3, 1, 2)
plt.plot(volumes_fine, spline_derivative(volumes_fine), label='First Derivative')
plt.title('First Derivative of Spline Fit')
plt.legend()

# Second derivative with zero crossings
plt.subplot(3, 1, 3)
plt.plot(volumes_fine, second_derivative_values, label='Second Derivative')
for crossing in zero_crossings:
    plt.axvline(x=volumes_fine[crossing], color='r', linestyle='--')
    # Label the volume at zero crossing
    volume_at_crossing = volumes_fine[crossing]
    y_min, y_max = plt.ylim()
    label_y_position = y_min + (y_max - y_min) * 0.05 
    plt.text(volume_at_crossing, label_y_position, f'{volume_at_crossing:.2f} mL', color='black', fontsize=12, fontweight='bold', ha='center', va='bottom')
plt.title('Second Derivative of Spline Fit and Zero Crossings')
plt.legend()

plt.tight_layout()
plt.show()

# Print approximate volumes of zero crossings
for crossing in zero_crossings:
    print(f"Approximate volume at zero crossing: {volumes_fine[crossing]} mL")


