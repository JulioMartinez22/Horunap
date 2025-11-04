from rest_framework import serializers
from .models import Horario, Asignacion, ConflictoHorario, DisponibilidadDocente
from academic.serializers import CursoSerializer, AulaSerializer
from users.serializers import UserSerializer

class HorarioSerializer(serializers.ModelSerializer):
    creado_por_nombre = serializers.CharField(source='creado_por.get_full_name', read_only=True)
    total_asignaciones = serializers.SerializerMethodField()
    total_conflictos = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Horario
        fields = [
            'id', 'nombre', 'semestre', 'estado', 'estado_display',
            'fecha_creacion', 'fecha_actualizacion', 'creado_por',
            'creado_por_nombre', 'total_asignaciones', 'total_conflictos'
        ]
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion', 'creado_por']

    def get_total_asignaciones(self, obj):
        return obj.asignaciones.count()

    def get_total_conflictos(self, obj):
        return obj.conflictos.count()

class AsignacionSerializer(serializers.ModelSerializer):
    curso_info = CursoSerializer(source='curso', read_only=True)
    docente_info = UserSerializer(source='docente', read_only=True)
    aula_info = AulaSerializer(source='aula', read_only=True)
    dia_display = serializers.CharField(source='get_dia_semana_display', read_only=True)
    bloque_display = serializers.CharField(source='get_bloque_horario_display', read_only=True)

    class Meta:
        model = Asignacion
        fields = [
            'id', 'horario', 'curso', 'curso_info', 'docente', 'docente_info',
            'aula', 'aula_info', 'dia_semana', 'dia_display', 'bloque_horario',
            'bloque_display', 'fecha_asignacion', 'activa'
        ]

class AsignacionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asignacion
        fields = [
            'horario', 'curso', 'docente', 'aula',
            'dia_semana', 'bloque_horario', 'activa'
        ]

    def validate(self, data):
        # Validar que no haya conflictos de horario
        horario = data['horario']
        docente = data['docente']
        aula = data['aula']
        dia_semana = data['dia_semana']
        bloque_horario = data['bloque_horario']

        # Verificar conflicto de docente
        if Asignacion.objects.filter(
            horario=horario,
            docente=docente,
            dia_semana=dia_semana,
            bloque_horario=bloque_horario
        ).exists():
            raise serializers.ValidationError(
                "El docente ya tiene una asignación en este horario"
            )

        # Verificar conflicto de aula
        if Asignacion.objects.filter(
            horario=horario,
            aula=aula,
            dia_semana=dia_semana,
            bloque_horario=bloque_horario
        ).exists():
            raise serializers.ValidationError(
                "El aula ya está ocupada en este horario"
            )

        return data

class ConflictoHorarioSerializer(serializers.ModelSerializer):
    asignacion_info = AsignacionSerializer(source='asignacion', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_conflicto_display', read_only=True)

    class Meta:
        model = ConflictoHorario
        fields = [
            'id', 'horario', 'asignacion', 'asignacion_info',
            'tipo_conflicto', 'tipo_display', 'descripcion',
            'fecha_deteccion', 'resuelto', 'fecha_resolucion'
        ]
        read_only_fields = ['fecha_deteccion', 'fecha_resolucion']

# NUEVO SERIALIZER AGREGADO
class DisponibilidadDocenteSerializer(serializers.ModelSerializer):
    docente_info = UserSerializer(source='docente', read_only=True)
    dia_display = serializers.CharField(source='get_dia_semana_display', read_only=True)
    bloque_display = serializers.CharField(source='get_bloque_horario_display', read_only=True)

    class Meta:
        model = DisponibilidadDocente
        fields = [
            'id', 'docente', 'docente_info', 'dia_semana', 'dia_display',
            'bloque_horario', 'bloque_display', 'disponible', 'fecha_actualizacion'
        ]
        read_only_fields = ['fecha_actualizacion']

class DisponibilidadMasivaSerializer(serializers.Serializer):
    """
    Serializer para actualización masiva de disponibilidad
    """
    docente = serializers.IntegerField()
    disponibilidades = serializers.ListField(
        child=serializers.DictField(
            child=serializers.BooleanField()
        )
    )

    def validate_docente(self, value):
        from users.models import User
        try:
            docente = User.objects.get(id=value, rol='DOCENTE')
            return docente
        except User.DoesNotExist:
            raise serializers.ValidationError("Docente no encontrado")

class GenerarHorarioSerializer(serializers.Serializer):
    """Serializer para la generación de horarios"""
    nombre = serializers.CharField(max_length=100)
    semestre = serializers.CharField(max_length=20)
    configuracion = serializers.JSONField(default=dict)

    def validate_configuracion(self, value):
        configuraciones_validas = {
            'dias_semana': ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES'],
            'bloques_horarios': ['08:00-10:00', '10:00-12:00', '14:00-16:00', '16:00-18:00'],
            'max_intentos_por_curso': 1000
        }

        # Validar que las configuraciones sean correctas
        if 'dias_semana' in value:
            dias_validos = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO']
            for dia in value['dias_semana']:
                if dia not in dias_validos:
                    raise serializers.ValidationError(f"Día no válido: {dia}")

        return value

class EstadisticasHorarioSerializer(serializers.Serializer):
    """Serializer para estadísticas del horario"""
    total_asignaciones = serializers.IntegerField()
    asignaciones_activas = serializers.IntegerField()
    total_conflictos = serializers.IntegerField()
    conflictos_resueltos = serializers.IntegerField()
    porcentaje_ocupacion = serializers.FloatField()
    aulas_utilizadas = serializers.IntegerField()
    docentes_asignados = serializers.IntegerField()