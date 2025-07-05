import numpy as np
import cv2
from cvzone.HandTrackingModule import HandDetector
import pyautogui
import time
from deepface import DeepFace
import threading

emotion = None
latest_frame = None
lock = threading.Lock()  # to sync access to latest_frame

# Emotion detection thread
def detect_emotion():
    global emotion, latest_frame
    while True:
        if latest_frame is None:
            continue
        with lock:
            frame_copy = latest_frame.copy()

        try:
            result = DeepFace.analyze(frame_copy, actions=['emotion'], enforce_detection=False)
            emotion = result[0]['dominant_emotion']
            print("🧠 Emotion Detected:", emotion)
        except Exception as e:
            # Skip frame if error
            pass

# Start emotion thread
emotion_thread = threading.Thread(target=detect_emotion)
emotion_thread.daemon = True
emotion_thread.start()

# Set up hand detector and camera
detector = HandDetector(detectionCon=0.8, maxHands=1)
capture = cv2.VideoCapture(0)

space_pressed = down_pressed = up_pressed = False
last_dunk_time = 0
cooldown = 3  # seconds

while True:
    success, frame = capture.read()
    if not success:
        print("Camera not working.")
        break

    with lock:
        latest_frame = frame.copy()  # update shared frame

    hands, img = detector.findHands(frame)

    if hands:
        hand = hands[0]
        fingers = detector.fingersUp(hand)

        # Fist or Index Only = Jump
        if fingers == [0, 0, 0, 0, 0] or fingers == [0, 1, 0, 0, 0]:
            cv2.putText(img, "Jump", (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
            if not space_pressed:
                pyautogui.press('space')
                space_pressed = True
            if not up_pressed:
                pyautogui.press('up')
                up_pressed = True

        elif fingers == [1, 0, 1, 1, 1]:  # 3 fingers = Duck
            cv2.putText(img, "Duck", (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
            if not down_pressed:
                pyautogui.keyDown('down')
                down_pressed = True
        else:
            space_pressed = up_pressed = down_pressed = False
            pyautogui.keyUp('down')

    # Emotion-based actions
    if emotion and time.time() - last_dunk_time > cooldown:
        if emotion.lower() in ["happy", "happiness"]:
            print("🏀 DUNK TRIGGERED (Happy)")
            pyautogui.keyDown('down')
            time.sleep(0.5)
            pyautogui.keyUp('down')
            last_dunk_time = time.time()
            emotion = None

        elif emotion.lower() == "angry":
            print("🚀 POWER JUMP TRIGGERED (Angry)")
            pyautogui.keyDown('space')
            pyautogui.keyDown('up')
            time.sleep(0.3)
            pyautogui.keyUp('space')
            pyautogui.keyUp('up')
            last_dunk_time = time.time()
            emotion = None

    cv2.imshow("Dino Jump", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()
