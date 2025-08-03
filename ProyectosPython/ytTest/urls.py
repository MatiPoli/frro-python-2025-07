from django.urls import path
from ytTest import profile_views  # Importación corregida
from django.contrib import admin
from django.http import HttpResponse

def home_view(request):
    return HttpResponse("<h1>Bienvenido a ytTest</h1>")

urlpatterns = [
    path('profile/', profile_views.profile_view, name='profile'),
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
]