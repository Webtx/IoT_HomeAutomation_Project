from picamera2 import Picamera2
import cv2
# Initialize Pi Camera
picam2 = Picamera2()
picam2.start()
print("Pi Camera started. Press 'q' to quit.")
while True:
 # Capture frame
 frame = picam2.capture_array()
 # Show frame
 cv2.imshow("Raspberry Pi Camera", frame)
 # Press 'q' to exit
 if cv2.waitKey(1) & 0xFF == ord('q'):
     break
picam2.stop()
cv2.destroyAllWindows() 
