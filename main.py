import os
import urllib.request
import cv2
from ultralytics import YOLO
import numpy as np
import pygame
import RPi.GPIO as GPIO
import time
import threading

# GPIO Setup
GPIO.setmode(GPIO.BCM)

LED_PINS = {
    "bottle": 17,
    "book": 22,
    "organic": 24
}

SERVO_PINS = {
    "bottle": 18,
    "book": 23,
    "organic": 25
}

for led in LED_PINS.values():
    GPIO.setup(led, GPIO.OUT)

for servo in SERVO_PINS.values():
    GPIO.setup(servo, GPIO.OUT)

servo_pwms = {name: GPIO.PWM(pin, 50) for name, pin in SERVO_PINS.items()}

for pwm in servo_pwms.values():
    pwm.start(0)

# Trash Categories
TRASH_CLASSES = {
    "bottle": ["bottle"],
    "book": ["book"],
    "organic": ["banana", "apple", "orange", "vegetable", "fruit", "leftover food"]
}

# Priority Order
PRIORITY = ["book", "bottle", "organic"]

# YOLO Model setup
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "yolov8n.pt")
MODEL_URL = "https://github.com/ultralytics/assets/releases/download/v8.0.0/yolov8n.pt"

def download_model():
    if not os.path.exists(MODEL_PATH):
        os.makedirs(MODEL_DIR, exist_ok=True)
        print("[INFO] Downloading YOLOv8 model...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("[INFO] Model downloaded.")
    else:
        print("[INFO] YOLO model found locally.")

def get_pi_camera_capture(width=640, height=480, framerate=30):
    pipeline = (
        f"libcamerasrc ! "
        f"video/x-raw,width={width},height={height},framerate={framerate}/1 ! "
        f"videoconvert ! appsink"
    )
    cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
    if not cap.isOpened():
        raise Exception("[ERROR] Cannot open Pi Camera.")
    return cap

def activate_output(trash_type):
    led_pin = LED_PINS[trash_type]
    servo_pwm = servo_pwms[trash_type]

    print(f"[ACTION] Activating {trash_type} output.")

    GPIO.output(led_pin, GPIO.HIGH)
    servo_pwm.ChangeDutyCycle(7.5)  # Open servo

    def reset_outputs():
        time.sleep(10)
        servo_pwm.ChangeDutyCycle(2.5)  # Close servo
        GPIO.output(led_pin, GPIO.LOW)

    threading.Thread(target=reset_outputs).start()

def get_trash_type(label):
    for trash_type, class_list in TRASH_CLASSES.items():
        if label in class_list:
            return trash_type
    return None

def process_detections(results, scale_w, scale_h, surface):
    font = pygame.font.SysFont(None, 24)
    detected_types = set()

    for box in results[0].boxes:
        class_idx = int(box.cls[0])
        label = results[0].names[class_idx]
        conf = box.conf[0].cpu().numpy()

        trash_type = get_trash_type(label)
        if trash_type:
            detected_types.add(trash_type)

            xyxy = box.xyxy[0].cpu().numpy()
            x1, y1, x2, y2 = xyxy

            x1, y1, x2, y2 = x1 * scale_w, y1 * scale_h, x2 * scale_w, y2 * scale_h

            pygame.draw.rect(surface, (0, 255, 0), pygame.Rect(x1, y1, x2 - x1, y2 - y1), 2)

            text = f"{label} {conf:.2f}"
            text_surface = font.render(text, True, (255, 255, 255))
            surface.blit(text_surface, (x1, y1 - 20))

    # Activate highest priority output only
    for priority_type in PRIORITY:
        if priority_type in detected_types:
            activate_output(priority_type)
            break

def main():
    download_model()
    model = YOLO(MODEL_PATH)

    pygame.init()
    window_size = (640, 480)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption("Smart Trash Can - Raspberry Pi 5 (Priority Mode)")

    cap = get_pi_camera_capture()

    try:
        running = True
        while running:
            ret, frame = cap.read()
            if not ret:
                continue

            results = model.predict(frame, conf=0.5, verbose=False)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_surface = pygame.surfarray.make_surface(np.flipud(np.rot90(frame_rgb)))

            screen.blit(pygame.transform.scale(frame_surface, window_size), (0, 0))

            h, w, _ = frame.shape
            scale_w, scale_h = window_size[0] / w, window_size[1] / h

            process_detections(results, scale_w, scale_h, screen)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

    finally:
        cap.release()
        pygame.quit()
        for pwm in servo_pwms.values():
            pwm.stop()
        GPIO.cleanup()
        print("[INFO] Program terminated. GPIO cleaned up.")

if __name__ == "__main__":
    main()
