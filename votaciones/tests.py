from concurrent.futures import ThreadPoolExecutor
from datetime import date
from datetime import timedelta
from threading import Barrier

from django.conf import settings
from django.contrib.auth.models import User
from django.db import IntegrityError, close_old_connections, transaction
from django.test import Client, TestCase, TransactionTestCase, skipUnlessDBFeature
from django.urls import reverse
from django.utils import timezone

from .models import Categoria, Edicion, Opcion, Votacion, Voto


class FlujoVotacionTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(
            username="votante",
            password="ClaveSegura-2027"
        )
        self.edicion = Edicion.objects.create(
            nombre="Festival de la Leyenda Vallenata",
            anio=2027,
            fecha_inicio=date(2027, 4, 1),
            fecha_fin=date(2027, 4, 30)
        )
        self.categoria = Categoria.objects.create(
            edicion=self.edicion,
            nombre="Acordeoneros"
        )
        ahora = timezone.now()
        self.votacion = Votacion.objects.create(
            categoria=self.categoria,
            titulo="Mejor acordeonero",
            fecha_inicio=ahora - timedelta(days=1),
            fecha_fin=ahora + timedelta(days=1),
            activa=True
        )
        self.opcion = Opcion.objects.create(
            votacion=self.votacion,
            nombre="Participante A"
        )
        self.otra_votacion = Votacion.objects.create(
            categoria=self.categoria,
            titulo="Mejor canción",
            fecha_inicio=ahora - timedelta(days=1),
            fecha_fin=ahora + timedelta(days=1),
            activa=True
        )
        self.opcion_ajena = Opcion.objects.create(
            votacion=self.otra_votacion,
            nombre="Participante de otra votación"
        )
        self.url = reverse(
            "registrar_voto",
            kwargs={"votacion_id": self.votacion.id}
        )

    def test_formulario_de_registro_muestra_textos_en_espanol(self):
        respuesta = self.client.get(reverse("registro"))

        self.assertContains(respuesta, "Nombre de usuario")
        self.assertContains(respuesta, "Correo electrónico")
        self.assertContains(respuesta, "La contraseña debe tener al menos")
        self.assertContains(respuesta, "Escribe nuevamente la contraseña")

        respuesta_invalida = self.client.post(reverse("registro"), {})
        self.assertContains(respuesta_invalida, "Este campo es obligatorio.")

    def test_usuario_autenticado_puede_votar(self):
        self.client.force_login(self.usuario)

        respuesta = self.client.post(
            self.url,
            {"opcion": self.opcion.id},
            follow=True
        )

        self.assertRedirects(
            respuesta,
            f"{reverse('detalle_votacion', kwargs={'votacion_id': self.votacion.id})}?confirmado=1"
        )
        self.assertEqual(Voto.objects.count(), 1)
        self.assertEqual(Voto.objects.get().opcion, self.opcion)
        self.assertContains(respuesta, "Voto registrado")
        self.assertContains(respuesta, "Continuar a Acordeoneros")
        self.assertContains(
            respuesta,
            reverse(
                "detalle_votacion",
                kwargs={"votacion_id": self.otra_votacion.id}
            )
        )
        respuesta_persistente = self.client.get(
            reverse(
                "detalle_votacion",
                kwargs={"votacion_id": self.votacion.id}
            )
        )
        self.assertContains(respuesta_persistente, "Tu voto:</strong> Participante A")
        self.assertContains(respuesta_persistente, "¡Gracias por participar!")
        self.assertNotContains(
            respuesta_persistente,
            "Tu voto se registró correctamente."
        )

    def test_usuario_anonimo_es_enviado_a_login_con_destino(self):
        respuesta = self.client.post(
            self.url,
            {"opcion": self.opcion.id}
        )

        self.assertRedirects(
            respuesta,
            f"{reverse('login')}?next={self.url}"
        )
        self.assertEqual(Voto.objects.count(), 0)

    def test_segundo_voto_es_rechazado(self):
        self.client.force_login(self.usuario)
        self.client.post(self.url, {"opcion": self.opcion.id})

        respuesta = self.client.post(
            self.url,
            {"opcion": self.opcion.id},
            follow=True
        )

        self.assertContains(respuesta, "Ya registraste tu voto")
        self.assertEqual(Voto.objects.count(), 1)

    def test_opcion_de_otra_votacion_es_rechazada(self):
        self.client.force_login(self.usuario)

        respuesta = self.client.post(
            self.url,
            {"opcion": self.opcion_ajena.id},
            follow=True
        )

        self.assertContains(respuesta, "Selecciona una opción válida")
        self.assertEqual(Voto.objects.count(), 0)

    def test_votacion_inactiva_o_fuera_de_fecha_no_acepta_votos(self):
        self.client.force_login(self.usuario)
        self.votacion.activa = False
        self.votacion.save(update_fields=["activa"])

        respuesta = self.client.post(
            self.url,
            {"opcion": self.opcion.id},
            follow=True
        )

        self.assertContains(respuesta, "no está habilitada")
        self.assertEqual(Voto.objects.count(), 0)

        self.votacion.activa = True
        self.votacion.fecha_fin = timezone.now() - timedelta(minutes=1)
        self.votacion.save(update_fields=["activa", "fecha_fin"])
        self.client.post(self.url, {"opcion": self.opcion.id})
        self.assertEqual(Voto.objects.count(), 0)

    def test_categoria_inhabilitada_no_acepta_votos(self):
        self.client.force_login(self.usuario)
        self.categoria.habilitada = False
        self.categoria.save(update_fields=["habilitada"])

        respuesta = self.client.post(
            self.url,
            {"opcion": self.opcion.id},
            follow=True
        )

        self.assertContains(respuesta, "no está habilitada")
        self.assertEqual(Voto.objects.count(), 0)

    def test_post_de_voto_requiere_csrf(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(self.usuario)

        respuesta = cliente.post(
            self.url,
            {"opcion": self.opcion.id}
        )

        self.assertEqual(respuesta.status_code, 403)
        self.assertEqual(Voto.objects.count(), 0)

    def test_solo_se_acepta_post(self):
        self.client.force_login(self.usuario)

        respuesta = self.client.get(self.url)

        self.assertEqual(respuesta.status_code, 405)
        self.assertEqual(Voto.objects.count(), 0)

    def test_base_de_datos_rechaza_voto_duplicado(self):
        Voto.objects.create(
            usuario=self.usuario,
            votacion=self.votacion,
            opcion=self.opcion
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Voto.objects.create(
                    usuario=self.usuario,
                    votacion=self.votacion,
                    opcion=self.opcion
                )

        self.assertEqual(Voto.objects.count(), 1)

    def test_detalle_muestra_opciones_y_formulario_solo_con_sesion(self):
        respuesta_publica = self.client.get(
            reverse(
                "detalle_votacion",
                kwargs={"votacion_id": self.votacion.id}
            )
        )
        self.assertContains(respuesta_publica, "Participante A")
        self.assertContains(respuesta_publica, "debes iniciar sesión")

        self.client.force_login(self.usuario)
        respuesta_autenticada = self.client.get(
            reverse(
                "detalle_votacion",
                kwargs={"votacion_id": self.votacion.id}
            )
        )
        self.assertContains(respuesta_autenticada, "Confirmar mi voto")

    def test_categoria_muestra_estado_de_voto_del_usuario(self):
        url = reverse(
            "categorias",
            kwargs={"edicion_id": self.edicion.id}
        )
        self.client.force_login(self.usuario)

        respuesta_pendiente = self.client.get(url)
        self.assertContains(respuesta_pendiente, "Pendiente")
        self.assertContains(respuesta_pendiente, "0 de 2 votaciones completadas")

        Voto.objects.create(
            usuario=self.usuario,
            votacion=self.votacion,
            opcion=self.opcion
        )
        respuesta_en_progreso = self.client.get(url)
        self.assertContains(respuesta_en_progreso, "En progreso")
        self.assertContains(respuesta_en_progreso, "1 de 2 votaciones completadas")

        Voto.objects.create(
            usuario=self.usuario,
            votacion=self.otra_votacion,
            opcion=self.opcion_ajena
        )
        respuesta_completada = self.client.get(url)
        self.assertContains(respuesta_completada, "Votaste")
        self.assertContains(respuesta_completada, "2 de 2 votaciones completadas")

    def test_completar_ultima_votacion_muestra_salida_a_categorias(self):
        Voto.objects.create(
            usuario=self.usuario,
            votacion=self.votacion,
            opcion=self.opcion
        )
        Voto.objects.create(
            usuario=self.usuario,
            votacion=self.otra_votacion,
            opcion=self.opcion_ajena
        )
        self.client.force_login(self.usuario)

        respuesta = self.client.get(
            reverse(
                "detalle_votacion",
                kwargs={"votacion_id": self.votacion.id}
            )
        )

        self.assertContains(respuesta, "¡Completaste todas las votaciones!")
        self.assertContains(respuesta, "Volver a categorías")
        self.assertNotContains(respuesta, "Continuar a Acordeoneros")

    def test_opciones_muestran_imagen_cuando_se_configura(self):
        self.opcion.imagen_url = "https://example.com/participante.jpg"
        self.opcion.save(update_fields=["imagen_url"])
        self.client.force_login(self.usuario)

        respuesta = self.client.get(
            reverse(
                "detalle_votacion",
                kwargs={"votacion_id": self.votacion.id}
            )
        )

        self.assertContains(respuesta, "https://example.com/participante.jpg")
        self.assertContains(respuesta, "participant-image")

    def test_votaciones_sin_opciones_no_bloquean_el_progreso(self):
        Votacion.objects.create(
            categoria=self.categoria,
            titulo="Votación sin participantes",
            fecha_inicio=timezone.now() - timedelta(days=1),
            fecha_fin=timezone.now() + timedelta(days=1),
            activa=True
        )
        Voto.objects.create(
            usuario=self.usuario,
            votacion=self.votacion,
            opcion=self.opcion
        )
        Voto.objects.create(
            usuario=self.usuario,
            votacion=self.otra_votacion,
            opcion=self.opcion_ajena
        )
        self.client.force_login(self.usuario)

        respuesta_detalle = self.client.get(
            reverse(
                "detalle_votacion",
                kwargs={"votacion_id": self.votacion.id}
            )
        )
        respuesta_categorias = self.client.get(
            reverse(
                "categorias",
                kwargs={"edicion_id": self.edicion.id}
            )
        )

        self.assertContains(respuesta_detalle, "¡Completaste todas las votaciones!")
        self.assertContains(respuesta_categorias, "2 de 2 votaciones completadas")


class VotoConcurrenteTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        usuario = User.objects.create_user(
            username="concurrente",
            password="ClaveSegura-2027"
        )
        edicion = Edicion.objects.create(
            nombre="Festival de la Leyenda Vallenata",
            anio=2027,
            fecha_inicio=date(2027, 4, 1),
            fecha_fin=date(2027, 4, 30)
        )
        categoria = Categoria.objects.create(
            edicion=edicion,
            nombre="Acordeoneros"
        )
        ahora = timezone.now()
        self.votacion = Votacion.objects.create(
            categoria=categoria,
            titulo="Votación concurrente",
            fecha_inicio=ahora - timedelta(days=1),
            fecha_fin=ahora + timedelta(days=1),
            activa=True
        )
        self.opcion = Opcion.objects.create(
            votacion=self.votacion,
            nombre="Participante A"
        )
        cliente = Client()
        cliente.force_login(usuario)
        self.session_key = cliente.session.session_key
        self.usuario_id = usuario.id

    @skipUnlessDBFeature("has_select_for_update")
    def test_dos_solicitudes_simultaneas_crean_un_solo_voto(self):
        url = reverse(
            "registrar_voto",
            kwargs={"votacion_id": self.votacion.id}
        )
        barrera = Barrier(2)

        def enviar_voto():
            close_old_connections()
            try:
                cliente = Client()
                cliente.cookies[settings.SESSION_COOKIE_NAME] = self.session_key
                barrera.wait(timeout=10)
                return cliente.post(url, {"opcion": self.opcion.id}).status_code
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            respuestas = list(executor.map(lambda _: enviar_voto(), range(2)))

        self.assertEqual(respuestas, [302, 302])
        self.assertEqual(
            Voto.objects.filter(
                usuario_id=self.usuario_id,
                votacion=self.votacion
            ).count(),
            1
        )


# PRUEBAS PERSONA 3: API E HISTORIAL

class Persona3Tests(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user(
            username="usuario_prueba_p3",
            password="ClaveSegura2027!"
        )

        self.otro_usuario = User.objects.create_user(
            username="otro_usuario_p3",
            password="ClaveSegura2027!"
        )

        self.edicion = Edicion.objects.create(
            nombre="Festival Vallenato",
            anio=2027,
            fecha_inicio=date(2027, 4, 1),
            fecha_fin=date(2027, 4, 30)
        )

        self.categoria = Categoria.objects.create(
            edicion=self.edicion,
            nombre="Acordeoneros"
        )

        ahora = timezone.now()

        self.votacion = Votacion.objects.create(
            categoria=self.categoria,
            titulo="Mejor acordeonero 2027",
            fecha_inicio=ahora - timedelta(days=1),
            fecha_fin=ahora + timedelta(days=1),
            activa=True
        )

        self.opcion = Opcion.objects.create(
            votacion=self.votacion,
            nombre="Acordeonero B"
        )

    def test_api_devuelve_json(self):
        respuesta = self.client.get("/api/categorias/")

        self.assertEqual(respuesta.status_code, 200)

        self.assertEqual(
            respuesta["Content-Type"],
            "application/json"
        )

        datos = respuesta.json()

        self.assertEqual(
            datos["categorias"][0]["nombre"],
            "Acordeoneros"
        )

        self.assertEqual(
            datos["categorias"][0]["votaciones"][0]
            ["opciones"][0]["nombre"],
            "Acordeonero B"
        )

    def test_historial_exige_inicio_sesion(self):
        respuesta = self.client.get("/mis-votos/")

        self.assertEqual(respuesta.status_code, 302)
        self.assertIn("/login/", respuesta.url)

    def test_historial_muestra_voto_propio(self):
        Voto.objects.create(
            usuario=self.usuario,
            votacion=self.votacion,
            opcion=self.opcion
        )

        self.client.force_login(self.usuario)

        respuesta = self.client.get("/mis-votos/")

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Acordeonero B")

    def test_historial_no_muestra_voto_ajeno(self):
        Voto.objects.create(
            usuario=self.otro_usuario,
            votacion=self.votacion,
            opcion=self.opcion
        )

        self.client.force_login(self.usuario)

        respuesta = self.client.get("/mis-votos/")

        self.assertEqual(respuesta.status_code, 200)

        self.assertNotContains(
            respuesta,
            "Acordeonero B"
        )
