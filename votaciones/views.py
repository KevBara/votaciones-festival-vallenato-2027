
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import RegistroUsuarioForm
from .models import Edicion, Categoria, Votacion


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


# Consultar todas las ediciones
def listar_ediciones(request):
    ediciones = Edicion.objects.all()

    return render(request, "ediciones.html", {
        "ediciones": ediciones
    })


# Consultar categorías de una edición
def listar_categorias(request, edicion_id):
    edicion = get_object_or_404(
        Edicion,
        id=edicion_id
    )

    categorias = Categoria.objects.filter(
        edicion=edicion
    )

    return render(request, "categorias.html", {
        "edicion": edicion,
        "categorias": categorias
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
        Votacion,
        id=votacion_id
    )

    opciones = votacion.opciones.all()

    return render(request, "detalle_votacion.html", {
        "votacion": votacion,
        "opciones": opciones
    })
