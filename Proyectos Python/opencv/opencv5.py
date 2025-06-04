import cv2

cap = cv2.VideoCapture(0)

while(True):
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.rectangle(frame, (100,100), (200, 200))