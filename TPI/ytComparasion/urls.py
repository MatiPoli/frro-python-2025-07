# profile_urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('comparison/<str:friend_username>/', views.comparison_view, name='comparison_view'),
]