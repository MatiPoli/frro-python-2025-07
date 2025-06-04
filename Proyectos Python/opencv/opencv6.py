import cv2

cap = cv2.VideoCapture(0)
cont = 0
while(True):
    _, frame = cap.read()
    cv2.imshow("Mi primer OpenCV",frame)
    
    if cv2.waitKey(1) & 0xFF == ord('c'):
        cv2.imwrite("mi_frame" + str(cont) + ".png", frame)
        cont += 1
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()