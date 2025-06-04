import cv2
import numpy as np

def load_obj(filename):
    vertices = []
    faces = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('v '):
                parts = line.strip().split()
                vertex = list(map(float, parts[1:4]))
                vertices.append(vertex)
            elif line.startswith('f '):
                parts = line.strip().split()
                face = [int(p.split('/')[0]) - 1 for p in parts[1:]]
                faces.append(face)
    return np.array(vertices), faces

def draw_axis(img, camera_matrix, dist_coeffs, rvec, tvec, length=0.05):
    import numpy as np
    import cv2
    axis = np.float32([[length,0,0],[0,length,0],[0,0,length]]).reshape(-1,3)
    imgpts, _ = cv2.projectPoints(axis, rvec, tvec, camera_matrix, dist_coeffs)
    corner = tuple(int(x) for x in cv2.projectPoints(np.zeros((1,3),dtype=np.float32), rvec, tvec, camera_matrix, dist_coeffs)[0].reshape(2))
    imgpts = imgpts.reshape(-1,2)
    img = cv2.line(img, corner, tuple(imgpts[0].astype(int)), (0,0,255), 3)  # X rojo
    img = cv2.line(img, corner, tuple(imgpts[1].astype(int)), (0,255,0), 3)  # Y verde
    img = cv2.line(img, corner, tuple(imgpts[2].astype(int)), (255,0,0), 3)  # Z azul
    return img

# Cargar modelo
obj_vertices, obj_faces = load_obj('alien.obj')

# Parámetros de cámara de ejemplo
camera_matrix = np.array([[800, 0, 320],
                          [0, 800, 240],
                          [0,   0,   1]], dtype=np.float32)
dist_coeffs = np.zeros((5, 1))  # sin distorsión

# Diccionario ArUco y detector
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
detector = cv2.aruco.ArucoDetector(aruco_dict)

parameters = cv2.aruco.DetectorParameters()

# Cámara
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    corners, ids, rejected = detector.detectMarkers(frame)

    #corners, ids, _ = detector.detectMarkers(gray, aruco_dict, parameters=parameters)
    scale = 0.0001
    if ids is not None:
        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, 0.05, camera_matrix, dist_coeffs)

        for rvec, tvec in zip(rvecs, tvecs):
            # Dibujar el eje del marcador
            #cv2.aruco.drawAxis(frame, camera_matrix, dist_coeffs, rvec, tvec, 0.03)
            draw_axis(frame, camera_matrix, dist_coeffs, rvec, tvec, 0.03)

            # Proyectar los vértices del modelo
            angle_rad = np.deg2rad(0)
            Rx = np.array([
                [1, 0, 0],
                [0, np.cos(angle_rad), -np.sin(angle_rad)],
                [0, np.sin(angle_rad),  np.cos(angle_rad)]
            ])

            rotated_vertices = (obj_vertices * scale).dot(Rx.T)
            projected_points, _ = cv2.projectPoints(rotated_vertices, rvec, tvec, camera_matrix, dist_coeffs)
            projected_points = projected_points.reshape(-1, 2).astype(int)

            # Dibujar el modelo como líneas entre vértices
            for face in obj_faces:
                for i in range(len(face)):
                    pt1 = tuple(projected_points[face[i]])
                    pt2 = tuple(projected_points[face[(i + 1) % len(face)]])
                    cv2.line(frame, pt1, pt2, (0, 255, 0), 2)

    cv2.imshow("MARKOS", frame)
    if cv2.waitKey(1) == 27:  # ESC para salir
        break

cap.release()
cv2.destroyAllWindows()

