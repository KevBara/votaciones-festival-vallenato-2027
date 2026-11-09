
from django.db.models import Count, Q
from django.db import IntegrityError, transaction
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone

from .forms import RegistroUsuarioForm, VotoForm
from .models import Edicion, Categoria, Votacion, Voto


# Página principal del festival
def inicio(request):
    ediciones = Edicion.objects.all()

    return render(request, "inicio.html", {
        "ediciones": ediciones
    })


# Registro de nuevos usuarios
def registro(request):
    if request.user.is_authenticated:
        return redirect("inicio")

    if request.method == "POST":
        formulario = RegistroUsuarioForm(request.POST)

        if formulario.is_valid():
            usuario = formulario.save()
            login(request, usuario)

            messages.success(
                request,
                "Tu cuenta se ha creado correctamente."
            )

            return redirect("inicio")
    else:
        formulario = RegistroUsuarioForm()

    return render(request, "registro.html", {
        "formulario": formulario
    })


# Consultar categorías de una edición
def listar_categorias(request, edicion_id):
    edicion = get_object_or_404(
        Edicion,
        id=edicion_id
    )

    ahora = timezone.now()
    votaciones_disponibles = Q(
        votaciones__activa=True,
        votaciones__fecha_inicio__lte=ahora,
        votaciones__fecha_fin__gte=ahora,
        votaciones__opciones__isnull=False,
    )
    categorias = Categoria.objects.filter(edicion=edicion).annotate(
        cantidad_votaciones=Count(
            "votaciones",
            filter=votaciones_disponibles,
            distinct=True
        ),
        cantidad_votaciones_total=Count(
            "votaciones",
            filter=Q(
                votaciones__activa=True,
                votaciones__opciones__isnull=False
            ),
            distinct=True
        ),
    )

    if request.user.is_authenticated:
        categorias = categorias.annotate(
            cantidad_votos_usuario=Count(
                "votaciones__votos",
                filter=Q(
                    votaciones__votos__usuario=request.user,
                    votaciones__activa=True,
                    votaciones__opciones__isnull=False
                ),
                distinct=True
            )
        )

    for categoria in categorias:
        if request.user.is_authenticated:
            if (
                categoria.cantidad_votaciones_total
                and categoria.cantidad_votos_usuario
                == categoria.cantidad_votaciones_total
            ):
                categoria.estado_votacion = "Votaste"
                categoria.clase_estado = "complete"
            elif categoria.cantidad_votos_usuario:
                categoria.estado_votacion = "En progreso"
                categoria.clase_estado = "progress"
            elif not categoria.habilitada or not categoria.cantidad_votaciones:
                categoria.estado_votacion = "No disponible"
                categoria.clase_estado = "unavailable"
            else:
                categoria.estado_votacion = "Pendiente"
                categoria.clase_estado = "pending"
        elif not categoria.habilitada or not categoria.cantidad_votaciones:
            categoria.estado_votacion = "No disponible"
            categoria.clase_estado = "unavailable"
        else:
            categoria.estado_votacion = "Disponible"
            categoria.clase_estado = "available"

    return render(request, "categorias.html", {
        "edicion": edicion,
        "categorias": categorias,
    })


# Consultar votaciones de una categoría
def listar_votaciones(request, categoria_id):
    categoria = get_object_or_404(
        Categoria,
        id=categoria_id
    )

    votaciones = Votacion.objects.filter(
        categoria=categoria
    )

    return render(request, "votaciones.html", {
        "categoria": categoria,
        "votaciones": votaciones
    })


