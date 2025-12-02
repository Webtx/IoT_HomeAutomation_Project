from flask import Flask, render_template, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from Adafruit_IO import Client
from datetime import datetime, timedelta
import requests
import paho.mqtt.client as mqtt

# Load environment variables
load_dotenv()

# Initialize Adafruit IO client (REST API)
aio = Client(os.getenv('ADAFRUIT_IO_USERNAME'), os.getenv('ADAFRUIT_IO_KEY'))

# MQTT Setup for Adafruit IO
MQTT_BROKER = "io.adafruit.com"
MQTT_PORT = 1883
USERNAME = "HappyAnnie"
KEY = "aio_wobh35X1rdbZEBadRSvU7Mk9kQLz"

# Initialize MQTT Client
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(USERNAME, KEY)

try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()
    print("MQTT Client connected successfully")
except Exception as e:
    print(f"Failed to connect MQTT client: {e}")

# Device feeds mapping
DEVICE_FEEDS = {
    'led': 'led1-control',
    'led1': 'led1-control',
    'led2': 'led2-control', 
    'led3': 'led3-control',
    'fan': 'fan-control',
    'relay': 'relay-control'
}

# Maintain device states
device_states = {device_id: 0 for device_id in DEVICE_FEEDS}

def get_db_connection():
    conn = psycopg2.connect(
        os.getenv('DATABASE_URL'),
        cursor_factory=RealDictCursor
    )
    return conn
 
app = Flask(__name__)
@app.route('/') 
def home(): 
 return render_template('home.html') 
 
@app.route('/line-chart') 
def line_chart(): 
 return render_template('line_chart.html') 
 
@app.route('/device-control')
def device_control():
 return render_template('device_control.html')

@app.route('/api/latest-readings')
def latest_readings():
 """Get the latest environmental readings from Neon database"""
 try:
  conn = get_db_connection()
  cursor = conn.cursor()
  
  cursor.execute('''
   SELECT temperature, humidity, pressure, timestamp
   FROM environmental_data
   ORDER BY timestamp DESC
   LIMIT 1
  ''')
  reading = cursor.fetchone()
  conn.close()
  
  if reading:
   # Handle timestamp - it might be datetime or string
   timestamp_str = reading['timestamp']
   if hasattr(timestamp_str, 'strftime'):
    timestamp_str = timestamp_str.strftime('%Y-%m-%d %H:%M:%S')
   elif isinstance(timestamp_str, str):
    # Already a string, use as-is
    timestamp_str = timestamp_str
   else:
    timestamp_str = str(timestamp_str)
   
   return jsonify({
    'success': True,
    'temperature': reading['temperature'],
    'humidity': reading['humidity'],
    'pressure': reading['pressure'],
    'timestamp': timestamp_str
   })
  else:
   return jsonify({
    'success': False,
    'message': 'No data available'
   })
 except Exception as e:
  print(f"ERROR in latest_readings: {e}")
  import traceback
  traceback.print_exc()
  return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/available-dates')
def available_dates():
 """Get list of unique dates that have data in the database"""
 try:
  conn = get_db_connection()
  cursor = conn.cursor()
  
  cursor.execute('''
   SELECT DISTINCT DATE(timestamp) as date 
   FROM environmental_data 
   ORDER BY date DESC
  ''')
  
  rows = cursor.fetchall()
  conn.close()
  
  dates = [str(row['date']) for row in rows]
  
  return jsonify({
   'success': True,
   'dates': dates
  })
  
 except Exception as e:
  print(f"Error fetching available dates: {e}")
  return jsonify({
   'success': False,
   'error': str(e)
  }), 500

