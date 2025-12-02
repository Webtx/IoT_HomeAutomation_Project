# CTRLHOUSE - IoT Dashboard System

## 🏗️ System Architecture (from PDF)

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  Raspberry Pi   │ ──MQTT─→│   Adafruit IO    │←──HTTP──│  Render Web App │
│  (Teammate)     │         │   (Cloud Bridge) │         │   (Your UI)     │
└────────┬────────┘         └─────────┬────────┘         └─────────────────┘
         │                            │                            ↑
         │ SQL Inserts                │ Historical Data            │
         ↓                            ↓                            │
┌─────────────────────────────────────────────────────────────────┘
│            Neon PostgreSQL Database (Cloud)
└──────────────────────────────────────────────────────────────────

```

## 📋 How It Works

### **1. Raspberry Pi (Your Teammate's Side)**
- Runs `raspberry_pi_controller.py`
- Reads real sensors (temperature, humidity, light)
- Controls physical devices (LED, fan, relay)
- **Sends** sensor data → Adafruit IO
- **Receives** control commands ← Adafruit IO
- Saves historical data → Neon database

### **2. Adafruit IO (Cloud Middleware)**
- **The magic connector!**
- Stores live sensor feeds
- Stores control commands
- Allows **remote control** from anywhere
- MQTT protocol for real-time communication

### **3. Your Render Web App (UI)**
- Beautiful liquid glass interface
- **Anyone can access** from any computer
- **You control from your laptop:**
  - Click "Turn LED ON" → sends to Adafruit IO → Pi receives → LED turns on
- **You view sensors:**
  - Pi sends temp → Adafruit IO → Your UI displays it
- Shows historical data from Neon database

### **4. Neon Database**
- Stores all sensor readings permanently
- Query historical trends (last 24 hours, week, month)
- **Offline backup**: When internet fails:
  - Pi saves to local SQLite
  - When online again, sync to Neon

## 🚀 Setup Instructions

### **For Your Teammate (Raspberry Pi):**

1. **Install dependencies on Pi:**
```bash
pip3 install Adafruit_IO psycopg2-binary RPi.GPIO Adafruit_DHT
```

2. **Run the controller:**
```bash
python3 raspberry_pi_controller.py
```

3. **That's it!** Leave it running. It will:
   - Send sensor data every 5 seconds
   - Listen for your control commands
   - Log everything to database

### **For You (Web Interface):**

1. **Deploy to Render:**
   - Push code to GitHub: `seblxx/renderdeploytest`
   - Create Web Service on Render
   - Add environment variables:
     - `DATABASE_URL`: (Neon connection string)
     - `ADAFRUIT_IO_USERNAME`: HappyAnnie
     - `ADAFRUIT_IO_KEY`: aio_KvJv15bgUedgLJzUU6u17NKSyEar

2. **Access from ANY computer:**
   - Go to `https://your-app.onrender.com`
   - View live sensor data
   - Control devices remotely!

## 🎮 Remote Control - How It Works

**Example: You want to turn on the LED from your laptop at home**

1. **You**: Click "Turn ON" button in browser
2. **Your UI** (Render): Sends HTTP POST to `/api/adafruit/control/led` with value=1
3. **Flask App**: Calls `aio.send_data('led', 1)` to Adafruit IO
4. **Adafruit IO**: Broadcasts to all MQTT subscribers
5. **Raspberry Pi**: Receives command via MQTT callback
6. **Pi**: Runs `control_led(1)` → GPIO output HIGH → **LED turns on!**

**The whole process takes ~500ms!**

## 📊 What Each Component Does

| Component | Purpose | Why Needed (from PDF) |
|-----------|---------|----------------------|
| **Raspberry Pi** | Physical device controller | Controls real sensors/devices in the house |
| **Adafruit IO** | Cloud MQTT broker | Allows remote control over internet |
| **Render Flask** | Web interface | Beautiful UI for monitoring & control |
| **Neon Database** | Historical storage | View past data trends, offline backup |

## 🔧 PDF Requirements Checklist

✅ Pi sends sensor data to Adafruit IO
✅ Pi sends sensor data to Neon database
✅ Flask app shows live data from **at least 3 sensors**
✅ Flask app controls **at least 3 devices**
✅ Flask app plots historical data (date selection)
✅ Handles offline mode (SQLite backup + sync)
✅ Nice CSS look (liquid glass design!)
✅ Deployed on Render.com

## 🎯 Answer to Your Questions

**Q: Can I control the house from my computer?**
**A:** YES! That's the whole point! Adafruit IO is the bridge. Your teammate's Pi listens to Adafruit IO. You send commands via your web UI → Adafruit IO → Pi executes.

**Q: Should I send her the UI?**
**A:** NO! That's the beauty of Render. You deploy once, **everyone can access** the same URL from any computer. She can also control from her phone!

**Q: What does Neon do?**
**A:** Two things:
1. **Long-term storage** - View temperature graph from last week
2. **Offline backup** - If Pi loses internet, saves locally, syncs later

**Q: Does our current setup work?**
**A:** Yes! Just need your teammate to run `raspberry_pi_controller.py` on the Pi. Then your Render UI will work perfectly.

## 🌐 Access Points

- **Your Render UI**: `https://ctrlhouse.onrender.com` (example)
- **Adafruit IO Dashboard**: `https://io.adafruit.com/HappyAnnie`
- **Neon Database**: Already connected via app.py

## 📝 Notes

- **No need to be on same WiFi** - everything is cloud-based!
- **Works from anywhere** - even different countries
- **Multiple users** - You, your teammate, your professor can all access simultaneously
- **Always on** - Pi stays running, you access UI whenever needed
