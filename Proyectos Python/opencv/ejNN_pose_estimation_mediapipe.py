import cv2
import mediapipe
import time


mpPose = mediapipe.solutions.pose
pose = mpPose.Pose()
mpDraw = mediapipe.solutions.drawing_utils

cap = cv2.VideoCapture(0)
pTime = 0

while True:
	success, img = cap.read()
	height, width = img.shape[:2]
	imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	results = pose.process(imgRGB)
	print(results.pose_landmarks)
	if results.pose_landmarks:
		mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
		for id, lm in enumerate(results.pose_landmarks.landmark):
			h, w,c = img.shape
			print(id, lm)
			cx, cy = int(lm.x*w), int(lm.y*h)
			cv2.circle(img, (cx, cy), 5, (255,0,0), cv2.FILLED)
			if id == 20 and cx < width/2 and cy < height/2:
				cv2.line(img, (0, height//2), (width, height//2), (255, 0, 0), 2)


	cTime = time.time()
	fps = 1/(cTime-pTime)
	pTime = cTime

	cv2.putText(img, str(int(fps)), (50,50), cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0), 3)
	cv2.imshow("Image", img)
	if cv2.waitKey(10) == 27:
         break

cap.release()
cv2.destroyAllWindows()
