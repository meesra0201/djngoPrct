

from django import forms
from .models import Question, Choice
from django.forms.models import inlineformset_factory

class QuestionForm(forms.ModelForm):
    question_text = forms.CharField(
        label="Agrega una nueva encuesta",
        widget=forms.TextInput(attrs={'placeholder': 'Escribe la pregunta aquí'})
    )
    pub_date = forms.DateTimeField(
        label="Fecha de publicación",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    class Meta:
        model = Question
        fields = ['question_text', 'pub_date']

ChoiceFormSet = inlineformset_factory(
    Question,
    Choice,
    fields=['choice_text'],
    extra=3,
    can_delete=False,
    widgets={
        'choice_text': forms.TextInput(attrs={'placeholder': 'Opción de respuesta'})
    },
    labels={'choice_text': 'Opción'}
)