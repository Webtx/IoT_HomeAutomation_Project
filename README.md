# CTRLHOUSE

## Team Members
- Student 1: Annie Yang
- Student 2: Sebastian

## Project Overview
This project implements a **Home Automation and Security System** using a **Raspberry Pi 5**.  
It integrates hardware and software to monitor home conditions, detect intrusions, and control devices remotely via a **dashboard**.

**Sensors Used:**
- PIR Motion Sensor (intrusion detection)
- DHT22 Temperature & Humidity Sensor
- Light Sensor (LDR)

**Actuators Used:**
- LEDs (visual indicators)
- Motor
- Relay-controlled device (Motor)

**Core Features:**
- Intrusion detection with instant alerts
- Temperature, humidity, and light monitoring
- Remote device control via MQTT dashboard
- Daily local data logging with automatic upload to cloud storage
- Clean packaging with cable management

---

## Features & Functionalities

### Real-Time Monitoring
- Detect motion using PIR sensor
- Capture last motion event timestamp and optionally trigger Pi Camera
- Monitor temperature, humidity, and light 

### Actuator Control
- Toggle LEDs, fan, and relay devices remotely

### Cloud Connectivity
- MQTT integration with **Adafruit IO**
- Live dashboard tiles for sensors and actuators
- Status indicators and mode selector (Home/Away/Night)

### Data Logging
- Logs stored locally in `data/` folder
- Daily file rotation with timestamped filenames (CSV format)
- Minimum fields: timestamp, sensor readings, actuator states, events

---

## Hardware Setup
- Raspberry Pi 5 
- GPIO pin connections:  
  - LED1 → GPIO 16  
  - LED2 → GPIO 23  
  - LED3 → GPIO 24  
  - Fan → GPIO 22  
  - Relay → GPIO 18  
  - PIR Motion Sensor → GPIO 17  
  - DHT11 Sensor → GPIO 4  
- Pi Camera Module V2 (optional for motion capture)  
- Wiring diagram and enclosure photos in `docs/`

<img width="693" height="530" alt="image" src="https://github.com/user-attachments/assets/d308bb2b-50cd-406b-b4ad-c932085d19a1" />


---
## Reflection

During this project, we successfully implemented a Home Automation and Security System using a Raspberry Pi. The system was able to monitor motion, temperature, humidity, and light levels while controlling actuators remotely through an MQTT dashboard.

The hardest part was integrating all modules—especially getting the PIR motion detection and camera capture working reliably together and pushing the code to github.
If we were to improve the project, we would improve error handling, improve organizations with files and folders and optimize data uploads.
## Software Setup

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/IoT_HomeAutomation_Project.git
cd IoT_HomeAutomation_Project
