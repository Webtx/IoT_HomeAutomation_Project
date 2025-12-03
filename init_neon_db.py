import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import random
import math
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

def create_database():
    try:
        # Connect to Neon PostgreSQL
        conn = psycopg2.connect(
            os.getenv('DATABASE_URL'),
            cursor_factory=RealDictCursor
        )
        cursor = conn.cursor()
        
        # Drop existing tables if they exist
        cursor.execute('DROP TABLE IF EXISTS temperature_readings')
        cursor.execute('DROP TABLE IF EXISTS environmental_data')
        cursor.execute('DROP TABLE IF EXISTS motion_events')
        
        # Create environmental_data table for Lab 08 data
        cursor.execute('''
            CREATE TABLE environmental_data (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                temperature REAL,
                humidity REAL,
                pressure REAL
            )
        ''')
        
        # Create motion_events table for security data
        cursor.execute('''
            CREATE TABLE motion_events (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                count INTEGER NOT NULL DEFAULT 0
            )
        ''')
        
        print("✅ Database tables created successfully!")
        print("✅ environmental_data table ready for temperature, humidity, pressure")
        print("✅ motion_events table ready for motion detection counts")
        print("✅ Data will be populated when Raspberry Pi runs the monitoring scripts")
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    create_database()