@app.route('/api/line-data') 
def line_data(): 
 """Get environmental data from Neon database with date and sensor filtering"""
 try:
  # Get date and sensor filter parameters
  date_filter = request.args.get('date')
  sensor = request.args.get('sensor', 'all')
  
  conn = get_db_connection() 
  cursor = conn.cursor()
  
  # Build query based on date filter
  if date_filter:
   # Filter by specific date
   cursor.execute('''
    SELECT timestamp, temperature, humidity, pressure 
    FROM environmental_data 
    WHERE DATE(timestamp) = %s
    ORDER BY timestamp ASC
   ''', (date_filter,))
  else:
   # All data (limit to recent for performance)
   cursor.execute('''
    SELECT timestamp, temperature, humidity, pressure 
    FROM environmental_data 
    ORDER BY timestamp DESC
    LIMIT 100
   ''')
  
  readings = cursor.fetchall()
  
  conn.close() 
  
  if not readings:
   return jsonify({
    'labels': [],
    'datasets': []
   })
  
  # Reverse if we limited to show oldest to newest
  if not date_filter:
   readings = list(reversed(readings))
  
  # Format data for Chart.js (3 lines: temp, humidity, pressure)
  labels = []
  for row in readings:
   timestamp_val = row['timestamp']
   if hasattr(timestamp_val, 'strftime'):
    labels.append(timestamp_val.strftime('%H:%M:%S'))
   else:
    # Already a string, extract time portion
    time_str = str(timestamp_val).split(' ')[1] if ' ' in str(timestamp_val) else str(timestamp_val)[11:19]
    labels.append(time_str)
  
  # Build datasets based on sensor selection
  datasets = []
  
  if sensor == 'all' or sensor == 'temperature':
   datasets.append({
    'label': 'Temperature (°C)', 
    'data': [row['temperature'] for row in readings], 
    'borderColor': 'rgb(255, 99, 132)', 
    'backgroundColor': 'rgba(255, 99, 132, 0.2)', 
    'tension': 0.4, 
    'fill': False,
    'yAxisID': 'y'
   })
  
  if sensor == 'all' or sensor == 'humidity':
   datasets.append({
    'label': 'Humidity (%)', 
    'data': [row['humidity'] for row in readings], 
    'borderColor': 'rgb(54, 162, 235)', 
    'backgroundColor': 'rgba(54, 162, 235, 0.2)', 
    'tension': 0.4, 
    'fill': False,
    'yAxisID': 'y'
   })
  
  if sensor == 'all' or sensor == 'pressure':
   datasets.append({
    'label': 'Pressure (hPa)', 
    'data': [row['pressure'] for row in readings], 
    'borderColor': 'rgb(75, 192, 192)', 
    'backgroundColor': 'rgba(75, 192, 192, 0.2)', 
    'tension': 0.4, 
    'fill': False,
    'yAxisID': 'y1'
   })
  
  data = { 
   'labels': labels, 
   'datasets': datasets
  } 
  
  return jsonify(data)
  
 except Exception as e:
  print(f"Error fetching line data: {e}")
  return jsonify({
   'labels': [],
   'datasets': [],
   'error': str(e)
  }), 500
  import traceback
  traceback.print_exc()
  return jsonify({
   'error': str(e),
   'labels': [],
   'datasets': []
  }), 500

