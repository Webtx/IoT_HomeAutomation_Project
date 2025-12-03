# CTRLHOUSE - IoT Home Automation Dashboard

🌐 **Live Website**: [https://ctrlhouse-v.onrender.com](https://ctrlhouse-v.onrender.com)

🎥 **Project Demo**: [Watch on YouTube](https://youtube.com/shorts/5ctSFgjcPUs?feature=share)

## 📖 Overview

CTRLHOUSE is a comprehensive IoT home automation system that allows you to monitor environmental conditions and control smart home devices through an elegant web interface. The system combines real-time sensor data, device control, and security monitoring in one unified dashboard.

## 🎯 What Does This App Do?

The CTRLHOUSE app provides three main functionalities:

### 1. **Environmental Monitoring**
- View real-time temperature, humidity, and pressure readings
- Visualize historical sensor data with interactive charts
- Navigate through individual readings to analyze trends
- Filter data by specific dates

### 2. **Device Control**
- Control smart home devices remotely (LED lights, fans, relays)
- Toggle devices on/off with simple button clicks
- Real-time status updates for all connected devices
- Works from anywhere with internet connection

### 3. **Security System**
- Enable/disable security monitoring
- View motion detection events
- Navigate through security history
- Real-time motion status updates

## 🏗️ System Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  Raspberry Pi   │ ──MQTT─→│   Adafruit IO    │←──HTTP──│    Flask App    │
│   (Sensors &    │         │   (Cloud MQTT)   │         │   (Web Server)  │
│    Devices)     │         │                  │         │                 │
└────────┬────────┘         └──────────────────┘         └────────┬────────┘
         │                                                          │
         │ SQL Inserts                                             │ SQL Queries
         ↓                                                          ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                    Neon PostgreSQL Database (Cloud)                       │
│                   - Environmental Data                                    │
│                   - Device States                                         │
│                   - Security Events                                       │
└──────────────────────────────────────────────────────────────────────────┘
```

## 🌐 How to Navigate the Website

### **Home Page** (`/`)
Your landing page with an overview of the system:
- **Live Sensor Readings**: See current temperature, humidity, and pressure at a glance
- **Quick Links**: Three cards that take you to different sections
  - Environmental Monitoring → View detailed charts
  - Device Control → Control your smart devices
  - Security System → Manage home security

### **Environmental Data** (`/line-chart`)
Monitor and analyze environmental conditions:
- **Interactive Chart**: View temperature, humidity, and pressure trends
- **Current Readings**: Three boxes showing latest sensor values
- **Navigation Controls**: 
  - Use "Previous" and "Next" buttons to browse individual readings
  - See timestamp and reading position (e.g., "10 of 33")
- **Statistics**: View temperature statistics (average, min, max, range)

### **Device Control** (`/device-control`)
Control your smart home devices:
- **Device Cards**: Each device has its own control card
  - LED Control: Toggle LED on/off
  - Fan Control: Turn fan on/off
  - Relay Control: Switch relay states
- **Status Indicators**: See if devices are currently ON or OFF
- **Instant Control**: Click once to toggle, changes happen immediately

### **Security** (`/security`)
Manage your home security system:
- **System Control**: 
  - Enable/disable the entire security system
  - Status indicator shows current state (ENABLED/DISABLED)
- **Motion Detection**:
  - Current motion status display
  - Last motion detection timestamp
- **History Navigation**:
  - Browse through all motion detection events
  - See detailed information (motion detected yes/no, sensor value, location)
  - Navigate with Previous/Next buttons

### **About** (`/about`)
Learn about the project:
- Project description and purpose
- Key features overview
- Technology stack used
- Project team information

## 🚀 Getting Started

### Prerequisites
- Python 3.13+
- Virtual environment (venv)
- Neon PostgreSQL database
- Adafruit IO account

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Webtx/IoT_HomeAutomation_Project.git
cd IoT_HomeAutomation_Project
```

2. **Create and activate virtual environment**
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create a `.env` file with:
```
DATABASE_URL=your_neon_postgresql_connection_string
ADAFRUIT_IO_USERNAME=your_username
ADAFRUIT_IO_KEY=your_api_key
```

5. **Initialize the database**
```bash
python init_neon_db.py
```

6. **Run the application**
```bash
python app.py
```

7. **Access the app**
Open your browser and go to `http://127.0.0.1:5000`

## 📊 Database Structure

### Tables

**environmental_data**
- `id`: Primary key
- `temperature`: Float (°C)
- `humidity`: Float (%)
- `pressure`: Float (hPa)
- `timestamp`: Timestamp

**device_status**
- `id`: Primary key
- `device_name`: String
- `status`: String (ON/OFF)
- `timestamp`: Timestamp

**security_data**
- `id`: Primary key
- `motion_detected`: Integer
- `timestamp`: Timestamp

## 🔌 API Endpoints

### Environmental Data
- `GET /api/latest-readings` - Get latest sensor readings
- `GET /api/line-data?date=YYYY-MM-DD&sensor=all` - Get historical data
- `GET /api/available-dates` - Get dates with available data

### Device Control
- `POST /api/adafruit/control/<device_id>` - Send control command
- `POST /api/adafruit/toggle/<device_id>` - Toggle device state
- `GET /api/adafruit/state/<device_id>` - Get device state

### Security
- `GET /api/motion-data` - Get motion detection history

## 🎨 Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Sensor data updates every 30 seconds
- **Glassmorphism UI**: Modern liquid glass design
- **Dark Theme**: Easy on the eyes with black background
- **Interactive Charts**: Powered by Chart.js
- **Remote Control**: Control devices from anywhere

## 🛠️ Technologies Used

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **Database**: PostgreSQL (Neon)
- **IoT Platform**: Adafruit IO (MQTT)
- **Charts**: Chart.js
- **Deployment**: Render.com

## 📝 Project Structure

```
IoT_HomeAutomation_Project/
├── app.py                      # Main Flask application
├── init_neon_db.py            # Database initialization
├── requirements.txt           # Python dependencies
├── runtime.txt               # Python version
├── Procfile                  # Render deployment config
├── .env                      # Environment variables (not in git)
├── static/
│   ├── styles.css           # Global styles
│   └── line_chart.js        # Chart functionality
├── templates/
│   ├── base.html            # Base template
│   ├── home.html            # Home page
│   ├── line_chart.html      # Environmental monitoring
│   ├── device_control.html  # Device control
│   ├── security.html        # Security system
│   └── about.html           # About page
└── src/
    ├── environmental_module.py
    ├── device_control_module.py
    ├── security_module.py
    └── ModeControl.py
```

## 🌟 Key Features Explained

### Real-time Sensor Monitoring
The system continuously monitors environmental conditions using sensors connected to a Raspberry Pi. Data is sent to the cloud database and displayed on the web interface with automatic updates.

### Remote Device Control
Using Adafruit IO's MQTT protocol, you can control devices from anywhere in the world. When you click a button on the web interface, a command is sent through the cloud to your Raspberry Pi, which then controls the physical device.

### Security Monitoring
The security system can be enabled or disabled through the web interface. When enabled, motion sensors detect activity and log all events with timestamps for review.

## 🔒 Security Notes

- Always use environment variables for sensitive data
- Never commit `.env` file to version control
- Use strong passwords for database and API keys
- Keep dependencies updated

## Reflexion ##
The part that worked best was controlling the LEDs, fan, and relay remotely using MQTT. The hardest part was figuring out how MQTT communication works and making sure messages are received and sent correctly. Connecting Flask and rendering the front-end was also tricky, especially keeping the web interface in sync with device states. We struggled a bit with avoiding message loops. If We were to improve this project, We would focus on handling better the MQTT messages. Overall, we learned a lot about IoT communication, device control, and integrating Python with web technologies.

## 📧 Support

For questions or issues, please open an issue on GitHub.

---

**CTRLHOUSE** - Control your smart home from anywhere with cutting-edge IoT technology.
