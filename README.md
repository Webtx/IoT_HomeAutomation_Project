# IoT Home Automation & Security System

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
- Monitor temperature, humidity, and light level

### Actuator Control
- Toggle LEDs, fan, and relay devices remotely
- Party mode: random LED patterns (demo feature)

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
- Raspberry Pi 4B 2GB+ with Raspberry Pi OS (64-bit)
- GPIO pin connections:  
  - LED1 → GPIO 16  
  - LED2 → GPIO 23  
  - LED3 → GPIO 24  
  - Fan → GPIO 22  
  - Relay → GPIO 18  
  - PIR Motion Sensor → GPIO 17  
  - DHT22 Sensor → GPIO 4  
- Pi Camera Module V2 (optional for motion capture)  
- Wiring diagram and enclosure photos in `docs/`

---

## Software Setup

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/IoT_HomeAutomation_Project.git
cd IoT_HomeAutomation_Project
