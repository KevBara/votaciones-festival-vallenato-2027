
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Edicion(models.Model):
    nombre = models.CharField(max_length=150)
    anio = models.PositiveIntegerField(unique=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    descripcion = models.TextField(blank=True)

    def clean(self):
        if self.fecha_inicio and self.fecha_fin:
            if self.fecha_fin < self.fecha_inicio:
                raise ValidationError(
                    "La fecha final no puede ser anterior a la inicial."
                )

    def __str__(self):
        return f"{self.nombre} - {self.anio}"

    class Meta:
        verbose_name = "Edición"
        verbose_name_plural = "Ediciones"
        ordering = ["-anio"]


class Categoria(models.Model):
    edicion = models.ForeignKey(
        Edicion,
        on_delete=models.CASCADE,
        related_name="categorias"
    )
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    habilitada = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.edicion.anio}"

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        constraints = [
            models.UniqueConstraint(
                fields=["edicion", "nombre"],
                name="categoria_unica_por_edicion"
            )
        ]


class Votacion(models.Model):
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name="votaciones"
    )
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    activa = models.BooleanField(default=False)

    def esta_habilitada(self, ahora=None):
        ahora = ahora or timezone.now()
        return (
            self.categoria.habilitada
            and self.activa
            and self.fecha_inicio <= ahora <= self.fecha_fin
        )

    def clean(self):
        if self.fecha_inicio and self.fecha_fin:
            if self.fecha_fin < self.fecha_inicio:
                raise ValidationError(
                    "La fecha final no puede ser anterior a la inicial."
                )

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Votación"
        verbose_name_plural = "Votaciones"


class Opcion(models.Model):
    votacion = models.ForeignKey(
        Votacion,
        on_delete=models.CASCADE,
        related_name="opciones"
    )
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    imagen_url = models.URLField(
        blank=True,
        max_length=500,
        verbose_name="URL de imagen del participante"
    )

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Opción"
        verbose_name_plural = "Opciones"
        constraints = [
            models.UniqueConstraint(
                fields=["votacion", "nombre"],
                name="opcion_unica_por_votacion"
            )
        ]


class Voto(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="votos_festival"
    )
    votacion = models.ForeignKey(
        Votacion,
        on_delete=models.PROTECT,
        related_name="votos"
    )
    opcion = models.ForeignKey(
        Opcion,
        on_delete=models.PROTECT,
        related_name="votos"
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} - {self.votacion}"

    class Meta:
        verbose_name = "Voto"
        verbose_name_plural = "Votos"
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "votacion"],
                name="voto_unico_usuario_votacion"
            )
        ]
        ordering = ["-creado_en"]
