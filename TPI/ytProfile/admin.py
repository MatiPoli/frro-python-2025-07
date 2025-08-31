from django.contrib import admin
from .models import Categoria, Canal, Subscription, Follow

# Register your models here.
admin.site.register(Categoria)
admin.site.register(Canal)
admin.site.register(Subscription)
admin.site.register(Follow)
