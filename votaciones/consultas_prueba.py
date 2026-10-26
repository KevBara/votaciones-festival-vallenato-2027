
from votaciones.models import Edicion, Categoria, Votacion, Opcion

print("\n=== EDICIONES ===")
for edicion in Edicion.objects.all():
    print(edicion.nombre, edicion.anio)

print("\n=== CATEGORIAS ===")
for categoria in Categoria.objects.select_related("edicion"):
    print(categoria.nombre, "-", categoria.edicion.anio)

print("\n=== VOTACIONES ===")
for votacion in Votacion.objects.select_related("categoria"):
    print(votacion.titulo, "-", votacion.categoria.nombre)

print("\n=== PARTICIPANTES ===")
for opcion in Opcion.objects.select_related(
    "votacion__categoria__edicion"
):
    print(
        opcion.votacion.categoria.edicion.anio,
        opcion.votacion.categoria.nombre,
        opcion.votacion.titulo,
        opcion.nombre
    )
