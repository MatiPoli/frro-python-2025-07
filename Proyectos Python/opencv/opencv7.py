import cv2

cap = cv2.VideoCapture(0)

salida = cv2.VideoWriter("videoSalida.avi", cv2.VideoWriter_fourcc(*'XVID'),20.0,(640,480))

while (cap.isOpened()):
    ret, imagen = cap.read()
    if ret == True:
        cv2.imshow('video', imagen)
        salida.write(imagen)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            break
    else: break
    
cap.release()
salida.release()
cv2.destroyAllWindows()