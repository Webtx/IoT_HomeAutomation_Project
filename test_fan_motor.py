import time
import board
import digitalio

# Define LED pins
led_pins = [board.D22, board.D23, board.D24, board.D16]

# Initialize LEDs
leds = []
for pin in led_pins:
    led = digitalio.DigitalInOut(pin)
    led.direction = digitalio.Direction.OUTPUT
    leds.append(led)

print("Testing LEDs on GPIO 23, 24, and 16...")

# Turn all LEDs ON (True)
print("Turning LEDs ON")
for led in leds:
    led.value = True
time.sleep(4)

# Turn all LEDs OFF (False)
print("Turning LEDs OFF")
for led in leds:
    led.value = False
time.sleep(2)

# Clean up
for led in leds:
    led.deinit()

print("Test complete.")
