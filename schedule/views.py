from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from .models import Horario, Asignacion, ConflictoHorario, DisponibilidadDocente
from .serializers import (
    HorarioSerializer, AsignacionSerializer, AsignacionCreateSerializer,
    ConflictoHorarioSerializer, GenerarHorarioSerializer, EstadisticasHorarioSerializer,
    DisponibilidadDocenteSerializer, DisponibilidadMasivaSerializer
)
from .core.algorithm import GeneradorHorarios, ResolvedorConflictos

class HorarioViewSet(viewsets.ModelViewSet):
    queryset = Horario.objects.all()
    serializer_class = HorarioSerializer

    def get_queryset(self):
        queryset = Horario.objects.all()

        # Filtros
        estado = self.request.query_params.get('estado', None)
        semestre = self.request.query_params.get('semestre', None)
        search = self.request.query_params.get('search', None)

        if estado:
            queryset = queryset.filter(estado=estado)
        if semestre:
            queryset = queryset.filter(semestre__icontains=semestre)
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(semestre__icontains=search)
            )

        return queryset

    def perform_create(self, serializer):
        # Asignar automáticamente el usuario que crea el horario
        serializer.save(creado_por=self.request.user)

    @action(detail=True, methods=['post'])
    def generar_automatico(self, request, pk=None):
        """
        Genera automáticamente un horario usando el algoritmo inteligente
        """
        horario = self.get_object()

        if horario.estado not in ['BORRADOR', 'GENERADO']:
            return Response(
                {'error': 'No se puede generar un horario en estado actual'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            generador = GeneradorHorarios(horario.id)
            asignaciones_creadas = generador.generar_horario()

            # Detectar conflictos después de la generación
            generador.detectar_conflictos()

            return Response({
                'message': f'Horario generado exitosamente. {asignaciones_creadas} asignaciones creadas.',
                'asignaciones_creadas': asignaciones_creadas,
                'estado': 'GENERADO'
            })

        except Exception as e:
            return Response(
                {'error': f'Error al generar horario: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def resolver_conflictos(self, request, pk=None):
        """
        Resuelve automáticamente los conflictos del horario
        """
        horario = self.get_object()

        try:
            resolvedor = ResolvedorConflictos(horario.id)
            conflictos_resueltos = resolvedor.resolver_conflictos()

            return Response({
                'message': f'Se resolvieron {conflictos_resueltos} conflictos automáticamente.',
                'conflictos_resueltos': conflictos_resueltos
            })

        except Exception as e:
            return Response(
                {'error': f'Error al resolver conflictos: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def estadisticas(self, request, pk=None):
        """
        Obtiene estadísticas detalladas del horario
        """
        horario = self.get_object()

        total_asignaciones = horario.asignaciones.count()
        asignaciones_activas = horario.asignaciones.filter(activa=True).count()
        total_conflictos = horario.conflictos.count()
        conflictos_resueltos = horario.conflictos.filter(resuelto=True).count()

        # Calcular porcentaje de ocupación
        total_bloques_posibles = 5 * 6  # 5 días × 6 bloques por día
        porcentaje_ocupacion = (asignaciones_activas / total_bloques_posibles * 100) if total_bloques_posibles > 0 else 0

        # Aulas y docentes utilizados
        aulas_utilizadas = horario.asignaciones.values('aula').distinct().count()
        docentes_asignados = horario.asignaciones.values('docente').distinct().count()

        estadisticas = {
            'total_asignaciones': total_asignaciones,
            'asignaciones_activas': asignaciones_activas,
            'total_conflictos': total_conflictos,
            'conflictos_resueltos': conflictos_resueltos,
            'porcentaje_ocupacion': round(porcentaje_ocupacion, 2),
            'aulas_utilizadas': aulas_utilizadas,
            'docentes_asignados': docentes_asignados
        }

        serializer = EstadisticasHorarioSerializer(estadisticas)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def asignaciones(self, request, pk=None):
        """
        Obtiene todas las asignaciones de un horario específico
        """
        horario = self.get_object()
        asignaciones = horario.asignaciones.all()

        # Filtros opcionales
        dia = request.query_params.get('dia', None)
        docente = request.query_params.get('docente', None)
        aula = request.query_params.get('aula', None)

        if dia:
            asignaciones = asignaciones.filter(dia_semana=dia)
        if docente:
            asignaciones = asignaciones.filter(docente_id=docente)
        if aula:
            asignaciones = asignaciones.filter(aula_id=aula)

        serializer = AsignacionSerializer(asignaciones, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def conflictos(self, request, pk=None):
        """
        Obtiene todos los conflictos de un horario específico
        """
        horario = self.get_object()
        conflictos = horario.conflictos.all()

        # Filtrar por tipo de conflicto o estado de resolución
        tipo = request.query_params.get('tipo', None)
        resuelto = request.query_params.get('resuelto', None)

        if tipo:
            conflictos = conflictos.filter(tipo_conflicto=tipo)
        if resuelto is not None:
            conflictos = conflictos.filter(resuelto=resuelto.lower() == 'true')

        serializer = ConflictoHorarioSerializer(conflictos, many=True)
        return Response(serializer.data)

class AsignacionViewSet(viewsets.ModelViewSet):
    queryset = Asignacion.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AsignacionCreateSerializer
        return AsignacionSerializer

    def get_queryset(self):
        queryset = Asignacion.objects.all()

        # Filtros
        horario = self.request.query_params.get('horario', None)
        docente = self.request.query_params.get('docente', None)
        aula = self.request.query_params.get('aula', None)
        dia = self.request.query_params.get('dia', None)
        activa = self.request.query_params.get('activa', None)

        if horario:
            queryset = queryset.filter(horario_id=horario)
        if docente:
            queryset = queryset.filter(docente_id=docente)
        if aula:
            queryset = queryset.filter(aula_id=aula)
        if dia:
            queryset = queryset.filter(dia_semana=dia)
        if activa is not None:
            queryset = queryset.filter(activa=activa.lower() == 'true')

        return queryset

    @action(detail=True, methods=['post'])
    def toggle_activa(self, request, pk=None):
        """
        Activa/desactiva una asignación
        """
        asignacion = self.get_object()
        asignacion.activa = not asignacion.activa
        asignacion.save()

        estado = "activada" if asignacion.activa else "desactivada"
        return Response({
            'message': f'Asignación {estado} exitosamente.',
            'activa': asignacion.activa
        })

class ConflictoHorarioViewSet(viewsets.ModelViewSet):
    queryset = ConflictoHorario.objects.all()
    serializer_class = ConflictoHorarioSerializer

    def get_queryset(self):
        queryset = ConflictoHorario.objects.all()

        # Filtros
        horario = self.request.query_params.get('horario', None)
        tipo = self.request.query_params.get('tipo', None)
        resuelto = self.request.query_params.get('resuelto', None)

        if horario:
            queryset = queryset.filter(horario_id=horario)
        if tipo:
            queryset = queryset.filter(tipo_conflicto=tipo)
        if resuelto is not None:
            queryset = queryset.filter(resuelto=resuelto.lower() == 'true')

        return queryset

    @action(detail=True, methods=['post'])
    def marcar_resuelto(self, request, pk=None):
        """
        Marca un conflicto como resuelto
        """
        from django.utils import timezone

        conflicto = self.get_object()
        conflicto.resuelto = True
        conflicto.fecha_resolucion = timezone.now()
        conflicto.save()

        return Response({
            'message': 'Conflicto marcado como resuelto.',
            'resuelto': True,
            'fecha_resolucion': conflicto.fecha_resolucion
        })

    @action(detail=False, methods=['get'])
    def estadisticas_globales(self, request):
        """
        Estadísticas globales de conflictos
        """
        total_conflictos = ConflictoHorario.objects.count()
        conflictos_resueltos = ConflictoHorario.objects.filter(resuelto=True).count()
        conflictos_por_tipo = ConflictoHorario.objects.values('tipo_conflicto').annotate(
            total=Count('id')
        )

        return Response({
            'total_conflictos': total_conflictos,
            'conflictos_resueltos': conflictos_resueltos,
            'conflictos_pendientes': total_conflictos - conflictos_resueltos,
            'por_tipo': list(conflictos_por_tipo)
        })

# NUEVO VIEWSET AGREGADO
class DisponibilidadDocenteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar la disponibilidad de docentes
    """
    queryset = DisponibilidadDocente.objects.all()
    serializer_class = DisponibilidadDocenteSerializer

    def get_queryset(self):
        queryset = DisponibilidadDocente.objects.all()
        
        # Filtrar por docente
        docente = self.request.query_params.get('docente', None)
        if docente:
            queryset = queryset.filter(docente_id=docente)
            
        # Filtrar por día
        dia = self.request.query_params.get('dia', None)
        if dia:
            queryset = queryset.filter(dia_semana=dia)

        # Filtrar por disponibilidad
        disponible = self.request.query_params.get('disponible', None)
        if disponible is not None:
            queryset = queryset.filter(disponible=disponible.lower() == 'true')
            
        return queryset

    @action(detail=False, methods=['post'])
    def actualizar_masivo(self, request):
        """
        Actualizar disponibilidad masiva para un docente
        """
        serializer = DisponibilidadMasivaSerializer(data=request.data)
        if serializer.is_valid():
            docente = serializer.validated_data['docente']
            disponibilidades = serializer.validated_data['disponibilidades']
            
            try:
                for disp_data in disponibilidades:
                    DisponibilidadDocente.objects.update_or_create(
                        docente=docente,
                        dia_semana=disp_data['dia_semana'],
                        bloque_horario=disp_data['bloque_horario'],
                        defaults={'disponible': disp_data['disponible']}
                    )
                
                return Response({'message': 'Disponibilidad actualizada exitosamente'})
                
            except Exception as e:
                return Response(
                    {'error': f'Error al actualizar disponibilidad: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def por_docente(self, request):
        """
        Obtener toda la disponibilidad de un docente específico
        """
        docente_id = request.query_params.get('docente')
        if not docente_id:
            return Response(
                {'error': 'Se requiere el parámetro docente'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        disponibilidades = DisponibilidadDocente.objects.filter(docente_id=docente_id)
        serializer = self.get_serializer(disponibilidades, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def resumen_disponibilidad(self, request):
        """
        Resumen de disponibilidad por docente
        """
        from django.db.models import Count
        
        resumen = DisponibilidadDocente.objects.values(
            'docente__username', 
            'docente__first_name', 
            'docente__last_name'
        ).annotate(
            total_bloques=Count('id'),
            bloques_disponibles=Count('id', filter=Q(disponible=True)),
            bloques_no_disponibles=Count('id', filter=Q(disponible=False))
        )
        
        return Response(list(resumen))