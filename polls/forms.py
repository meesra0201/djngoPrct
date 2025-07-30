from django import forms
from .models import Question, Choice
from django.forms.models import inlineformset_factory

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'pub_date']

ChoiceFormSet = inlineformset_factory(
    Question, Choice, fields=['choice_text'], extra=3, can_delete=False
)