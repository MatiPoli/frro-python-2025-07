# profile_urls.py
from django.urls import path
from . import views

urlpatterns = [
    # URL para la página de perfil del usuario
    path('profile/', views.profile_view, name='profile_view'),
    path('error/',views.error_view, name='error_page')
]