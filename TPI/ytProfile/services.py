from collections import Counter
import json
import re

from .models import Subscription, Categoria

def get_profile_data(user):
    """
    Prepara los datos del perfil, incluyendo suscripciones y distribución de categorías.
    """
    # 1. Obtener suscripciones de la base de datos
    subs_db = Subscription.objects.filter(usuario=user).select_related('canal').prefetch_related('canal__categorias')
    
    # 2. Preparar datos para la lista de suscripciones y contar temas
    subscriptions_render = []
    all_topics = []
    for sub in subs_db:
        categorias = list(sub.canal.categorias.all())
        if categorias:
            topics = [re.sub(r"\s*\(.*?\)", "", cat.tematica).strip() for cat in categorias]
            all_topics.extend(topics)
            topic_str = ', '.join(topics)
        else:
            topic_str = 'Sin categoría'
            all_topics.append(topic_str)
        subscriptions_render.append({
            'title': sub.canal.nombreCanal,
            'topic': topic_str,
            'thumbnail_url': sub.canal.thumbnail_url
        })

    # 3. Calcular la distribución de temas y preparar datos para el gráfico
    topic_distribution = Counter(all_topics)
    total = sum(topic_distribution.values())
    chart_data_list = []
    otras_count = 0
    for k, v in topic_distribution.items():
        main_cat = re.sub(r"\s*\(.*?\)", "", k).strip()
        percent = (v / total) * 100 if total > 0 else 0
        if percent < 2:
            otras_count += v
        else:
            try:
                cat_obj = Categoria.objects.get(tematica=main_cat)
                color = cat_obj.color
            except Categoria.DoesNotExist:
                color = "#b0b0b0"
            chart_data_list.append({'category': main_cat, 'count': v, 'color': color})
    
    if otras_count > 0:
        chart_data_list.append({'category': 'Otras', 'count': otras_count, 'color': '#b0b0b0'})
    
    chart_data_json = json.dumps(chart_data_list)

    return {
        'subscriptions_render': subscriptions_render,
        'subscriptions_count': subs_db.count(),
        'chart_data': chart_data_json,
        'topic_distribution': topic_distribution # Devolver esto para el servicio de recomendación
    }
