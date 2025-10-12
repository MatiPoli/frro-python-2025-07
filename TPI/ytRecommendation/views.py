from django.shortcuts import render
from .services import get_channel_recommendations

def recommend(request):
    recommendations = get_channel_recommendations(request.user)
    return render(request, 'ytRecommendation/recommendations.html', {'recommendations': recommendations})