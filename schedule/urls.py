from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'horarios', views.HorarioViewSet, basename='horario')
router.register(r'asignaciones', views.AsignacionViewSet, basename='asignacion')
router.register(r'conflictos', views.ConflictoHorarioViewSet, basename='conflicto')
router.register(r'disponibilidades', views.DisponibilidadDocenteViewSet, basename='disponibilidad')  # NUEVA RUTA

urlpatterns = [
    path('', include(router.urls)),
]