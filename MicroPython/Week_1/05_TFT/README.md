# TFT Example Code for TitraLab

This example demonstrates how to utilize the TFT display on the TitraLab board using the ili9341 driver. Follow the instructions below to set up the necessary files on your TitraLab board and run the example scripts.

## File Structure

The TFT example code includes the following files:

    .
    ├── 01_test_display.py # Example script to test basic TFT display functionality
    ├── 02_temperature.py # Example script to display temperature readings on the TFT
    ├── fonts
    │ ├── ArcadePix9x11.c # Font file for use with TFT display
    │ └── EspressoDolce18x24.c # Font file for use with TFT display
    ├── ili9341.py # TFT display driver
    └── xglcd_font.py # Font management library for TFT display

## Setup Instructions

### Step 1: Copy Required Files to the TitraLab Board

Before running any example scripts, copy the following files to the **root directory** of your TitraLab board:

1. `ArcadePix9x11.c` (from the `fonts` folder)
2. `EspressoDolce18x24.c` (from the `fonts` folder)
3. `ili9341.py`
4. `xglcd_font.py`

Use your IDE (such as [Thonny](https://thonny.org/)) or a file transfer method to ensure these files are placed correctly on the board.

### Step 2: Run the Example Scripts

After copying the required files:

1. Upload and run `01_test_display.py` to test basic display output.
2. Upload and run `02_temperature.py` to read and display temperature data on the TFT display.

Ensure that the TFT display is properly connected and the TitraLab board is powered on before running the scripts.

## Notes

- Make sure the required libraries (e.g., `machine`, `time`) are available in your MicroPython environment.
- The fonts (`ArcadePix9x11.c`, `EspressoDolce18x24.c`) are used to customize the appearance of text on the display.
- The `ili9341.py` driver and `xglcd_font.py` library are essential for interfacing with the TFT display and managing font rendering.

## Troubleshooting

If the display does not work as expected:

- Verify that all required files are correctly copied to the root directory of the TitraLab board.
- Check connections between the TFT display and the TitraLab board.
- Ensure that your board is running the correct version of MicroPython.

## License

This code is provided for educational purposes as part of the Integrated Chemistry Laboratory I (2302311) course. For any issues, please contact your course instructor.
