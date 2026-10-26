
from datetime import date, datetime
from django.utils import timezone
from votaciones.models import Edicion, Categoria, Votacion, Opcion

edicion, _ = Edicion.objects.get_or_create(
    anio=2027,
    defaults={
        "nombre": "Festival de la Leyenda Vallenata",
        "fecha_inicio": date(2027, 4, 1),
        "fecha_fin": date(2027, 4, 30),
        "descripcion": "Edición 2027 del Festival Vallenato"
    }
)

datos = [
    (
        "Acordeoneros",
        "Mejor acordeonero 2027",
        ["Acordeonero A", "Acordeonero B", "Acordeonero C"]
    ),
    (
        "Canción inédita",
        "Mejor canción inédita 2027",
        ["Canción A", "Canción B", "Canción C"]
    ),
    (
        "Piqueria",
        "Mejor verseador 2027",
        ["Verseador A", "Verseador B", "Verseador C"]
    )
]

inicio = timezone.make_aware(datetime(2027, 4, 1, 8, 0))
fin = timezone.make_aware(datetime(2027, 4, 30, 18, 0))

for nombre_categoria, titulo, participantes in datos:
    categoria, _ = Categoria.objects.get_or_create(
        edicion=edicion,
        nombre=nombre_categoria
    )

    votacion, _ = Votacion.objects.get_or_create(
        categoria=categoria,
        titulo=titulo,
        defaults={
            "fecha_inicio": inicio,
            "fecha_fin": fin,
            "activa": False
        }
    )

    for participante in participantes:
        Opcion.objects.get_or_create(
            votacion=votacion,
            nombre=participante
        )

print("Carga de datos completada")
print("Ediciones:", Edicion.objects.count())
print("Categorias:", Categoria.objects.count())
print("Votaciones:", Votacion.objects.count())
print("Opciones:", Opcion.objects.count())
