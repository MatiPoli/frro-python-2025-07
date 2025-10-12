import re
import random
from django.db.models import Count, Case, When, F, Sum, Value, FloatField
from ytProfile.models import Follow, Subscription, Canal, Categoria

def get_channel_recommendations(user, topic_distribution):
    """
    Genera recomendaciones de canales, ponderando categorías y añadiendo aleatoriedad.
    """
    if not user.is_authenticated:
        return []

    followed_users = [f.seguido for f in Follow.objects.filter(seguidor=user)]
    if not followed_users:
        return []

    user_subscribed_channel_ids = Subscription.objects.filter(usuario=user).values_list('canal__id', flat=True)

    total_topics = sum(topic_distribution.values())
    category_weights = {}
    if total_topics > 0:
        category_weights = {topic: count / total_topics for topic, count in topic_distribution.items()}

    whens = []
    if category_weights:
        all_db_categories = Categoria.objects.all()
        for cat_obj in all_db_categories:
            cleaned_name = re.sub(r"\s*\(.*?\)", "", cat_obj.tematica).strip()
            if cleaned_name in category_weights:
                weight = category_weights[cleaned_name]
                whens.append(When(categorias__id=cat_obj.id, then=Value(weight)))

    category_score_annotation = Sum(
        Case(*whens, default=Value(0.0), output_field=FloatField()),
        distinct=True
    )

    CATEGORY_WEIGHT_MULTIPLIER = 10 

    # 1. Obtener un grupo más grande de recomendaciones (Top 30)
    top_recommendations = Canal.objects.filter(
        suscriptores__usuario__in=followed_users
    ).exclude(
        id__in=user_subscribed_channel_ids
    ).annotate(
        friend_score=Count('suscriptores__usuario', distinct=True)
    ).annotate(
        category_score=category_score_annotation
    ).annotate(
        score=F('friend_score') + (F('category_score') * CATEGORY_WEIGHT_MULTIPLIER)
    ).order_by('-score').distinct()[:30]

    # 2. Mezclar la lista de candidatos
    recommendation_list = list(top_recommendations)
    random.shuffle(recommendation_list)

    # 3. Devolver los primeros 10 de la lista mezclada
    return recommendation_list[:10]