# Consultar opciones participantes
def detalle_votacion(request, votacion_id):
    votacion = get_object_or_404(
        Votacion.objects.select_related("categoria__edicion"),
        id=votacion_id
    )

    opciones = votacion.opciones.all()
    mi_voto = None
    if request.user.is_authenticated:
        mi_voto = Voto.objects.filter(
            usuario=request.user,
            votacion=votacion
        ).select_related("opcion").first()
    ya_voto = mi_voto is not None
    disponible = votacion.esta_habilitada()
    confirmado = ya_voto
    siguiente_votacion = None

    if confirmado:
        pendientes = Votacion.objects.filter(
            categoria__edicion=votacion.categoria.edicion,
            categoria__habilitada=True,
            activa=True,
            fecha_inicio__lte=timezone.now(),
            fecha_fin__gte=timezone.now(),
            opciones__isnull=False,
        ).exclude(
            votos__usuario=request.user
        )
        siguiente_votacion = pendientes.filter(
            Q(categoria_id__gt=votacion.categoria_id)
            | Q(
                categoria_id=votacion.categoria_id,
                id__gt=votacion.id
            )
        ).select_related("categoria").order_by(
            "categoria_id", "id"
        ).first()

        if siguiente_votacion is None:
            siguiente_votacion = pendientes.select_related(
                "categoria"
            ).order_by("categoria_id", "id").first()

    return render(request, "detalle_votacion.html", {
        "votacion": votacion,
        "opciones": opciones,
        "ya_voto": ya_voto,
        "disponible": disponible,
        "formulario": VotoForm(votacion=votacion),
        "confirmado": confirmado,
        "siguiente_votacion": siguiente_votacion,
        "mi_voto": mi_voto,
    })


@login_required
def registrar_voto(request, votacion_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        with transaction.atomic():
            # Serializa los envíos para esta votación, incluso si llegan a la vez.
            votacion = get_object_or_404(
                Votacion.objects.select_for_update(),
                id=votacion_id
            )
            if not votacion.esta_habilitada():
                messages.error(
                    request,
                    "Esta votación no está habilitada en este momento."
                )
                return redirect("detalle_votacion", votacion_id=votacion.id)

            formulario = VotoForm(request.POST, votacion=votacion)
            if not formulario.is_valid():
                messages.error(
                    request,
                    "Selecciona una opción válida para esta votación."
                )
                return redirect("detalle_votacion", votacion_id=votacion.id)

            if Voto.objects.filter(
                usuario=request.user,
                votacion=votacion
            ).exists():
                messages.warning(
                    request,
                    "Ya registraste tu voto en esta votación."
                )
                return redirect("detalle_votacion", votacion_id=votacion.id)

            Voto.objects.create(
                usuario=request.user,
                votacion=votacion,
                opcion=formulario.cleaned_data["opcion"]
            )
    except IntegrityError:
        # La restricción única es la última defensa ante envíos concurrentes.
        if Voto.objects.filter(
            usuario=request.user,
            votacion_id=votacion_id
        ).exists():
            messages.warning(
                request,
                "Ya registraste tu voto en esta votación."
            )
            return redirect("detalle_votacion", votacion_id=votacion_id)
        raise

    detalle_url = reverse(
        "detalle_votacion",
        kwargs={"votacion_id": votacion_id}
    )
    return redirect(f"{detalle_url}?confirmado=1")

# PERSONA 3 - API DE CATEGORIAS

def api_categorias(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    categorias = Categoria.objects.select_related(
        "edicion"
    ).prefetch_related(
        "votaciones__opciones"
    ).order_by("edicion__anio", "id")

    resultado = []

    for categoria in categorias:
        lista_votaciones = []

        for votacion in categoria.votaciones.all():
            lista_opciones = []

            for opcion in votacion.opciones.all():
                lista_opciones.append({
                    "id": opcion.id,
                    "nombre": opcion.nombre,
                    "descripcion": opcion.descripcion,
                    "imagen_url": opcion.imagen_url
                })

            lista_votaciones.append({
                "id": votacion.id,
                "titulo": votacion.titulo,
                "activa": votacion.esta_habilitada(),
                "opciones": lista_opciones
            })

        resultado.append({
            "id": categoria.id,
            "nombre": categoria.nombre,
            "descripcion": categoria.descripcion,
            "habilitada": categoria.habilitada,
            "edicion": {
                "id": categoria.edicion.id,
                "nombre": categoria.edicion.nombre,
                "anio": categoria.edicion.anio
            },
            "votaciones": lista_votaciones
        })

    return JsonResponse(
        {"categorias": resultado},
        json_dumps_params={"ensure_ascii": False}
    )



# PERSONA 3 - HISTORIAL DE PARTICIPACION

@login_required
def mis_votos(request):
    votos = Voto.objects.filter(
        usuario=request.user
    ).select_related(
        "votacion__categoria__edicion",
        "opcion"
    ).order_by("-creado_en")

    return render(request, "mis_votos.html", {
        "votos": votos
    })
