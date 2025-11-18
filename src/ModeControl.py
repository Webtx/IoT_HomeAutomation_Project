from gpiozero import LED
import time
import random
import threading

# -----------------------
# Device Setup
# -----------------------
DEVICES = {
    'led1': {'device': LED(16), 'name': 'Yellow Led', 'state': False},
    'led2': {'device': LED(23), 'name': 'Red Led', 'state': False},
    'led3': {'device': LED(24), 'name': 'Green Led', 'state': False},
    'fan':  {'device': LED(22), 'name': 'Fan', 'state': False},   # LED as generic output
    'relay':{'device': LED(18), 'name': 'Relay', 'state': False}  # LED as generic output
}

# Party mode control
party_mode_active = False
party_thread = None

# -----------------------
# Functions
# -----------------------
def show_menu():
    print("\n=== DEVICE CONTROL MENU ===")
    print("Select a device to toggle:")
    for idx, (device_id, device) in enumerate(DEVICES.items(), start=1):
        state_str = "ON" if device['state'] else "OFF"
        print(f"  {idx}. {device['name']} ({state_str})")
    print("\nOther commands:")
    print("  s - Show status")
    print("  a - Turn ALL ON")
    print("  o - Turn ALL OFF")
    print("  p - Toggle Party Mode 🎉")
    print("  q - Quit")

def toggle_device(device_id):
    device_entry = DEVICES[device_id]
    device_entry['state'] = not device_entry['state']
    if device_entry['state']:
        device_entry['device'].on()
    else:
        device_entry['device'].off()
    print(f"✓ {device_entry['name']} turned {'ON' if device_entry['state'] else 'OFF'}")

def show_status():
    print("\n--- Current Status ---")
    for device_id, device in DEVICES.items():
        state_str = "ON" if device['state'] else "OFF"
        print(f"  {device['name']}: {state_str}")

def turn_all(state):
    for device_id, device in DEVICES.items():
        device['state'] = state
        if state:
            device['device'].on()
        else:
            device['device'].off()
    print(f"✓ All devices turned {'ON' if state else 'OFF'}")

def party_mode():
    global party_mode_active
    led_devices = ['led1', 'led2', 'led3']
    print("🎉 PARTY MODE ACTIVATED! 🎉")
    print("Press 'p' again to stop...")
    
    while party_mode_active:
        pattern = random.choice(['random', 'sequence', 'strobe', 'wave'])
        
        if pattern == 'random':
            for _ in range(10):
                if not party_mode_active:
                    break
                led = random.choice(led_devices)
                state = random.choice([True, False])
                DEVICES[led]['state'] = state
                if state:
                    DEVICES[led]['device'].on()
                else:
                    DEVICES[led]['device'].off()
                time.sleep(0.1)
        
        elif pattern == 'sequence':
            for led in led_devices:
                if not party_mode_active:
                    break
                DEVICES[led]['state'] = True
                DEVICES[led]['device'].on()
                time.sleep(0.2)
                DEVICES[led]['state'] = False
                DEVICES[led]['device'].off()
        
        elif pattern == 'strobe':
            for _ in range(5):
                if not party_mode_active:
                    break
                for led in led_devices:
                    DEVICES[led]['state'] = True
                    DEVICES[led]['device'].on()
                time.sleep(0.1)
                for led in led_devices:
                    DEVICES[led]['state'] = False
                    DEVICES[led]['device'].off()
                time.sleep(0.1)
        
        elif pattern == 'wave':
            for led in led_devices + led_devices[::-1]:
                if not party_mode_active:
                    break
                DEVICES[led]['state'] = True
                DEVICES[led]['device'].on()
                time.sleep(0.15)
                DEVICES[led]['state'] = False
                DEVICES[led]['device'].off()
    
    for led in led_devices:
        DEVICES[led]['state'] = False
        DEVICES[led]['device'].off()
    
    print("🎉 Party mode stopped")

def toggle_party_mode():
    global party_mode_active, party_thread
    if party_mode_active:
        party_mode_active = False
        if party_thread:
            party_thread.join()
    else:
        party_mode_active = True
        party_thread = threading.Thread(target=party_mode, daemon=True)
        party_thread.start()

def cleanup():
    global party_mode_active
    party_mode_active = False
    print("\nCleaning up GPIO...")
    for device in DEVICES.values():
        device['device'].off()
    print("Goodbye!")

# -----------------------
# Main Loop
# -----------------------
def main():
    device_keys = list(DEVICES.keys())
    try:
        while True:
            show_menu()
            choice = input("\nEnter command: ").strip().lower()
            
            if choice == 'q':
                break
            elif choice == 's':
                show_status()
            elif choice == 'a':
                turn_all(True)
            elif choice == 'o':
                turn_all(False)
            elif choice == 'p':
                toggle_party_mode()
            elif choice.isdigit() and 1 <= int(choice) <= len(DEVICES):
                device_id = device_keys[int(choice) - 1]
                toggle_device(device_id)
            else:
                print("❌ Invalid command!")
            
            time.sleep(0.3)
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    finally:
        cleanup()

if __name__ == '__main__':
    main()
