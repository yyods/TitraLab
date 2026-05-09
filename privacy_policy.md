# Privacy Policy for SciLabPro MicroPad

Last updated: 2026-05-09

This Privacy Policy applies to the SciLabPro MicroPad Android app, including the
proof-of-concept release `0.1.0`.

## Developer and Contact

SciLabPro MicroPad is developed by SciLabPro for TitraLab classroom board
testing and STEM education workflows.

Privacy contact: `viwat.v@chula.ac.th`

## Summary

SciLabPro MicroPad is an offline-first tablet coding workspace for TitraLab
boards. The app scans the temporary QR code shown on the board LCD, connects to
the board over Bluetooth Low Energy (BLE), edits MicroPython files, uploads code
to the board, runs code on the board, and displays console output.

The app does not include ads, analytics SDKs, cloud accounts, or a developer
server. The release Android app does not request Internet permission.

## Permissions Used

| Permission | Purpose |
| --- | --- |
| Camera | Used only to scan the temporary pairing QR code shown on the TitraLab LCD. |
| Bluetooth scan/connect | Used to discover and connect to the assigned TitraLab board over BLE. |
| Location on Android 11 and lower | Required by older Android versions for BLE scanning. The app does not use GPS location. |

Camera frames are processed on the device for QR decoding. The app does not take
photos, record video, or send camera data to SciLabPro.

## Data Accessed or Stored Locally

The app may store the following data locally on the tablet:

- Paired board identifiers and pairing state.
- Local workspace file cache and MicroPython code snapshots.
- Console output and run logs from the connected board.
- App preferences, such as language selection.

This local data stays on the tablet unless the user explicitly transfers it by
another mechanism outside the app.

## Data Collection and Sharing

SciLabPro MicroPad does not collect app data on a SciLabPro server and does not
share app data with third parties. BLE communication occurs directly between the
tablet and the nearby TitraLab board.

The app does not sell personal or sensitive user data.

## Data Retention and Deletion

Local app data remains on the tablet until the user deletes it through app
features where available, clears the app data in Android settings, or uninstalls
the app. Because SciLabPro MicroPad does not collect app data on a developer
server, there is no server-side user account or server-side data deletion flow.

## Security

SciLabPro MicroPad requests camera and Bluetooth permissions only when needed
for the pairing and board-control workflow. Pairing data and workspace files are
stored locally by the Android app. BLE communication is limited to the nearby
TitraLab board selected during pairing.

## Children and Classroom Use

The proof-of-concept release is intended for trusted internal testing with
colleagues and classroom hardware. Broader classroom deployment should be
managed by the responsible instructor or institution according to local privacy
and education policies.

## Changes

This policy may be updated as SciLabPro MicroPad adds features. Material changes
will be reflected by updating this page and the effective date.
