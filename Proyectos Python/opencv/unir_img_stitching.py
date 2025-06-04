import cv2
import os

# Directorio donde están las imágenes (nombres tipo 000.jpg, 001.jpg, etc.)
directorio = "img"
formato = "{:03d}.jpeg"
cantidad = 6

imagenes = []
for i in range(cantidad):
    path = os.path.join(directorio, formato.format(i))
    img = cv2.imread(path)
    if img is None:
        print(f"No se pudo cargar: {path}")
        continue
    imagenes.append(img)

if len(imagenes) < 2:
    print("Se necesitan al menos dos imágenes para hacer stitching.")
    exit()

# Usa el módulo de Stitcher (disponible en OpenCV 4+)
stitcher = cv2.Stitcher_create()
estado, pano = stitcher.stitch(imagenes)

if estado == cv2.Stitcher_OK:
    print("Stitching completado con éxito")
    cv2.imshow("Panorama", pano)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print(f"Error en stitching. Código de estado: {estado}")
