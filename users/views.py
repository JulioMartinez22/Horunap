from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from schedule.models import Asignacion, DisponibilidadDocente, Horario
from academic.models import Curso
import datetime

def redireccion_por_rol(request):
    """
    Vista de redirección inteligente basada en el rol del usuario.
    """
    if not request.user.is_authenticated:
        return redirect('admin:login')

    # Redirección basada en rol y permisos
    if request.user.is_superuser or request.user.rol == 'ADMIN':
        # Administradores van al admin de Django
        return HttpResponseRedirect(reverse('admin:index'))
    elif request.user.rol == 'DOCENTE':
        # Docentes van a su panel personalizado
        return redirect('dashboard_docente')
    else:
        # Por defecto, ir al admin
        return HttpResponseRedirect(reverse('admin:index'))

@login_required
def dashboard_docente(request):
    """Panel principal EXCLUSIVO para docentes"""
    # Validación estricta - SOLO docentes pueden acceder
    if request.user.rol != 'DOCENTE':
        messages.warning(request, 'No tienes permisos para acceder al panel docente')
        return HttpResponseRedirect(reverse('admin:index'))

    # Obtener datos del docente
    hoy = datetime.date.today()
    asignaciones = Asignacion.objects.filter(docente=request.user, activa=True)
    disponibilidades = DisponibilidadDocente.objects.filter(docente=request.user)
    cursos = Curso.objects.filter(asignacion__docente=request.user).distinct()

    # Organizar asignaciones por día
    dias_semana = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO']
    horario_por_dia = {}

    for dia in dias_semana:
        horario_por_dia[dia] = asignaciones.filter(dia_semana=dia).order_by('bloque_horario')

    context = {
        'asignaciones': asignaciones,
        'disponibilidades': disponibilidades,
        'cursos': cursos,
        'horario_por_dia': horario_por_dia,
        'dias_semana': dias_semana,
        'hoy': hoy,
        'es_docente': True
    }
    return render(request, 'docente/dashboard.html', context)

@login_required
def mi_horario(request):
    """Vista detallada del horario del docente - SOLO para docentes"""
    if request.user.rol != 'DOCENTE':
        return HttpResponseForbidden("No tienes permisos para acceder a esta página")

    asignaciones = Asignacion.objects.filter(docente=request.user, activa=True)
    
    # Definir días y bloques horarios
    dias_semana = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO']
    bloques_horarios = ['08:00-10:00', '10:00-12:00', '12:00-14:00', 
                       '14:00-16:00', '16:00-18:00', '18:00-20:00']
    
    # Crear estructura de horario sin filtros complejos
    horario_estructura = []
    for dia in dias_semana:
        dia_data = {
            'nombre': dia,
            'bloques': []
        }
        for bloque in bloques_horarios:
            asignacion = asignaciones.filter(dia_semana=dia, bloque_horario=bloque).first()
            dia_data['bloques'].append({
                'horario': bloque,
                'asignacion': asignacion
            })
        horario_estructura.append(dia_data)

    context = {
        'horario_estructura': horario_estructura,
        'dias_semana': dias_semana,
        'bloques_horarios': bloques_horarios,
        'asignaciones': asignaciones,
        'es_docente': True
    }
    return render(request, 'docente/mi_horario.html', context)

