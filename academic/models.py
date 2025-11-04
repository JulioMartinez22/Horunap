from django.db import models

class Curso(models.Model):
    TIPO_CURSO = [
        ('OBLIGATORIO', 'Obligatorio'),
        ('ELECTIVO', 'Electivo'),
        ('OPTATIVO', 'Optativo'),
    ]
    
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Curso")
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código del Curso")
    creditos = models.IntegerField(verbose_name="Número de Créditos")
    tipo = models.CharField(max_length=20, choices=TIPO_CURSO, default='OBLIGATORIO')
    sesiones_semana = models.IntegerField(default=1, verbose_name="Sesiones por Semana")
    duracion_sesion = models.IntegerField(default=2, verbose_name="Duración de Sesión (horas)")
    requisitos = models.ManyToManyField('self', symmetrical=False, blank=True, verbose_name="Prerrequisitos")
    capacidad_estimada = models.IntegerField(default=30, verbose_name="Capacidad Estimada de Estudiantes")
    equipamiento_requerido = models.TextField(blank=True, verbose_name="Equipamiento Requerido")
    activo = models.BooleanField(default=True, verbose_name="Curso Activo")
    
    # NUEVO CAMPO AGREGADO PARA COMPATIBILIDAD CON EL ALGORITMO
    requiere_laboratorio = models.BooleanField(default=False, verbose_name="Requiere Laboratorio")
    
    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
        ordering = ['codigo']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    # MÉTODO PARA DETERMINAR SI REQUIERE LABORATORIO BASADO EN EQUIPAMIENTO
    def save(self, *args, **kwargs):
        # Si no se ha especificado requiere_laboratorio, determinarlo automáticamente
        if not self.requiere_laboratorio and self.equipamiento_requerido:
            equipamiento_lower = self.equipamiento_requerido.lower()
            if any(term in equipamiento_lower for term in ['laboratorio', 'lab', 'computadora', 'software', 'equipo']):
                self.requiere_laboratorio = True
        super().save(*args, **kwargs)

class Aula(models.Model):
    TIPO_AULA = [
        ('TEORIA', 'Aula de Teoría'),
        ('LABORATORIO', 'Laboratorio'),
        ('MIXTA', 'Aula Mixta'),
    ]
    
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Aula")
    capacidad = models.IntegerField(verbose_name="Capacidad Máxima")
    tipo = models.CharField(max_length=20, choices=TIPO_AULA, default='TEORIA')
    edificio = models.CharField(max_length=50, blank=True, verbose_name="Edificio")
    piso = models.CharField(max_length=10, blank=True, verbose_name="Piso")
    tiene_proyector = models.BooleanField(default=False, verbose_name="Tiene Proyector")
    tiene_computadoras = models.BooleanField(default=False, verbose_name="Tiene Computadoras")
    tiene_pizarra_digital = models.BooleanField(default=False, verbose_name="Tiene Pizarra Digital")
    equipamiento_adicional = models.TextField(blank=True, verbose_name="Equipamiento Adicional")
    activa = models.BooleanField(default=True, verbose_name="Aula Activa")
    
    class Meta:
        verbose_name = "Aula"
        verbose_name_plural = "Aulas"
        ordering = ['edificio', 'piso', 'nombre']
    
    def __str__(self):
        ubicacion = f"{self.edificio} - " if self.edificio else ""
        return f"{ubicacion}{self.nombre} (Cap: {self.capacidad})"
    
    def get_equipamiento(self):
        equipos = []
        if self.tiene_proyector:
            equipos.append("Proyector")
        if self.tiene_computadoras:
            equipos.append("Computadoras")
        if self.tiene_pizarra_digital:
            equipos.append("Pizarra Digital")
        if self.equipamiento_adicional:
            equipos.append(self.equipamiento_adicional)
        return ", ".join(equipos) if equipos else "Equipamiento básico"
    
    # PROPIEDADES DE COMPATIBILIDAD PARA EL ALGORITMO
    @property
    def tipo_aula(self):
        """Compatibilidad con el algoritmo - mapea tipo a los valores esperados"""
        mapping = {
            'TEORIA': 'NORMAL',
            'LABORATORIO': 'LABORATORIO', 
            'MIXTA': 'NORMAL'
        }
        return mapping.get(self.tipo, 'NORMAL')
    
    @property
    def es_laboratorio(self):
        """Compatibilidad con el algoritmo"""
        return self.tipo == 'LABORATORIO'