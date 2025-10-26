
import datetime

from django.db import models
from django.utils import timezone
from django.contrib import admin

# Create your models here.

class Pregunta(models.Model):
    texto_pregunta = models.CharField(max_length=200)
    fecha_publicacion = models.DateTimeField("date published", auto_now_add=True)
    def __str__(self):
        return self.texto_pregunta
    
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.fecha_publicacion <= now
    
    @admin.display(
        boolean=True,
        ordering="fecha_publicacion",
        description="Published recently?",
    )
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.fecha_publicacion <= now


class Opcion(models.Model):
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, related_name="opciones")
    texto_opcion = models.CharField(max_length=200)
    votos = models.IntegerField(default=0)

    def __str__(self):
        return self.texto_opcion
    