@login_required
def mi_disponibilidad(request):
    """Vista para gestionar horarios personalizados del docente"""
    if request.user.rol != 'DOCENTE':
        return HttpResponseForbidden("No tienes permisos para acceder a esta página")

    # Obtener los horarios personalizados existentes del docente
    from schedule.models import HorarioPersonalizadoDocente
    horarios_personalizados = HorarioPersonalizadoDocente.objects.filter(
        docente=request.user
    ).order_by('dia_semana', 'hora_inicio')

    # Calcular estadísticas directamente en la vista
    total_horarios = horarios_personalizados.count()
    horarios_disponibles = horarios_personalizados.filter(tipo='DISPONIBLE').count()
    horarios_no_disponibles = horarios_personalizados.filter(tipo='NO_DISPONIBLE').count()

    if request.method == 'POST':
        try:
            # Procesar eliminación
            if 'eliminar_id' in request.POST:
                horario_id = request.POST.get('eliminar_id')
                horario = HorarioPersonalizadoDocente.objects.get(id=horario_id, docente=request.user)
                horario.delete()
                messages.success(request, '✅ Horario eliminado correctamente')
                return redirect('mi_disponibilidad')
            
            # Procesar nuevo horario
            dia_semana = request.POST.get('dia_semana')
            hora_inicio = request.POST.get('hora_inicio')
            hora_fin = request.POST.get('hora_fin')
            tipo = request.POST.get('tipo')
            descripcion = request.POST.get('descripcion', '')

            # Validaciones básicas
            if not all([dia_semana, hora_inicio, hora_fin, tipo]):
                messages.error(request, '❌ Todos los campos son obligatorios')
                return redirect('mi_disponibilidad')

            if hora_inicio >= hora_fin:
                messages.error(request, '❌ La hora de inicio debe ser anterior a la hora de fin')
                return redirect('mi_disponibilidad')

            # Verificar si ya existe un horario similar
            horario_existente = HorarioPersonalizadoDocente.objects.filter(
                docente=request.user,
                dia_semana=dia_semana,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin
            ).exists()
            
            if horario_existente:
                messages.warning(request, '⚠️ Ya existe un horario con estas características')
                return redirect('mi_disponibilidad')

            # Crear nuevo horario personalizado
            HorarioPersonalizadoDocente.objects.create(
                docente=request.user,
                dia_semana=dia_semana,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                tipo=tipo,
                descripcion=descripcion
            )

            messages.success(request, '✅ Horario agregado correctamente')
            return redirect('mi_disponibilidad')
            
        except Exception as e:
            messages.error(request, f'❌ Error al procesar la solicitud: {str(e)}')

    # Días de la semana para el formulario
    dias_semana = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO']

    context = {
        'horarios_personalizados': horarios_personalizados,
        'dias_semana': dias_semana,
        'total_horarios': total_horarios,
        'horarios_disponibles': horarios_disponibles,
        'horarios_no_disponibles': horarios_no_disponibles,
        'es_docente': True
    }
    return render(request, 'docente/mi_disponibilidad.html', context)

@login_required
def admin_ver_disponibilidades(request):
    """Vista para que los administradores vean todas las disponibilidades de docentes"""
    if not (request.user.is_superuser or request.user.rol == 'ADMIN'):
        return HttpResponseForbidden("No tienes permisos para acceder a esta página")

    from schedule.models import HorarioPersonalizadoDocente
    from django.db.models import Count
    
    # Obtener todos los horarios personalizados de todos los docentes
    horarios_todos = HorarioPersonalizadoDocente.objects.all().order_by('docente', 'dia_semana', 'hora_inicio')
    
    # Estadísticas generales
    total_horarios = horarios_todos.count()
    horarios_disponibles = horarios_todos.filter(tipo='DISPONIBLE').count()
    horarios_no_disponibles = horarios_todos.filter(tipo='NO_DISPONIBLE').count()
    
    # Estadísticas por docente
    estadisticas_docentes = HorarioPersonalizadoDocente.objects.values(
        'docente__username', 
        'docente__first_name', 
        'docente__last_name'
    ).annotate(
        total=Count('id'),
        disponibles=Count('id', filter=models.Q(tipo='DISPONIBLE')),
        no_disponibles=Count('id', filter=models.Q(tipo='NO_DISPONIBLE'))
    ).order_by('docente__username')

    # Filtrar por docente si se especifica
    docente_id = request.GET.get('docente')
    if docente_id:
        horarios_todos = horarios_todos.filter(docente_id=docente_id)

    context = {
        'horarios_todos': horarios_todos,
        'estadisticas_docentes': estadisticas_docentes,
        'total_horarios': total_horarios,
        'horarios_disponibles': horarios_disponibles,
        'horarios_no_disponibles': horarios_no_disponibles,
        'es_admin': True
    }
    return render(request, 'admin/ver_disponibilidades.html', context)