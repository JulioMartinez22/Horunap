from django.urls import path
from . import views

urlpatterns = [
    path('', views.redireccion_por_rol, name='inicio'),
    path('docente/dashboard/', views.dashboard_docente, name='dashboard_docente'),
    path('docente/horario/', views.mi_horario, name='mi_horario'),
    path('docente/disponibilidad/', views.mi_disponibilidad, name='mi_disponibilidad'),
    # NUEVA RUTA PARA ADMINISTRADORES
    path('admin/disponibilidades/', views.admin_ver_disponibilidades, name='admin_ver_disponibilidades'),
]