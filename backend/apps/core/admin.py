from django.contrib import admin

from apps.core.models import (
    EnteSupervisadoCatalog, 
    MecanismoCambiarioCatalog, 
    MonedaCatalog,
    ActividadEconomicaCatalog
)

@admin.register(EnteSupervisadoCatalog)
class EnteSupervisadoCatalogAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_selectable', 'is_active', 'sort_order')
    search_fields = ('code', 'name')
    list_filter = ('is_selectable', 'is_active')
    ordering = ('sort_order', 'code')


@admin.register(MecanismoCambiarioCatalog)
class MecanismoCambiarioCatalogAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_selectable', 'is_active', 'sort_order')
    search_fields = ('code', 'name', 'description')
    list_filter = ('is_selectable', 'is_active')
    ordering = ('sort_order', 'code')


@admin.register(MonedaCatalog)
class MonedaCatalogAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'description', 'is_selectable', 'is_active', 'sort_order')
    search_fields = ('code', 'name', 'description')
    list_filter = ('is_selectable', 'is_active')
    ordering = ('sort_order', 'code')

@admin.register(ActividadEconomicaCatalog)
class ActividadEconomicaCatalogAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_selectable', 'is_active', 'sort_order')
    search_fields = ('code', 'name')
    list_filter = ('is_selectable', 'is_active')
    ordering = ('sort_order', 'code')
