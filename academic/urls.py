from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'cursos', views.CursoViewSet, basename='curso')
router.register(r'aulas', views.AulaViewSet, basename='aula')

urlpatterns = [
    path('', include(router.urls)),
]