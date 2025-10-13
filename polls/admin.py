from django.contrib import admin
from .models import Opcion, Pregunta

# Register your models here.

class OpcionEnLinea(admin.TabularInline):
    model = Opcion
    extra = 3

class AdminPregunta(admin.ModelAdmin):
        fieldsets = [
        ("Pregunta", {"fields": ["texto_pregunta"]}),
        ("Datos de publicación", {"fields": ["fecha_publicacion"], "classes":["collapse"]}),
        ]
        inlines = [OpcionEnLinea]  
        list_display = ["texto_pregunta", "fecha_publicacion", "was_published_recently"]
        list_filter = ["fecha_publicacion"]
        search_fields = ["texto_pregunta"]


admin.site.register(Pregunta, AdminPregunta)
