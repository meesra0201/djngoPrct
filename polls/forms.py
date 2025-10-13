

from django import forms
from .models import Pregunta, Opcion
from django.forms.models import inlineformset_factory

class CreaPregunta(forms.ModelForm):
    texto_pregunta = forms.CharField(
        label="Agrega una nueva encuesta",
        widget=forms.TextInput(attrs={'placeholder': 'Escribe la pregunta aquí'})
    )
    
    class Meta:
        model = Pregunta
        fields = ['texto_pregunta']

ConjuntoOpciones = inlineformset_factory(
    Pregunta,
    Opcion,
    fields=['texto_opcion'],
    extra=3,
    can_delete=True,
    widgets={
        'texto_opcion': forms.TextInput(attrs={'placeholder': 'Opción de respuesta'})
    },
    labels={'texto_opcion': 'Opción'}
)