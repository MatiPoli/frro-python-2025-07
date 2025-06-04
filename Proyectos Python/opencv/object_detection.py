import cv2
import numpy as np # Necesario para cálculos de distancia y centroides

# Labels of Network.
classNames = { 0: 'background',
    1: 'aeroplane', 2: 'bicycle', 3: 'bird', 4: 'boat',
    5: 'bottle', 6: 'bus', 7: 'car', 8: 'cat', 9: 'chair',
    10: 'cow', 11: 'diningtable', 12: 'dog', 13: 'horse',
    14: 'motorbike', 15: 'person', 16: 'pottedplant',
    17: 'sheep', 18: 'sofa', 19: 'train', 20: 'tvmonitor' }

# Open video file or capture device.
cap = cv2.VideoCapture("highway3.mp4") # Usa tu video
# cap = cv2.VideoCapture(0) # O la cámara web

if not cap.isOpened():
    print("Error: No se pudo abrir el video o la cámara.")
    exit()

#Load the Caffe model
net = cv2.dnn.readNetFromCaffe('MobileNetSSD_deploy.prototxt.txt', 'MobileNetSSD_deploy.caffemodel')

# --- Variables para el conteo y seguimiento ---
contador_coches = 0
tracked_cars = []  # Lista para almacenar los coches rastreados
next_car_id = 0    # Siguiente ID único para un coche
# Línea de conteo (posición Y). Ajusta esto según tu video.
# Por ejemplo, a la mitad de la altura del frame.
# Se definirá después de leer el primer frame para tener las dimensiones.
LINE_Y = None
# Distancia máxima (en píxeles) para considerar que un nuevo centroide es el mismo coche
MAX_DISTANCE = 50
# Número máximo de frames que un coche puede estar sin ser detectado antes de eliminarlo del rastreo
MAX_FRAMES_TO_SKIP = 10
# --- Fin Variables para el conteo y seguimiento ---

def calculate_centroid(x1, y1, x2, y2):
    """Calcula el centroide de un bounding box."""
    return int((x1 + x2) / 2), int((y1 + y2) / 2)

def calculate_distance(p1, p2):
    """Calcula la distancia euclidiana entre dos puntos."""
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

frame_count = 0 # Para inicializar LINE_Y

