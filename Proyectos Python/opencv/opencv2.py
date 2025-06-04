import cv2

cap = cv2.VideoCapture("video.mp4")
#cap = cv2.VideoCapture("rtsp://192.168.1.2:8080/out.h264")

while(True):
    ret, frame = cap.read()
    
    if ret == False:
        print("El frame está vacío")
        break
    
    cv2.imshow("Mi primer OpenCV",frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()