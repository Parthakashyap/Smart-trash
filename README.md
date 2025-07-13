
# Smart Trash Can using YOLOv8 and Raspberry Pi 5

## Real-Time Trash Classification & Automated Lid Control

---

## Project Overview

This project is a **smart trash bin system** using:

- **YOLOv8 (Ultralytics)** for real-time trash detection  
- **Pygame** for camera feed & visualization  
- **Raspberry Pi 5 GPIO** to control:
  - **3 Servos** (to open different trash bin lids)
  - **3 LEDs** (to indicate detection)

### Supported Trash Categories:

| Category | Trash Items Detected |
|---|---|
| **Book** | book |
| **Bottle** | bottle |
| **Organic Waste** | banana, apple, orange, vegetable, fruit, leftover food |

---

## Priority Logic

If multiple trash types are detected **in the same frame**, the system follows this priority:

1. **Book** (Highest Priority)  
2. **Bottle**  
3. **Organic Waste**

**Only the highest-priority detection triggers the servo & LED per frame.**

---

## System Workflow

1. **Run the Python script**  
2. The script:
   - Downloads the YOLOv8n model if not present  
   - Initializes the **Pi Camera** using GStreamer pipeline  
   - Runs object detection in real-time  
3. **Hardware Activation:**
   - When trash is detected, corresponding **LED turns ON**
   - **Servo opens the trash lid** (90°)  
   - Lid remains open for **10 seconds**, then closes automatically (0°)  

---

## Hardware Components

| Component | Quantity |
|---|---|
| **Raspberry Pi 5** | 1 |
| **Pi Camera (libcamera compatible)** | 1 |
| **Micro Servo Motors (SG90 / MG90)** | 3 |
| **LEDs (Different Colors Recommended)** | 3 |
| **Resistors (220Ω for LEDs)** | 3 |
| **External 5V Power Supply for Servos** | 1 |
| **Breadboard & Jumper Wires** | As needed |

---

## GPIO Pin Configuration

| Trash Type | **LED Pin (BCM)** | **Servo Pin (BCM)** |
|---|---|---|
| **Bottle** | 17 | 18 |
| **Book** | 22 | 23 |
| **Organic Waste** | 24 | 25 |

---

## Servo Control Details

| Action | Duty Cycle | Description |
|---|---|---|
| **Open Lid (90°)** | 7.5% | Trash bin opens |
| **Close Lid (0°)** | 2.5% | Trash bin closes |

**Note:** Servos run at **50Hz PWM**

---

## Wiring Diagram (Text)

### Servo Motor Wiring (Per Servo)

| Servo Wire | Connection |
|---|---|
| **Signal (Orange)** | GPIO 18 / 23 / 25 |
| **VCC (Red)** | **External 5V Power Supply** |
| **GND (Brown)** | **Common Ground with Pi** |

---

### LED Wiring (Per LED)

| LED Pin | Connection |
|---|---|
| **Anode (+)** | GPIO Pin via **220Ω resistor** |
| **Cathode (-)** | Pi Ground |

---

### Overall Wiring Summary

```
Raspberry Pi 5 GPIO:
-----------------------------
| GPIO 17 --> Bottle LED (+)
| GPIO 18 --> Bottle Servo Signal
| GPIO 22 --> Book LED (+)
| GPIO 23 --> Book Servo Signal
| GPIO 24 --> Organic LED (+)
| GPIO 25 --> Organic Servo Signal
| GND     --> All Servo Grounds + LED Grounds
| 5V      --> LEDs (with resistor) only
External 5V Power --> Servo VCC
-----------------------------
```

---

## Software Setup

### Install Dependencies

#### Install System Packages:

```bash
sudo apt update
sudo apt install python3-opencv libcamera-apps gstreamer1.0-plugins-good gstreamer1.0-tools libsdl2-dev libsdl2-image-dev
```

---

#### Install Python Packages

Create a `requirements.txt`:

```
ultralytics==8.0.204
pygame==2.5.2
numpy==1.26.4
opencv-python==4.9.0.80
RPi.GPIO==0.7.1
```

Install:

```bash
pip install -r requirements.txt
```

---

## Running the Project

```bash
python3 smart_trash_detector.py
```

---

## Autostart on Boot (Optional)

Create a systemd service:

```bash
sudo nano /etc/systemd/system/smart-trash.service
```

Paste the following:

```
[Unit]
Description=Smart Trash Can Detection Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/smart_trash_detector.py
WorkingDirectory=/home/pi
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable smart-trash.service
sudo systemctl start smart-trash.service
```

---

## Features Summary

- ✅ Real-time trash detection using YOLOv8n  
- ✅ Pi Camera input (optimized for Raspberry Pi 5 Bookworm)  
- ✅ Pygame live video display with bounding boxes  
- ✅ Priority-based lid opening (Book > Bottle > Organic)  
- ✅ Automatic lid closing after 10 seconds  
- ✅ Hardware integration with 3 servos & 3 LEDs  

---

## Safety Notes

- **Use external 5V power for servos.**  
  Do not power servos directly from the Pi’s 5V pin.  
- **Connect grounds together** (Pi GND ↔ Servo GND ↔ External Power GND)

---

## License

MIT License  
(c) 2025 Partha Pratim Kashyap