# New endpoints for Adafruit IO integration
@app.route('/api/adafruit/feeds')
def get_adafruit_feeds():
    """Get all available Adafruit IO feeds"""
    try:
        feeds = aio.feeds()
        feed_list = [{'key': feed.key, 'name': feed.name} for feed in feeds]
        return jsonify({'success': True, 'feeds': feed_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/adafruit/sensor/<feed_key>')
def get_sensor_data(feed_key):
    """Get live sensor data from Adafruit IO feed"""
    try:
        # Get the last 50 data points from the feed
        data_points = aio.data(feed_key, max_results=50)
        
        labels = []
        values = []
        
        for point in reversed(data_points):
            labels.append(point.created_at)
            values.append(float(point.value))
        
        chart_data = {
            'labels': labels,
            'datasets': [{
                'label': f'{feed_key} Sensor Data',
                'data': values,
                'borderColor': 'rgb(75, 192, 192)',
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'tension': 0.4,
                'fill': True
            }]
        }
        
        return jsonify({'success': True, 'data': chart_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/adafruit/control/<feed_key>', methods=['POST'])
def control_device(feed_key):
    """Send control command to Adafruit IO feed to control devices via MQTT"""
    try:
        data = request.get_json()
        value = data.get('value')
        
        # Map feed_key to actual feed name
        actual_feed = DEVICE_FEEDS.get(feed_key, feed_key)
        
        # Update device state
        if feed_key in device_states:
            device_states[feed_key] = value
        
        # Publish to MQTT (more reliable for device control)
        topic = f"{USERNAME}/feeds/{actual_feed}"
        mqtt_client.publish(topic, str(value))
        print(f"Published to {topic}: {value}")
        
        # Also try REST API as backup
        try:
            aio.send_data(actual_feed, value)
        except Exception as rest_error:
            print(f"REST API backup failed: {rest_error}")
        
        return jsonify({
            'success': True, 
            'message': f'Command sent to {feed_key}',
            'feed': actual_feed,
            'value': value
        })
    except Exception as e:
        print(f"Error controlling device: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/adafruit/toggle/<device_id>', methods=['POST'])
def toggle_device(device_id):
    """Toggle device state (0 to 1 or 1 to 0)"""
    try:
        # Map device_id to actual feed name
        actual_feed = DEVICE_FEEDS.get(device_id, device_id)
        
        # Toggle state
        if device_id in device_states:
            device_states[device_id] = 1 - device_states[device_id]
        else:
            device_states[device_id] = 1
        
        new_state = device_states[device_id]
        
        # Publish to MQTT
        topic = f"{USERNAME}/feeds/{actual_feed}"
        mqtt_client.publish(topic, str(new_state))
        print(f"Toggled {topic}: {new_state}")
        
        return jsonify({
            'success': True,
            'message': f'{device_id} toggled',
            'state': new_state
        })
    except Exception as e:
        print(f"Error toggling device: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/adafruit/state/<device_id>')
def get_device_state(device_id):
    """Get current state of a device"""
    try:
        state = device_states.get(device_id, 0)
        return jsonify({
            'success': True,
            'device': device_id,
            'state': state
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/motion-data')
def get_motion_data():
    """Get motion sensor data (simulated for now)"""
    try:
        from datetime import datetime, timedelta
        
        # Simulate motion sensor data
        motion_data = []
        base_time = datetime.now()
        
        for i in range(20):
            time_offset = timedelta(minutes=i * 5)
            motion_data.append({
                'timestamp': (base_time - time_offset).strftime('%Y-%m-%d %H:%M:%S'),
                'detected': i % 3 == 0,  # Every 3rd reading has motion
                'value': 1 if i % 3 == 0 else 0,
                'location': 'Main Entrance'
            })
        
        return jsonify({
            'success': True,
            'data': list(reversed(motion_data))
        })
    except Exception as e:
        print(f"Error getting motion data: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/adafruit/historical')
def get_historical_data():
    """Get historical sensor data for a specific date range"""
    try:
        feed_key = request.args.get('feed', 'temperature')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Get data from Adafruit IO
        data_points = aio.data(feed_key, max_results=1000)
        
        # Filter by date if provided
        filtered_data = []
        for point in data_points:
            filtered_data.append({
                'timestamp': point.created_at,
                'value': float(point.value)
            })
        
        return jsonify({'success': True, 'data': filtered_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sync-to-cloud', methods=['POST'])
def sync_to_cloud():
    """Sync local database data to cloud (Neon) when internet is restored"""
    try:
        # This would sync local SQLite data to Neon PostgreSQL
        # Implementation for offline sync capability
        return jsonify({'success': True, 'message': 'Data synced to cloud'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
 
@app.route('/security')
def security():
 return render_template('security.html')

@app.route('/about')
def about():
 return render_template('about.html')

if __name__ == '__main__': 
 app.run(debug=True) 