
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .forms import QuestionForm, ChoiceFormSet

from .models import Choice, Question


class IndexView(generic.ListView):
    template_name = "polls/inicio.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[
            :5
        ]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detalle.html"
    
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/resultados.html"


def votar(request, question_id):
    pregunta = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = pregunta.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detalle.html",
            {
                "pregunta": pregunta,
                "error_message": "No has elegido ninguna opcion!! D-:<",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:resultados", args=(pregunta.id,)))

def agregar_pregunta(request):
    if request.method == 'POST':
        formulario = QuestionForm(request.POST)
        formularios = ChoiceFormSet(request.POST)
        if formulario.is_valid() and formularios.is_valid():
            pregunta = formulario.save()
            opciones = formularios.save(commit=False)
            for opcion in opciones:
                opcion.pregunta = pregunta
                opcion.save()
            return redirect('polls:inicio')  # Cambia esto por la vista a la que quieras redirigir
    else:
        formulario = QuestionForm()
        formularios = ChoiceFormSet()
    return render(request, 'polls/agregaOEditaPreg.html', {'formulario': formulario, 'formularios': formularios})

def agregar_o_editar_pregunta(request, pk=None):
    if pk:
        pregunta = get_object_or_404(Question, pk=pk)
    else:
        pregunta = None

    if request.method == 'POST':
        formulario = QuestionForm(request.POST, instance=pregunta)
        formularios = ChoiceFormSet(request.POST, instance=pregunta)
        if formulario.is_valid() and formularios.is_valid():
            print(formulario.cleaned_data['question_text'])
            pregunta = formulario.save()
            opciones = formularios.save(commit=False)
            # Asigna la pregunta y guarda los nuevos/actualizados
            for opcion in opciones:
                opcion.question = pregunta
                opcion.save()
            # Elimina los marcados para borrar
            for obj in formularios.deleted_objects:
                obj.delete()
            return redirect('polls:inicio')
    else:
        formulario = QuestionForm(instance=pregunta)
        formularios = ChoiceFormSet(instance=pregunta)
    return render(
        request,
        'polls/agregaOEditaPreg.html',
        {'formulario': formulario, 'formularios': formularios, 'editando': pk is not None}
    )

def mapa_leaflet(request):
    return render(request, 'polls/mapa_leaflet.html')