while True:
    ret, frame = cap.read()
    if not ret:
        print("Fin del video o error al leer frame.")
        break

    frame_height, frame_width = frame.shape[:2]

    # Definir LINE_Y basado en la altura del primer frame
    if LINE_Y is None:
        LINE_Y = int(frame_height * 0.6) # Línea al 60% de la altura (ajustar)

    frame_resized = cv2.resize(frame,(300,300))

    blob = cv2.dnn.blobFromImage(frame_resized, 0.007843, (300, 300), (127.5, 127.5, 127.5), False)
    net.setInput(blob)
    detections = net.forward()

    cols = frame_resized.shape[1]
    rows = frame_resized.shape[0]

    current_detected_centroids = [] # Centroides detectados en este frame

    # --- Paso 1: Detectar coches y obtener sus centroides ---
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5: # Umbral de confianza más alto puede ayudar
            class_id = int(detections[0, 0, i, 1])

            if classNames.get(class_id) == 'car':
                xLeftBottom = int(detections[0, 0, i, 3] * cols)
                yLeftBottom = int(detections[0, 0, i, 4] * rows)
                xRightTop   = int(detections[0, 0, i, 5] * cols)
                yRightTop   = int(detections[0, 0, i, 6] * rows)

                heightFactor = frame_height / 300.0
                widthFactor = frame_width / 300.0

                xLeftBottom_orig = int(widthFactor * xLeftBottom)
                yLeftBottom_orig = int(heightFactor * yLeftBottom)
                xRightTop_orig   = int(widthFactor * xRightTop)
                yRightTop_orig   = int(heightFactor * yRightTop)

                centroid = calculate_centroid(xLeftBottom_orig, yLeftBottom_orig, xRightTop_orig, yRightTop_orig)
                current_detected_centroids.append({
                    'centroid': centroid,
                    'box': (xLeftBottom_orig, yLeftBottom_orig, xRightTop_orig, yRightTop_orig)
                })

                # Dibujar bounding box para todos los coches detectados
                cv2.rectangle(frame, (xLeftBottom_orig, yLeftBottom_orig), (xRightTop_orig, yRightTop_orig), (0, 255, 0), 2)
                # No pongas el contador en la etiqueta del coche individual aquí
                # label = "Car"
                # labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                # cv2.rectangle(frame, (xLeftBottom_orig, yLeftBottom_orig - labelSize[1]),
                #                      (xLeftBottom_orig + labelSize[0], yLeftBottom_orig + baseLine),
                #                      (255, 255, 255), cv2.FILLED)
                # cv2.putText(frame, label, (xLeftBottom_orig, yLeftBottom_orig),
                #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))


    # --- Paso 2: Actualizar rastreadores existentes y contar ---
    updated_tracked_cars = []
    for car_info in tracked_cars:
        car_id = car_info['id']
        prev_centroid = car_info['centroid']
        frames_skipped = car_info['frames_skipped']
        counted = car_info['counted']

        best_match_dist = MAX_DISTANCE + 1 # Un valor mayor que MAX_DISTANCE
        best_match_detection = None
        best_match_idx = -1

        # Intentar encontrar el coche rastreado en las detecciones actuales
        for idx, detected_obj in enumerate(current_detected_centroids):
            dist = calculate_distance(prev_centroid, detected_obj['centroid'])
            if dist < best_match_dist:
                best_match_dist = dist
                best_match_detection = detected_obj
                best_match_idx = idx

        if best_match_detection and best_match_dist < MAX_DISTANCE:
            # Coche encontrado, actualizar
            new_centroid = best_match_detection['centroid']
            
            # Comprobar si cruzó la línea (asumiendo que los coches van de arriba hacia abajo)
            # Si tus coches van de abajo hacia arriba, invierte la condición: prev_centroid[1] > LINE_Y and new_centroid[1] <= LINE_Y
            if not counted and prev_centroid[1] > LINE_Y and new_centroid[1] <= LINE_Y:
                contador_coches += 1
                counted = True
                # Opcional: Cambiar color del coche contado
                # cv2.rectangle(frame, best_match_detection['box'][0:2], best_match_detection['box'][2:4], (0, 0, 255), 2)


            updated_tracked_cars.append({
                'id': car_id,
                'centroid': new_centroid,
                'box': best_match_detection['box'],
                'frames_skipped': 0,
                'counted': counted
            })
            # Marcar esta detección como usada para que no se asigne a otro rastreador
            if best_match_idx != -1:
                 current_detected_centroids.pop(best_match_idx)
        else:
            # Coche no encontrado en este frame
            frames_skipped += 1
            if frames_skipped <= MAX_FRAMES_TO_SKIP:
                # Mantener el rastreo por unos frames más
                car_info['frames_skipped'] = frames_skipped
                updated_tracked_cars.append(car_info)
            # Si frames_skipped > MAX_FRAMES_TO_SKIP, el coche se elimina (no se añade a updated_tracked_cars)

    tracked_cars = updated_tracked_cars

    # --- Paso 3: Registrar nuevos coches ---
    for detected_obj in current_detected_centroids: # Lo que queda son nuevas detecciones
        tracked_cars.append({
            'id': next_car_id,
            'centroid': detected_obj['centroid'],
            'box': detected_obj['box'],
            'frames_skipped': 0,
            'counted': False # Un coche nuevo no ha sido contado aún
        })
        next_car_id += 1

    # --- Dibujar información en el frame ---
    # Dibujar la línea de conteo
    cv2.line(frame, (0, LINE_Y), (frame_width, LINE_Y), (255, 0, 0), 2)

    # Dibujar IDs de los coches rastreados (opcional, para depuración)
    for car in tracked_cars:
        c_id = car['id']
        centroid = car['centroid']
        # cv2.putText(frame, f"ID: {c_id}", (centroid[0] - 10, centroid[1] - 10),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        # Dibuja un círculo en el centroide rastreado
        cv2.circle(frame, centroid, 4, (0, 0, 255) if car['counted'] else (255, 255, 0) , -1)


    # Mostrar el contador de coches
    cv2.putText(frame, f"Coches Contados: {contador_coches}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Contador de Coches", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'): # Salir con 'q'
        break
    # if cv2.waitKey(1) >= 0:  # Break with any key (tu original)
    #     break

cap.release()
cv2.destroyAllWindows()