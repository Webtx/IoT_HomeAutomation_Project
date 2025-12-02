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
        
        print("✅ Database tables created successfully!")
        print("✅ Ready for Lab 08 environmental data (temperature, humidity, pressure)")
        print("✅ Data will be populated when Raspberry Pi runs lab08_domisafe_remote.py")
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    create_database()
