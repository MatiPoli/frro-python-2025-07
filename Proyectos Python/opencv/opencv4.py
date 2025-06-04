import cv2
import numpy as nm

cap = cv2.VideoCapture(0)

velocidad_texto = 20
pos_texto = 0
texto = "Markos gordoy"

while(True):
    _, rgb = cap.read()
    escala_grises = cv2.cvtColor(rgb,cv2.COLOR_BGR2GRAY)
    _,binaria = cv2.threshold(escala_grises, 90, 255, cv2.THRESH_BINARY_INV)
    
    x_offset = rgb.shape[1] - 150
    y_offset = 20
    
    pos_texto += velocidad_texto
    if pos_texto > rgb.shape[1]:
        pos_texto = -200
    
    cv2.putText(rgb, texto, (rgb.shape[1] - pos_texto, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
    
    cv2.circle(rgb, (x_offset + 20, y_offset + 20), 15 , (0, 255, 255))
    
    cv2.imshow("RGB",rgb)
    cv2.imshow("Escala de grises", escala_grises)
    cv2.imshow("Binaria",binaria)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
