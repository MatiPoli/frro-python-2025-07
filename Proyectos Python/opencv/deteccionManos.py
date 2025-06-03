import cv2
import mediapipe
import time


mpPose = mediapipe.solutions.pose
pose = mpPose.Pose()
mpDraw = mediapipe.solutions.drawing_utils

cap = cv2.VideoCapture(0)
pTime = 0


width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

rectangle_width = int(width/2.5)
rectangle_height = int(height/3)

sacar_foto = False
grabar_video = False

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (width, height))

while True:
	success, img = cap.read()
	imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	results = pose.process(imgRGB)
	overlay = img.copy()
	
	print(results.pose_landmarks)
	if results.pose_landmarks:
		mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
		for id, lm in enumerate(results.pose_landmarks.landmark):
			h, w,c = img.shape
			print(id, lm)
			cx, cy = int(lm.x*w), int(lm.y*h)
			cv2.circle(img, (cx, cy), 5, (255,0,0), cv2.FILLED)

			if id == 20 and cx < rectangle_width and cy < rectangle_height:
				sacar_foto = True
			elif id == 20:
				sacar_foto = False

			if id == 19 and cx > (width - rectangle_width) and cy < rectangle_height:
				grabar_video = True
			elif id == 19:
				grabar_video = False
			
	if sacar_foto:
		cv2.imwrite("foto.jpg", img)
		cv2.rectangle(overlay, (0, 0), (rectangle_width, rectangle_height), (0, 255, 0), -1)
	else:
		cv2.rectangle(overlay, (0, 0), (rectangle_width, rectangle_height), (255, 0, 0), -1)

	if grabar_video:
		out.write(img)
		cv2.rectangle(overlay, (width - rectangle_width, 0), (width, rectangle_height), (0, 255, 0), -1)
		cv2.putText(img, "Grabando Video", (int(width - rectangle_width + 10), int(rectangle_height/2)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
	else:
		cv2.rectangle(overlay, (width - rectangle_width, 0), (width, rectangle_height), (0, 0, 255), -1)

	img = cv2.addWeighted(overlay, 0.3, img, 1 - 0.3, 0)
	cTime = time.time()
	fps = 1/(cTime-pTime)
	pTime = cTime

	cv2.putText(img, str(int(fps)), (50,50), cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0), 3)
	cv2.imshow("Image", img)
	if cv2.waitKey(10) == 27:
         break

cap.release()
out.release()
cv2.destroyAllWindows()