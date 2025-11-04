from django.http import Http404
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from ytProfile.models import Subscription, Categoria
import math

# --- VISTA PRINCIPAL ---
def comparison_view(request, friend_username):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        friend = User.objects.get(username=friend_username)
    except User.DoesNotExist:
        raise Http404("No se encontró un usuario con el nombre especificado.")

    # --- 1. Obtener datos crudos ---
    user_subs = Subscription.objects.filter(usuario=request.user)
    friend_subs = Subscription.objects.filter(usuario=friend)

    user_category_counts = {}
    for sub in user_subs:
        for category in sub.canal.categorias.all():
            user_category_counts[category.tematica] = user_category_counts.get(category.tematica, 0) + 1

    friend_category_counts = {}
    for sub in friend_subs:
        for category in sub.canal.categorias.all():
            friend_category_counts[category.tematica] = friend_category_counts.get(category.tematica, 0) + 1

    # --- 2. Calcular la compatibilidad (lógica sin cambios) ---
    taste_similarity = calculate_cosine_similarity(user_category_counts, friend_category_counts)
    engagement_factor = calculate_engagement_factor(user_subs.count(), friend_subs.count())
    final_compatibility = int(round(taste_similarity * engagement_factor * 100))

    # --- 3. Preparar datos para los gráficos (LÓGICA SIMÉTRICA) ---
    user_pie_data, friend_pie_data, legend_data = get_symmetric_pie_data(
        user_category_counts, friend_category_counts
    )

    # --- 4. Renderizar ---
    context = {
        'friend': friend,
        'user_categories': user_pie_data,
        'friend_categories': friend_pie_data,
        'compatibility': final_compatibility,
        'legend': legend_data,
    }
    return render(request, 'comparison.html', context)

# --- FUNCIONES DE CÁLCULO ---

def get_symmetric_pie_data(user_counts, friend_counts, threshold=2.0):
    """
    Prepara los datos para los gráficos de tarta de forma simétrica.
    Una categoría se agrupa en 'Otros' solo si es pequeña para AMBOS usuarios.
    """
    total_user_cats = sum(user_counts.values()) or 1
    total_friend_cats = sum(friend_counts.values()) or 1

    user_percentages = {cat: (count / total_user_cats) * 100 for cat, count in user_counts.items()}
    friend_percentages = {cat: (count / total_friend_cats) * 100 for cat, count in friend_counts.items()}

    all_categories = set(user_counts.keys()) | set(friend_counts.keys())

    # --- Lógica de agrupación simétrica ---
    user_pie = {}
    friend_pie = {}
    user_others = 0
    friend_others = 0

    for cat in all_categories:
        user_perc = user_percentages.get(cat, 0)
        friend_perc = friend_percentages.get(cat, 0)

        # Si la categoría es pequeña para AMBOS, se agrupa
        if user_perc < threshold and friend_perc < threshold:
            user_others += user_perc
            friend_others += friend_perc
        else:
            user_pie[cat] = user_perc
            friend_pie[cat] = friend_perc

    if user_others > 0 or friend_others > 0:
        user_pie['Otros'] = user_others
        friend_pie['Otros'] = friend_others

    # --- Asignación de colores y formato final ---
    final_category_names = user_pie.keys()
    category_colors = {}
    for name in final_category_names:
        if name == 'Otros':
            category_colors[name] = '#b0b0b0'
        else:
            try:
                cat_obj = Categoria.objects.get(tematica=name)
                category_colors[name] = cat_obj.color
            except Categoria.DoesNotExist:
                category_colors[name] = '#b0b0b0'  # Color por defecto

    # Formatear para la plantilla
    user_final_data = sorted([{'name': name, 'percentage': round(perc, 1), 'color': category_colors.get(name)}
                              for name, perc in user_pie.items()], key=lambda x: x['percentage'], reverse=True)
    
    friend_final_data = sorted([{'name': name, 'percentage': round(perc, 1), 'color': category_colors.get(name)}
                                for name, perc in friend_pie.items()], key=lambda x: x['percentage'], reverse=True)

    legend_data = sorted([{'name': name, 'color': color} for name, color in category_colors.items()], key=lambda x: x['name'])

    return user_final_data, friend_final_data, legend_data

def calculate_cosine_similarity(counts1, counts2):
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
    if count1 + count2 == 0: return 0
    numerator = 2 * math.sqrt(count1 * count2)
    denominator = count1 + count2
    return numerator / denominator
