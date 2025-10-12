from django.urls import path
from . import views

app_name = 'ytRecommendation'

urlpatterns = [
    path('recommend/', views.recommend, name='recommend'),
]