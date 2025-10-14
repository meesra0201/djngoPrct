from django.urls import path

from . import views

app_name = "polls"
urlpatterns = [
    path("", views.IndexView.as_view(), name="inicio"),
    path("<int:pk>/", views.DetailView.as_view(), name="detalle"),
    path("<int:pk>/resultados/", views.ResultsView.as_view(), name="resultados"),
    path("<int:question_id>/votar/", views.votar, name="votar"),
#   path('agregar/', views.agregar_pregunta, name='agregar_pregunta'),
    path('agregar/', views.agregar_o_editar_pregunta, name='agregar_pregunta'),
    path('editar/<int:pk>/', views.agregar_o_editar_pregunta, name='editar_pregunta'),
    path('mapa/', views.mapa_leaflet, name='mapa_leaflet'),


]