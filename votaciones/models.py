
from django.db import models
from django.core.exceptions import ValidationError


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
