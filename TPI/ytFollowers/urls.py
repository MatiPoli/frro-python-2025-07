from django.urls import path
from . import views

urlpatterns = [
    path('followers/', views.home, name='ytfollowers_home'),
]
