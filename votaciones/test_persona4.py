from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Edicion, Categoria, Votacion, Opcion, Voto


class Persona4PruebasFuncionales(TestCase):
    """
    Casos CP-01 a CP-10 para la responsabilidad de pruebas funcionales.
    Se ejecutan con: python manage.py test votaciones.test_persona4
    """

    def setUp(self):
        self.usuario = User.objects.create_user(
            username="votante_cp",
            password="ClaveSegura-2027!",
            first_name="Usuario",
            last_name="Prueba",
            email="votante_cp@example.test",
        )
        self.otro_usuario = User.objects.create_user(
            username="otro_cp",
            password="ClaveSegura-2027!",
            email="otro_cp@example.test",
        )
        self.edicion = Edicion.objects.create(
            nombre="Festival de la Leyenda Vallenata",
            anio=2027,
            fecha_inicio=date(2027, 4, 1),
            fecha_fin=date(2027, 4, 30),
        )
        self.categoria = Categoria.objects.create(
            edicion=self.edicion,
            nombre="Acordeoneros",
            habilitada=True,
        )
        ahora = timezone.now()
        self.votacion = Votacion.objects.create(
            categoria=self.categoria,
            titulo="Mejor acordeonero 2027",
            fecha_inicio=ahora - timedelta(days=1),
            fecha_fin=ahora + timedelta(days=1),
            activa=True,
        )
        self.opcion = Opcion.objects.create(
            votacion=self.votacion,
            nombre="Acordeonero A",
        )
        self.opcion_b = Opcion.objects.create(
            votacion=self.votacion,
            nombre="Acordeonero B",
        )
        self.url_votar = reverse(
            "registrar_voto",
            kwargs={"votacion_id": self.votacion.pk},
        )

    def test_cp01_registro_de_usuario(self):
        """Un visitante puede crear una cuenta con datos válidos."""
        datos = {
            "username": "nuevo_cp01",
            "first_name": "Nuevo",
            "last_name": "Participante",
            "email": "nuevo_cp01@example.test",
            "password1": "Festival2027!ClaveSegura",
            "password2": "Festival2027!ClaveSegura",
        }
        respuesta = self.client.post(
            reverse("registro"),
            datos,
            follow=True,
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(User.objects.filter(username="nuevo_cp01").exists())
        self.assertTrue(respuesta.wsgi_request.user.is_authenticated)

    def test_cp02_inicio_de_sesion(self):
        """Un usuario registrado puede iniciar sesión."""
        respuesta = self.client.post(
            reverse("login"),
            {
                "username": "votante_cp",
                "password": "ClaveSegura-2027!",
            },
            follow=True,
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.wsgi_request.user.is_authenticated)
        self.assertEqual(respuesta.wsgi_request.user.username, "votante_cp")

    def test_cp03_cierre_de_sesion(self):
        """El cierre de sesión finaliza la autenticación."""
        self.client.force_login(self.usuario)
        respuesta = self.client.post(reverse("logout"), follow=True)
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(respuesta.wsgi_request.user.is_authenticated)

    def test_cp04_consulta_de_ediciones_y_categorias(self):
        """La página de categorías presenta la edición y su categoría."""
        url = reverse(
            "categorias",
            kwargs={"edicion_id": self.edicion.pk},
        )
        respuesta = self.client.get(url)
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Acordeoneros")
        self.assertContains(respuesta, "2027")

    def test_cp05_consulta_de_votaciones_y_opciones(self):
        """La navegación muestra la votación y sus opciones asociadas."""
        url_lista = reverse(
            "votaciones",
            kwargs={"categoria_id": self.categoria.pk},
        )
        respuesta_lista = self.client.get(url_lista)
        self.assertEqual(respuesta_lista.status_code, 200)
        self.assertContains(respuesta_lista, "Mejor acordeonero 2027")

        url_detalle = reverse(
            "detalle_votacion",
            kwargs={"votacion_id": self.votacion.pk},
        )
        respuesta_detalle = self.client.get(url_detalle)
        self.assertEqual(respuesta_detalle.status_code, 200)
        self.assertContains(respuesta_detalle, "Acordeonero A")
        self.assertContains(respuesta_detalle, "Acordeonero B")

    def test_cp06_api_de_categorias_devuelve_json(self):
        """El endpoint GET devuelve categorías, votaciones y opciones."""
        respuesta = self.client.get(reverse("api_categorias"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta["Content-Type"], "application/json")
        datos = respuesta.json()
        categoria = datos["categorias"][0]
        self.assertEqual(categoria["nombre"], "Acordeoneros")
        self.assertEqual(
            categoria["votaciones"][0]["opciones"][0]["nombre"],
            "Acordeonero A",
        )

    def test_cp07_usuario_anonimo_no_puede_votar(self):
        """Un visitante es redirigido al login y no crea registros de voto."""
        respuesta = self.client.post(
            self.url_votar,
            {"opcion": self.opcion.pk},
        )
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse("login"), respuesta.url)
        self.assertEqual(Voto.objects.count(), 0)

    def test_cp08_usuario_autenticado_registra_voto_valido(self):
        """Un usuario autenticado puede registrar un voto permitido."""
        self.client.force_login(self.usuario)
        respuesta = self.client.post(
            self.url_votar,
            {"opcion": self.opcion.pk},
            follow=True,
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Voto.objects.count(), 1)
        voto = Voto.objects.get()
        self.assertEqual(voto.usuario, self.usuario)
        self.assertEqual(voto.votacion, self.votacion)
        self.assertEqual(voto.opcion, self.opcion)

    def test_cp09_no_se_permite_voto_duplicado(self):
        """El segundo voto del mismo usuario para la votación se rechaza."""
        self.client.force_login(self.usuario)
        self.client.post(self.url_votar, {"opcion": self.opcion.pk})
        respuesta = self.client.post(
            self.url_votar,
            {"opcion": self.opcion_b.pk},
            follow=True,
        )
        self.assertContains(respuesta, "Ya registraste tu voto")
        self.assertEqual(
            Voto.objects.filter(
                usuario=self.usuario,
                votacion=self.votacion,
            ).count(),
            1,
        )

    def test_cp10_historial_personal_y_consulta_administrativa(self):
        """
        El usuario consulta solo su voto y el administrador puede ver el listado.
        """
        Voto.objects.create(
            usuario=self.usuario,
            votacion=self.votacion,
            opcion=self.opcion,
        )
        Voto.objects.create(
            usuario=self.otro_usuario,
            votacion=self.votacion,
            opcion=self.opcion_b,
        )

        self.client.force_login(self.usuario)
        respuesta_historial = self.client.get(reverse("mis_votos"))
        self.assertEqual(respuesta_historial.status_code, 200)
        self.assertContains(respuesta_historial, "Acordeonero A")
        self.assertNotContains(respuesta_historial, "Acordeonero B")

        administrador = User.objects.create_superuser(
            username="admin_cp",
            email="admin_cp@example.test",
            password="ClaveSegura-2027!",
        )
        self.client.force_login(administrador)
        respuesta_admin = self.client.get(
            reverse("admin:votaciones_voto_changelist")
        )
        self.assertEqual(respuesta_admin.status_code, 200)
        self.assertContains(respuesta_admin, "votante_cp")
        self.assertContains(respuesta_admin, "otro_cp")
