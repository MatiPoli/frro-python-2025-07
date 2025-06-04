import cv2
import numpy as np

cap = cv2.VideoCapture(0)

while(True):
    _, rgb = cap.read()
    escala_grises = cv2.cvtColor(rgb,cv2.COLOR_BGR2GRAY)
    _,binaria = cv2.threshold(escala_grises, 90, 255, cv2.THRESH_BINARY_INV)
    
    cv2.imshow("RGB",rgb)
    cv2.imshow("Escala de grises", escala_grises)
    cv2.imshow("Binaria",binaria)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()