from rest_framework import serializers
from .models import Curso, Aula

class CursoSerializer(serializers.ModelSerializer):
    requisitos_list = serializers.SerializerMethodField()
    estado = serializers.SerializerMethodField()
    
    class Meta:
        model = Curso
        fields = [
            'id', 'nombre', 'codigo', 'creditos', 'tipo', 
            'sesiones_semana', 'duracion_sesion', 'requisitos',
            'requisitos_list', 'capacidad_estimada', 
            'equipamiento_requerido', 'activo', 'estado'
        ]
        depth = 1
    
    def get_requisitos_list(self, obj):
        return [f"{curso.codigo} - {curso.nombre}" for curso in obj.requisitos.all()]
    
    def get_estado(self, obj):
        return "Activo" if obj.activo else "Inactivo"

class CursoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = [
            'nombre', 'codigo', 'creditos', 'tipo', 
            'sesiones_semana', 'duracion_sesion', 'requisitos',
            'capacidad_estimada', 'equipamiento_requerido', 'activo'
        ]

class AulaSerializer(serializers.ModelSerializer):
    equipamiento_completo = serializers.SerializerMethodField()
    estado = serializers.SerializerMethodField()
    ubicacion_completa = serializers.SerializerMethodField()
    
    class Meta:
        model = Aula
        fields = [
            'id', 'nombre', 'capacidad', 'tipo', 'edificio', 'piso',
            'tiene_proyector', 'tiene_computadoras', 'tiene_pizarra_digital',
            'equipamiento_adicional', 'equipamiento_completo', 
            'activa', 'estado', 'ubicacion_completa'
        ]
    
    def get_equipamiento_completo(self, obj):
        return obj.get_equipamiento()
    
    def get_estado(self, obj):
        return "Activa" if obj.activa else "Inactiva"
    
    def get_ubicacion_completa(self, obj):
        ubicacion = f"{obj.edificio} - " if obj.edificio else ""
        return f"{ubicacion}{obj.nombre} (Piso {obj.piso})" if obj.piso else f"{ubicacion}{obj.nombre}"

class AulaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aula
        fields = [
            'nombre', 'capacidad', 'tipo', 'edificio', 'piso',
            'tiene_proyector', 'tiene_computadoras', 'tiene_pizarra_digital',
            'equipamiento_adicional', 'activa'
        ]