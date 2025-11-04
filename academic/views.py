from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Curso, Aula
from .serializers import (
    CursoSerializer, CursoCreateSerializer, 
    AulaSerializer, AulaCreateSerializer
)

class CursoViewSet(viewsets.ModelViewSet):
    queryset = Curso.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CursoCreateSerializer
        return CursoSerializer
    
    def get_queryset(self):
        queryset = Curso.objects.all()
        
        # Filtros
        tipo = self.request.query_params.get('tipo', None)
        activo = self.request.query_params.get('activo', None)
        search = self.request.query_params.get('search', None)
        
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        if activo is not None:
            queryset = queryset.filter(activo=activo.lower() == 'true')
        if search:
            queryset = queryset.filter(
                Q(codigo__icontains=search) | 
                Q(nombre__icontains=search)
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        total_cursos = Curso.objects.count()
        cursos_activos = Curso.objects.filter(activo=True).count()
        cursos_obligatorios = Curso.objects.filter(tipo='OBLIGATORIO').count()
        cursos_electivos = Curso.objects.filter(tipo='ELECTIVO').count()
        
        return Response({
            'total_cursos': total_cursos,
            'cursos_activos': cursos_activos,
            'cursos_obligatorios': cursos_obligatorios,
            'cursos_electivos': cursos_electivos,
        })

class AulaViewSet(viewsets.ModelViewSet):
    queryset = Aula.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AulaCreateSerializer
        return AulaSerializer
    
    def get_queryset(self):
        queryset = Aula.objects.all()
        
        # Filtros
        tipo = self.request.query_params.get('tipo', None)
        activa = self.request.query_params.get('activa', None)
        capacidad_min = self.request.query_params.get('capacidad_min', None)
        search = self.request.query_params.get('search', None)
        
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        if activa is not None:
            queryset = queryset.filter(activa=activa.lower() == 'true')
        if capacidad_min:
            queryset = queryset.filter(capacidad__gte=int(capacidad_min))
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) | 
                Q(edificio__icontains=search)
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        """Aulas disponibles para asignación"""
        aulas = Aula.objects.filter(activa=True)
        serializer = self.get_serializer(aulas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        total_aulas = Aula.objects.count()
        aulas_activas = Aula.objects.filter(activa=True).count()
        capacidad_total = sum(aula.capacidad for aula in Aula.objects.filter(activa=True))
        
        return Response({
            'total_aulas': total_aulas,
            'aulas_activas': aulas_activas,
            'capacidad_total': capacidad_total,
        })