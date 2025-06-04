import cv2
import numpy as np

# Configuración del detector ArUco
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
detector = cv2.aruco.ArucoDetector(dictionary)

# Inicializar la cámara
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)  # Ancho
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # Alto

# Cargar la imagen para superponer
imagen_overlay = cv2.imread("mi_frame.png")
if imagen_overlay is None:
    print("Error: No se pudo cargar la imagen 'utn.png'")
    exit()

while True:
    imagen_overlay = cv2.imread("mi_frame.png")
    ret, frame = cap.read()
    if not ret:
        print("No se pudo capturar el frame")
        break
    
    # Detectar marcadores
    corners, ids, rejected = detector.detectMarkers(frame)
    
    if ids is not None:
        # Dibujar marcadores detectados
        frame_markers = cv2.aruco.drawDetectedMarkers(frame.copy(), corners, ids)
        
        # Procesar solo el primer marcador detectado
        marker_corners = corners[0][0]
        
        # Extraer las esquinas del marcador
        c1 = (marker_corners[0][0], marker_corners[0][1])
        c2 = (marker_corners[1][0], marker_corners[1][1])
        c3 = (marker_corners[2][0], marker_corners[2][1])
        c4 = (marker_corners[3][0], marker_corners[3][1])
        
        # Preparar puntos para la homografía
        puntos_aruco = np.array([c1, c2, c3, c4], dtype=np.float32)
        
        # Puntos de la imagen a superponer
        h, w = imagen_overlay.shape[:2]
        puntos_imagen = np.array([
            [0, 0],
            [w - 1, 0],
            [w - 1, h - 1],
            [0, h - 1]
        ], dtype=np.float32)
        
        # Calcular homografía
        H, _ = cv2.findHomography(puntos_imagen, puntos_aruco)
        
        # Aplicar transformación de perspectiva
        warped_image = cv2.warpPerspective(imagen_overlay, H, (frame.shape[1], frame.shape[0]))
        
        # Crear máscara y superponer la imagen
        mask = np.zeros(frame.shape, dtype=np.uint8)
        cv2.fillConvexPoly(mask, np.int32(puntos_aruco), (255, 255, 255))
        
        # Combinar las imágenes
        frame_markers = cv2.bitwise_and(frame_markers, cv2.bitwise_not(mask))
        resultado = cv2.bitwise_or(frame_markers, warped_image)
        
        #Recursividad
        for _ in range(30):
            corners, ids, rejected = detector.detectMarkers(resultado)
            if ids is not None:
                frame_markers = cv2.aruco.drawDetectedMarkers(resultado.copy(), corners, ids)
                
                # Procesar solo el primer marcador detectado
                marker_corners = corners[0][0]
                
                # Extraer las esquinas del marcador
                c1 = (marker_corners[0][0], marker_corners[0][1])
                c2 = (marker_corners[1][0], marker_corners[1][1])
                c3 = (marker_corners[2][0], marker_corners[2][1])
                c4 = (marker_corners[3][0], marker_corners[3][1])
                
                # Preparar puntos para la homografía
                puntos_aruco = np.array([c1, c2, c3, c4], dtype=np.float32)
                
                H, _ = cv2.findHomography(puntos_imagen, puntos_aruco)
                
                # Aplicar transformación de perspectiva
                warped_image = cv2.warpPerspective(imagen_overlay, H, (resultado.shape[1], resultado.shape[0]))
                
                # Crear máscara y superponer la imagen
                mask = np.zeros(resultado.shape, dtype=np.uint8)
                cv2.fillConvexPoly(mask, np.int32(puntos_aruco), (255, 255, 255))
                
                # Combinar las imágenes
                frame_markers = cv2.bitwise_and(frame_markers, cv2.bitwise_not(mask))
                resultado = cv2.bitwise_or(frame_markers, warped_image)
            
        cv2.imshow("Realidad Aumentada", resultado)
    else:
        cv2.imshow("Realidad Aumentada", frame)
    
    cv2.imwrite("mi_frame.png", frame)
    
    # Salir con ESC
    if cv2.waitKey(10) == 27:
        break

cap.release()
cv2.destroyAllWindows()
