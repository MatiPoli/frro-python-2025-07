from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
	idCategoria = models.CharField(max_length=50, unique=True)
	tematica = models.CharField(max_length=100)

	def __str__(self):
		return self.tematica

class Canal(models.Model):
	idCanal = models.CharField(max_length=100, unique=True)
	nombreCanal = models.CharField(max_length=255)
	categorias = models.ManyToManyField(Categoria, related_name='canales')
	thumbnail_url = models.URLField(max_length=500, blank=True, null=True)

	def __str__(self):
		return self.nombreCanal

class Subscription(models.Model):
	usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='suscripciones')
	canal = models.ForeignKey(Canal, on_delete=models.CASCADE, related_name='suscriptores')
	fecha_suscripcion = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.usuario.username} suscripto a {self.canal.nombreCanal}"

class Follow(models.Model):
	seguidor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='siguiendo')
	seguido = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seguidores')
	fecha = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.seguidor.username} sigue a {self.seguido.username}"

# User --> username... (mail ?)