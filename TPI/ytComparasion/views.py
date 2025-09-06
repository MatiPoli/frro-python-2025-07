from django.http import Http404
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from ytProfile.models import Subscription, Categoria
import random
import colorsys
import math

def comparison_view(request, friend_username):
    if not request.user.is_authenticated:
        return redirect('login')

    current_user = request.user

    try:
        friend = User.objects.get(username=friend_username)
    except User.DoesNotExist:
        raise Http404("No se encontró un usuario con el nombre especificado.")
    
    user_subscriptions = Subscription.objects.filter(usuario=current_user)
    friend_subscriptions = Subscription.objects.filter(usuario=friend)
    
    user_total_subs = user_subscriptions.count()
    friend_total_subs = friend_subscriptions.count()

    user_category_counts = {}
    for sub in user_subscriptions:
        for category in sub.canal.categorias.all():
            user_category_counts[category.tematica] = user_category_counts.get(category.tematica, 0) + 1

    friend_category_counts = {}
    for sub in friend_subscriptions:
        for category in sub.canal.categorias.all():
            friend_category_counts[category.tematica] = friend_category_counts.get(category.tematica, 0) + 1

    # --- 2. Calcular la compatibilidad HÍBRIDA ---
    
    # 2a. Similitud de GUSTOS (0 a 1)
    taste_similarity = calculate_cosine_similarity(user_category_counts, friend_category_counts)
    
    # 2b. Similitud de COMPROMISO (0 a 1)
    # Pasamos el número total de suscripciones, no el conteo de categorías.
    engagement_factor = calculate_engagement_factor(user_total_subs, friend_total_subs)
    
    # 2c. Compatibilidad final combinada
    final_compatibility_float = taste_similarity * engagement_factor
    final_compatibility = int(round(final_compatibility_float * 100)) # Convertir a porcentaje

    # --- 3. Calcular porcentajes SÓLO para la VISUALIZACIÓN ---
    total_user_cats = sum(user_category_counts.values())
    user_category_percentages = {cat: (count / (total_user_cats or 1)) * 100 for cat, count in user_category_counts.items()}
    
    total_friend_cats = sum(friend_category_counts.values())
    friend_category_percentages = {cat: (count / (total_friend_cats or 1)) * 100 for cat, count in friend_category_counts.items()}
    
    # --- 4. Preparar datos para la plantilla (sin cambios) ---
    user_grouped_data = group_small_categories(user_category_percentages)
    friend_grouped_data = group_small_categories(friend_category_percentages)
    
    final_category_names = set(item['name'] for item in user_grouped_data) | set(item['name'] for item in friend_grouped_data)
    category_colors = generate_color_palette(final_category_names)
    if 'Otros' in category_colors: category_colors['Otros'] = '#b0b0b0'

    for item in user_grouped_data: item['color'] = category_colors.get(item['name'])
    for item in friend_grouped_data: item['color'] = category_colors.get(item['name'])
    
    legend_data = [{'name': name, 'color': category_colors[name]} for name in sorted(list(final_category_names))]

    context = {
        'friend': friend,
        'user_categories': user_grouped_data,
        'friend_categories': friend_grouped_data,
        'compatibility': final_compatibility,
        'legend': legend_data,
    }

    return render(request, 'comparison.html', context)

def generate_color_palette(category_names):
    """
    Genera una paleta de colores vistosos y visualmente distintos para una lista de nombres.
    Usa la técnica de la 'proporción áurea' para espaciar los matices.
    """
    palette = {}
    hue = random.random()  # Punto de partida aleatorio
    golden_ratio_conjugate = 0.61803398875
    
    for name in category_names:
        hue += golden_ratio_conjugate
        hue %= 1  # Mantener el matiz entre 0 y 1
        
        # Fijar saturación y brillo para colores vivos
        saturation = 0.85
        value = 0.9
        
        rgb_float = colorsys.hsv_to_rgb(hue, saturation, value)
        rgb_int = [int(c * 255) for c in rgb_float]
        palette[name] = f"#{rgb_int[0]:02x}{rgb_int[1]:02x}{rgb_int[2]:02x}"
        
    return palette

# --- FUNCIÓN AUXILIAR 2: AGRUPAR CATEGORÍAS PEQUEÑAS ---
def group_small_categories(category_percentages, threshold=2.0):
    """
    Agrupa categorías cuyo porcentaje es menor que el umbral en una sola categoría "Otros".
    """
    grouped_data = []
    others_percentage = 0.0
    
    # Ordenar de mayor a menor para un mejor display
    sorted_categories = sorted(category_percentages.items(), key=lambda item: item[1], reverse=True)

    for name, perc in sorted_categories:
        if perc >= threshold:
            grouped_data.append({'name': name, 'percentage': round(perc, 1)})
        else:
            others_percentage += perc
            
    if others_percentage > 0:
        grouped_data.append({'name': 'Otros', 'percentage': round(others_percentage, 1)})
        
    return grouped_data

def calculate_cosine_similarity(counts1, counts2):
    # ... (código sin cambios de la versión anterior)
    all_categories = set(counts1.keys()) | set(counts2.keys())
    if not all_categories: return 0
    dot_product, norm_a, norm_b = 0, 0, 0
    for category in all_categories:
        count_a = counts1.get(category, 0)
        count_b = counts2.get(category, 0)
        dot_product += count_a * count_b
        norm_a += count_a ** 2
        norm_b += count_b ** 2
    magnitude_a = math.sqrt(norm_a)
    magnitude_b = math.sqrt(norm_b)
    denominator = magnitude_a * magnitude_b
    if denominator == 0: return 0
    return (dot_product / denominator)

def calculate_engagement_factor(count1, count2):
    """
    Calcula un factor de penalización basado en la diferencia
    en el número total de suscripciones (compromiso).
    Devuelve un valor entre 0 y 1.
    """
    if count1 + count2 == 0:
        return 0
    
    # Usamos la media geométrica / media aritmética para un buen decaimiento
    numerator = 2 * math.sqrt(count1 * count2)
    denominator = count1 + count2
    
    return numerator / denominator