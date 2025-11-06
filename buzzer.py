from gpiozero import TonalBuzzer
from gpiozero.tones import Tone
import time

BUZZER_PIN = 7  # your GPIO pin

buzzer = TonalBuzzer(BUZZER_PIN)

try:
    print("Buzzer sweep test")
    for freq in [261, 329, 392, 523]:  # C4, E4, G4, C5
        buzzer.play(Tone(freq))
        time.sleep(1)
    buzzer.stop()
    print("Test finished")
finally:
    buzzer.close()
