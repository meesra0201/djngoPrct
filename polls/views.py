
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .forms import CreaPregunta, ConjuntoOpciones

from .models import Pregunta, Opcion


class IndexView(generic.ListView):
    template_name = "polls/inicio.html"
    context_object_name = "lista_ultimas_preguntas"

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Pregunta.objects.filter(fecha_publicacion__lte=timezone.now()).order_by("-fecha_publicacion")[
            :5
        ]


class DetailView(generic.DetailView):
    model = Pregunta
    template_name = "polls/detalle.html"
    
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Pregunta.objects.filter(fecha_publicacion__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Pregunta
    template_name = "polls/resultados.html"


def votar(request, question_id):
    pregunta = get_object_or_404(Pregunta, pk=question_id)
    try:
        opcion_elegida = pregunta.opcion_set.get(pk=request.POST["opcion"])
    except (KeyError, Opcion.DoesNotExist):
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
        opcion_elegida.votos = F("votos") + 1
        opcion_elegida.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:resultados", args=(pregunta.id,)))


def agregar_o_editar_pregunta(request, pk=None):
    if pk:
        pregunta = get_object_or_404(Pregunta, pk=pk)
    else:
        pregunta = None

    if request.method == 'POST':
        formulario = CreaPregunta(request.POST, instance=pregunta)
        formularios = ConjuntoOpciones(request.POST, instance=pregunta)
        if formulario.is_valid() and formularios.is_valid():
            #print(formulario.cleaned_data['texto_pregunta'])
            opciones_validas = [f for f in formularios if f.cleaned_data.get('texto_opcion') and not f.cleaned_data.get('DELETE')]
            if len(opciones_validas) < 2:
                mensaje_error = "Debes ingresar al menos dos opciones de respuesta."
                return render(
                    request,
                    'polls/agregaOEditaPreg.html',
                    {
                        'formulario': formulario,
                        'formularios': formularios,
                        'editando': pk is not None,
                        'mensaje_error': mensaje_error
                    }
            )
            pregunta = formulario.save()
            opciones = formularios.save(commit=False)
            # Asigna la pregunta y guarda los nuevos/actualizados
            for opcion in opciones:
                opcion.pregunta = pregunta
                opcion.save()
            # Elimina los marcados para borrar
            for obj in formularios.deleted_objects:
                obj.delete()
            return redirect('polls:inicio')
        else:
            mensaje_error = "Revisa los campos: hay errores en el formulario."
            # se imprimen los errores para depuración
            print(formulario.errors)
            print(formularios.errors)
            return render(
                request,
                'polls/agregaOEditaPreg.html',
                {
                    'formulario': formulario,
                    'formularios': formularios,
                    'editando': pk is not None,
                    'mensaje_error': mensaje_error
                }
            )
    else:
        formulario = CreaPregunta(instance=pregunta)
        formularios = ConjuntoOpciones(instance=pregunta)
    return render(
        request,
        'polls/agregaOEditaPreg.html',
        {'formulario': formulario, 'formularios': formularios, 'editando': pk is not None}
    )

def mapa_leaflet(request):
    return render(request, 'polls/mapa_leaflet.html')
