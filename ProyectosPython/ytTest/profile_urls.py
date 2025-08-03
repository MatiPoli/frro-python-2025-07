# profile_urls.py
from django.urls import path
from . import profile_views

urlpatterns = [
    # URL para la página de perfil del usuario
    path('profile/', profile_views.profile_view, name='profile'),
]