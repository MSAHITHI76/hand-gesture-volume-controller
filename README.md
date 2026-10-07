<<<<<<< HEAD
# Hand Gesture Volume Controller

A real-time Computer Vision desktop application built in Python that allows users to control their Windows laptop's master system volume using hand gestures captured through the built-in webcam.

No external hardware is required.

---

## Description

The application processes frames captured from the webcam, detects hand landmarks using MediaPipe, and measures the 2D Euclidean distance between the tip of the thumb and the tip of the index finger. That distance is continuously mapped to system volume level (0% to 100%) on Windows using the Pycaw library.

An Exponential Moving Average (EMA) algorithm smooths hand movement fluctuations, while a dead-zone threshold prevents unnecessary Windows volume API spamming.

---

## Features

* **Real-Time Hand Tracking**: Tracks 21 3D hand landmarks at high camera frame rates.
* **Intuitive Gesture Control**: Pinching thumb and index finger together decreases volume; spreading them apart increases volume.
* **Smooth Volume Adjustment**: Exponential moving average prevents jittery or abrupt volume spikes.
* **Dead-Zone Thresholding**: Updates Windows system volume only when volume changes noticeably.
* **Visual On-Screen UI**: Real-time camera display featuring skeleton overlays, pinch distance line, volume percentage, and a dynamic volume bar.
* **Clean Webcam Handling**: Handles missing hands or camera disconnection gracefully without crashing.

---

## How It Works

```text
Webcam
↓
OpenCV
↓
MediaPipe
↓
Hand Landmarks
↓
Thumb-Index Distance
↓
Smoothing
↓
Volume Mapping
↓
Windows System Volume
```

---

## Tech Stack

* **Python 3.x**
* **OpenCV (`opencv-python`)**: Video capture, image transformations, and on-screen graphics.
* **MediaPipe (`mediapipe`)**: Machine learning framework for hand skeleton tracking and landmark extraction.
* **Pycaw & Comtypes (`pycaw`, `comtypes`)**: Direct integration with Windows Core Audio APIs (`IAudioEndpointVolume`).
* **NumPy (`numpy`)**: Mathematical mapping and matrix calculations.

---

## Project Structure

```text
hand-gesture-volume-controller/
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Requirements

* **Operating System**: Windows 10 / Windows 11
* **Python**: Python 3.8+ (Python 3.11 recommended)
* **Hardware**: Built-in or USB webcam, Speakers/Headphones

---

## Installation

1. **Clone or Open the Repository**:
   ```bash
   cd hand-gesture-volume-controller
   ```

2. **Create a Virtual Environment (Optional but Recommended)**:
   ```bash
   python -m venv .venv
   ```

3. **Activate Virtual Environment on Windows**:
   ```cmd
   .venv\Scripts\activate
   ```
   *For PowerShell:*
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## How to Run

Execute the main script:

```bash
python main.py
```

---

## Controls

* **Increase Volume**: Spread your thumb tip and index finger tip apart.
* **Decrease Volume**: Pinch your thumb tip and index finger tip together.
* **Quit Application**: Press the `q` key on your keyboard while the camera window is focused.

---

## Troubleshooting

* **Webcam Error**: Ensure no other application (Zoom, Teams, Skype, or Camera app) is using the webcam.
* **Audio Control Warning**: Verify that Pycaw and Comtypes are installed properly (`pip install pycaw comtypes`).
* **Hand Detection Lag**: Ensure proper lighting in the room and keep your hand clearly visible within the camera's field of view.
=======
# hand-gesture-volume-controller
>>>>>>> e0697fe43a6a56fd1738c42cb9d8361ae08c1bf8
