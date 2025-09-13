from ytProfile.models import Categoria
from django.db import transaction
import colorsys

@transaction.atomic
def asignar_colores():
    categorias = list(Categoria.objects.all())
    n = len(categorias)
    # Generar N colores bien separados en el espectro HSV
    for i, cat in enumerate(categorias):
        # Alternar saturación y valor para más contraste
        hue = (i * 1.618) % 1  # Golden ratio for better spread
        saturation = 0.85 if i % 2 == 0 else 0.65
        value = 0.95 if i % 3 == 0 else 0.75
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        color_hex = '#{:02x}{:02x}{:02x}'.format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
        cat.color = color_hex
        cat.save()
    print(f"Colores HSV asignados correctamente a {n} categorías.")

if __name__ == "__main__":
    asignar_colores()
