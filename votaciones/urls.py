
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Página principal
    path("", views.inicio, name="inicio"),

    # Registro de usuarios
    path("registro/", views.registro, name="registro"),

    # Inicio de sesión
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="login.html"
        ),
        name="login"
    ),

    # Cierre de sesión
    path(
        "logout/",
        auth_views.LogoutView.as_view(
            next_page="inicio"
        ),
        name="logout"
    ),

    # Ediciones del festival
    path(
        "ediciones/",
        views.listar_ediciones,
        name="ediciones"
    ),

    # Categorías de una edición
    path(
        "ediciones/<int:edicion_id>/categorias/",
        views.listar_categorias,
        name="categorias"
    ),

    # Votaciones de una categoría
    path(
        "categorias/<int:categoria_id>/votaciones/",
        views.listar_votaciones,
        name="votaciones"
    ),

    # Participantes de una votación
    path(
        "votaciones/<int:votacion_id>/",
        views.detalle_votacion,
        name="detalle_votacion"
    ),
]
