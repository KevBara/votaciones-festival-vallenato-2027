from django.contrib import admin

from .models import Categoria, Edicion, Opcion, Votacion, Voto


@admin.register(Edicion)
class EdicionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "anio", "fecha_inicio", "fecha_fin")
    ordering = ("-anio",)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "edicion", "habilitada")
    list_filter = ("edicion", "habilitada")


class OpcionInline(admin.TabularInline):
    model = Opcion
    extra = 0


@admin.register(Votacion)
class VotacionAdmin(admin.ModelAdmin):
    list_display = ("titulo", "categoria", "activa", "fecha_inicio", "fecha_fin")
    list_filter = ("activa", "categoria__edicion")
    inlines = (OpcionInline,)


@admin.register(Voto)
class VotoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "votacion", "opcion", "creado_en")
    list_filter = ("votacion", "votacion__categoria__edicion")
    search_fields = ("usuario__username", "votacion__titulo", "opcion__nombre")
    readonly_fields = ("usuario", "votacion", "opcion", "creado_en")

    def has_add_permission(self, request):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.has_perm("votaciones.view_voto")

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
