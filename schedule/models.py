from django.db import models
from django.conf import settings
from academic.models import Curso, Aula

class Horario(models.Model):
    DIA_SEMANA = [
        ('LUNES', 'Lunes'),
        ('MARTES', 'Martes'),
        ('MIERCOLES', 'Miércoles'),
        ('JUEVES', 'Jueves'),
        ('VIERNES', 'Viernes'),
        ('SABADO', 'Sábado'),
    ]

    BLOQUES_HORARIOS = [
        ('08:00-10:00', '08:00 - 10:00'),
        ('10:00-12:00', '10:00 - 12:00'),
        ('12:00-14:00', '12:00 - 14:00'),
        ('14:00-16:00', '14:00 - 16:00'),
        ('16:00-18:00', '16:00 - 18:00'),
        ('18:00-20:00', '18:00 - 20:00'),
    ]

    ESTADO_HORARIO = [
        ('BORRADOR', 'Borrador'),
        ('GENERADO', 'Generado'),
        ('APROBADO', 'Aprobado'),
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
    ]

    nombre = models.CharField(max_length=100, verbose_name="Nombre del Horario")
    semestre = models.CharField(max_length=20, verbose_name="Semestre Académico")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    estado = models.CharField(max_length=20, choices=ESTADO_HORARIO, default='BORRADOR')
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Creado por"
    )

    class Meta:
        verbose_name = "Horario"
        verbose_name_plural = "Horarios"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre} - {self.semestre} ({self.estado})"

class Asignacion(models.Model):
    horario = models.ForeignKey(Horario, on_delete=models.CASCADE, related_name='asignaciones')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, verbose_name="Curso")
    docente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'DOCENTE'},
        verbose_name="Docente"
    )
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE, verbose_name="Aula")
    dia_semana = models.CharField(max_length=20, choices=Horario.DIA_SEMANA, verbose_name="Día de la Semana")
    bloque_horario = models.CharField(max_length=20, choices=Horario.BLOQUES_HORARIOS, verbose_name="Bloque Horario")
    fecha_asignacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Asignación")
    activa = models.BooleanField(default=True, verbose_name="Asignación Activa")

    class Meta:
        verbose_name = "Asignación"
        verbose_name_plural = "Asignaciones"
        ordering = ['dia_semana', 'bloque_horario']
        unique_together = [
            ['horario', 'docente', 'dia_semana', 'bloque_horario'],
            ['horario', 'aula', 'dia_semana', 'bloque_horario'],
            ['horario', 'curso', 'dia_semana', 'bloque_horario'],
        ]

    def __str__(self):
        return f"{self.curso.codigo} - {self.docente.username} - {self.dia_semana} {self.bloque_horario}"

class ConflictoHorario(models.Model):
    TIPO_CONFLICTO = [
        ('DOCENTE', 'Conflicto de Docente'),
        ('AULA', 'Conflicto de Aula'),
        ('CURSO', 'Conflicto de Curso'),
        ('CAPACIDAD', 'Conflicto de Capacidad'),
        ('EQUIPAMIENTO', 'Conflicto de Equipamiento'),
    ]

    horario = models.ForeignKey(Horario, on_delete=models.CASCADE, related_name='conflictos')
    asignacion = models.ForeignKey(Asignacion, on_delete=models.CASCADE, verbose_name="Asignación Conflictiva")
    tipo_conflicto = models.CharField(max_length=20, choices=TIPO_CONFLICTO, verbose_name="Tipo de Conflicto")
    descripcion = models.TextField(verbose_name="Descripción del Conflicto")
    fecha_deteccion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Detección")
    resuelto = models.BooleanField(default=False, verbose_name="Conflicto Resuelto")
    fecha_resolucion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Resolución")

    class Meta:
        verbose_name = "Conflicto de Horario"
        verbose_name_plural = "Conflictos de Horario"
        ordering = ['-fecha_deteccion']

    def __str__(self):
        return f"Conflicto {self.tipo_conflicto} - {self.asignacion.curso.codigo}"

# NUEVO MODELO AGREGADO
class DisponibilidadDocente(models.Model):
    """
    Modelo para gestionar la disponibilidad horaria de los docentes
    """
    docente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'DOCENTE'},
        verbose_name="Docente"
    )
    dia_semana = models.CharField(max_length=20, choices=Horario.DIA_SEMANA, verbose_name="Día de la Semana")
    bloque_horario = models.CharField(max_length=20, choices=Horario.BLOQUES_HORARIOS, verbose_name="Bloque Horario")
    disponible = models.BooleanField(default=True, verbose_name="Disponible")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

    class Meta:
        verbose_name = "Disponibilidad de Docente"
        verbose_name_plural = "Disponibilidades de Docentes"
        ordering = ['docente', 'dia_semana', 'bloque_horario']
        unique_together = ['docente', 'dia_semana', 'bloque_horario']

    def __str__(self):
        estado = "Disponible" if self.disponible else "No Disponible"
        return f"{self.docente.username} - {self.dia_semana} {self.bloque_horario} ({estado})"
    

# NUEVO MODELO PARA HORARIOS PERSONALIZADOS
class HorarioPersonalizadoDocente(models.Model):
    """
    Modelo para que los docentes ingresen sus horarios libres personalizados
    """
    TIPO_HORARIO = [
        ('DISPONIBLE', '✅ Horario Disponible'),
        ('NO_DISPONIBLE', '🚫 Horario No Disponible'),
    ]

    docente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'DOCENTE'},
        verbose_name="Docente"
    )
    dia_semana = models.CharField(max_length=20, choices=Horario.DIA_SEMANA, verbose_name="Día de la Semana")
    hora_inicio = models.TimeField(verbose_name="Hora de Inicio")
    hora_fin = models.TimeField(verbose_name="Hora de Fin")
    tipo = models.CharField(
        max_length=20, 
        choices=TIPO_HORARIO, 
        default='DISPONIBLE', 
        verbose_name="Tipo de Horario"
    )
    descripcion = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name="Descripción (opcional)",
        help_text="Ej: Reunión de departamento, Investigación, etc."
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

    class Meta:
        verbose_name = "Horario Personalizado de Docente"
        verbose_name_plural = "Horarios Personalizados de Docentes"
        ordering = ['docente', 'dia_semana', 'hora_inicio']
        unique_together = ['docente', 'dia_semana', 'hora_inicio', 'hora_fin']

    def __str__(self):
        tipo_str = "Disponible" if self.tipo == 'DISPONIBLE' else "No Disponible"
        return f"{self.docente.username} - {self.dia_semana} {self.hora_inicio}-{self.hora_fin} ({tipo_str})"
    
    @property
    def horario_completo(self):
        return f"{self.hora_inicio.strftime('%H:%M')} - {self.hora_fin.strftime('%H:%M')}"
    
    def duracion_horas(self):
        """Calcula la duración en horas del horario"""
        from datetime import datetime
        inicio = datetime.combine(datetime.today(), self.hora_inicio)
        fin = datetime.combine(datetime.today(), self.hora_fin)
        diferencia = fin - inicio
        return diferencia.total_seconds() / 3600  # Convertir a horas