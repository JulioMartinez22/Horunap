from django.contrib import admin
from .models import Horario, Asignacion, ConflictoHorario, DisponibilidadDocente, HorarioPersonalizadoDocente

@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'semestre', 'estado', 'fecha_creacion', 'creado_por']
    list_filter = ['estado', 'semestre']
    search_fields = ['nombre', 'semestre']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']

@admin.register(Asignacion)
class AsignacionAdmin(admin.ModelAdmin):
    list_display = ['curso', 'docente', 'aula', 'dia_semana', 'bloque_horario', 'activa']
    list_filter = ['dia_semana', 'bloque_horario', 'activa', 'horario']
    search_fields = ['curso__nombre', 'docente__username', 'aula__nombre']

@admin.register(ConflictoHorario)
class ConflictoHorarioAdmin(admin.ModelAdmin):
    list_display = ['tipo_conflicto', 'asignacion', 'fecha_deteccion', 'resuelto']
    list_filter = ['tipo_conflicto', 'resuelto', 'horario']
    search_fields = ['asignacion__curso__nombre', 'descripcion']
    readonly_fields = ['fecha_deteccion']

@admin.register(DisponibilidadDocente)
class DisponibilidadDocenteAdmin(admin.ModelAdmin):
    list_display = ['docente', 'dia_semana', 'bloque_horario', 'disponible', 'fecha_actualizacion']
    list_filter = ['dia_semana', 'bloque_horario', 'disponible', 'docente']
    search_fields = ['docente__username', 'docente__first_name', 'docente__last_name']
    readonly_fields = ['fecha_actualizacion']

# NUEVO ADMIN PARA HORARIOS PERSONALIZADOS
@admin.register(HorarioPersonalizadoDocente)
class HorarioPersonalizadoDocenteAdmin(admin.ModelAdmin):
    list_display = ['docente', 'dia_semana', 'hora_inicio', 'hora_fin', 'tipo', 'descripcion', 'fecha_creacion']
    list_filter = ['dia_semana', 'tipo', 'docente']
    search_fields = ['docente__username', 'docente__first_name', 'docente__last_name', 'descripcion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    list_per_page = 20
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('docente', 'dia_semana', 'tipo')
        }),
        ('Horario', {
            'fields': ('hora_inicio', 'hora_fin', 'descripcion')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )