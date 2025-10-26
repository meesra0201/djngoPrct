
from django.db.models import F
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .forms import CreaPregunta, ConjuntoOpciones
from .models import Pregunta, Opcion
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json


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
        opcion_elegida = pregunta.opciones.get(pk=request.POST["opcion"])
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


def gestion_preguntas(request):
    return render(request, 'polls/gestion_preguntas.html')


@csrf_exempt
@require_http_methods(["POST", "PUT"])
def guardar_o_actualizar_pregunta(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        pregunta_id = data.get("id")
        texto_pregunta = data.get("pregunta") or data.get("texto_pregunta")
        opciones = data.get("opciones", [])

        if not texto_pregunta:
            return JsonResponse({"error": "El texto de la pregunta es obligatorio"}, status=400)

        # ✅ Crear o actualizar la pregunta
        if pregunta_id:
            pregunta = Pregunta.objects.get(pk=pregunta_id)
            pregunta.texto_pregunta = texto_pregunta
            pregunta.save()
        else:
            pregunta = Pregunta.objects.create(texto_pregunta=texto_pregunta)

        # ✅ Actualizar o crear opciones
        ids_enviados = []
        for opcion in opciones:
            opcion_id = opcion.get("id")
            texto_op = opcion.get("texto") or opcion.get("texto_opcion", "")
            texto_op = texto_op.strip()

            if not texto_op:
                continue

            if opcion_id:
                # Actualiza opción existente
                op = Opcion.objects.get(pk=opcion_id)
                op.texto_opcion = texto_op
                op.save()
                ids_enviados.append(op.id)
            else:
                # Crea nueva opción
                nueva_op = Opcion.objects.create(pregunta=pregunta, texto_opcion=texto_op)
                ids_enviados.append(nueva_op.id)

        # ✅ Eliminar opciones no incluidas
        Opcion.objects.filter(pregunta=pregunta).exclude(id__in=ids_enviados).delete()

        return JsonResponse({
            "mensaje": "Pregunta y opciones guardadas correctamente",
            "pregunta_id": pregunta.id
        })

    except Pregunta.DoesNotExist:
        return JsonResponse({"error": "La pregunta no existe"}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Formato JSON inválido"}, status=400)
    except Exception as e:
        print("Error interno:", e)
        return JsonResponse({"error": str(e)}, status=500)




def listar_preguntas(request):
    preguntas = Pregunta.objects.all().order_by("-fecha_publicacion")
    data = [
        {
            "id": p.id,
            "texto": p.texto_pregunta,
            "opciones": [{"id": o.id, "texto": o.texto_opcion} for o in p.opciones.all()]
        } for p in preguntas
    ]
    return JsonResponse(data, safe=False)

@csrf_exempt
def eliminar_pregunta(request, id):
    if request.method == "DELETE":
        try:
            Pregunta.objects.get(id=id).delete()
            return JsonResponse({"mensaje": "Pregunta eliminada"})
        except Pregunta.DoesNotExist:
            return JsonResponse({"error": "Pregunta no encontrada"}, status=404)
