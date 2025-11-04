from django.contrib import admin
from .models import Curso, Aula

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'creditos', 'tipo', 'sesiones_semana', 'activo']
    list_filter = ['tipo', 'activo']
    search_fields = ['codigo', 'nombre']
    filter_horizontal = ['requisitos']
    list_editable = ['activo']

@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'edificio', 'capacidad', 'tipo', 'tiene_proyector', 'activa']
    list_filter = ['tipo', 'edificio', 'activa', 'tiene_proyector', 'tiene_computadoras']
    search_fields = ['nombre', 'edificio']
    list_editable = ['activa']