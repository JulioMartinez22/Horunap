# schedule/core/algorithm.py
import random
from datetime import datetime
from django.db.models import Q
from academic.models import Curso, Aula
from users.models import User
from ..models import Horario, Asignacion, ConflictoHorario, DisponibilidadDocente

class GeneradorHorarios:
    """
    Motor inteligente para la generación automática de horarios
    """

    def __init__(self, horario_id):
        self.horario = Horario.objects.get(id=horario_id)
        self.conflictos = []

    def generar_horario(self):
        """
        Genera un horario completo basado en restricciones y disponibilidades
        """
        print(f"Iniciando generación de horario: {self.horario.nombre}")

        # Limpiar asignaciones previas
        Asignacion.objects.filter(horario=self.horario).delete()
        ConflictoHorario.objects.filter(horario=self.horario).delete()

        # Obtener datos necesarios
        cursos = Curso.objects.filter(activo=True)
        aulas = Aula.objects.filter(activa=True)
        docentes = User.objects.filter(rol='DOCENTE', is_active=True)

        # Parámetros de configuración
        dias_semana = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES']
        bloques_horarios = ['08:00-10:00', '10:00-12:00', '14:00-16:00', '16:00-18:00']

        asignaciones_generadas = 0
        max_intentos = 1000

        for curso in cursos:
            for sesion in range(curso.sesiones_semana):
                intentos = 0
                asignado = False

                while not asignado and intentos < max_intentos:
                    # Seleccionar aleatoriamente día y bloque
                    dia = random.choice(dias_semana)
                    bloque = random.choice(bloques_horarios)

                    # Seleccionar docente disponible (MEJORADO)
                    docente = self._seleccionar_docente_disponible(docentes, dia, bloque, curso)

                    # Seleccionar aula disponible
                    aula = self._seleccionar_aula_disponible(aulas, dia, bloque, curso)

                    if docente and aula:
                        # Verificar si no hay conflictos
                        if not self._tiene_conflictos(curso, docente, aula, dia, bloque):
                            # Crear asignación
                            asignacion = Asignacion.objects.create(
                                horario=self.horario,
                                curso=curso,
                                docente=docente,
                                aula=aula,
                                dia_semana=dia,
                                bloque_horario=bloque
                            )
                            asignaciones_generadas += 1
                            asignado = True
                            print(f"Asignación creada: {curso.codigo} - {dia} {bloque}")

                    intentos += 1

                if not asignado:
                    print(f"⚠️ No se pudo asignar sesión {sesion + 1} del curso {curso.codigo}")

        # Actualizar estado del horario
        self.horario.estado = 'GENERADO'
        self.horario.save()

        print(f"✅ Generación completada. {asignaciones_generadas} asignaciones creadas.")
        return asignaciones_generadas

    def _seleccionar_docente_disponible(self, docentes, dia, bloque, curso):
        """
        MEJORADO: Selecciona un docente disponible considerando disponibilidad registrada
        """
        docentes_disponibles = []
        for docente in docentes:
            # Verificar disponibilidad registrada (NUEVA LÓGICA)
            if self._docente_tiene_disponibilidad(docente, dia, bloque):
                if not self._docente_ocupado(docente, dia, bloque):
                    docentes_disponibles.append(docente)

        return random.choice(docentes_disponibles) if docentes_disponibles else None

    def _docente_tiene_disponibilidad(self, docente, dia, bloque):
        """
        MEJORADO: Verifica si el docente tiene disponibilidad en horarios personalizados
        """
        try:
            from ..models import HorarioPersonalizadoDocente
            
            # Convertir bloque a horas (ej: "08:00-10:00" -> "08:00" y "10:00")
            hora_inicio_bloque, hora_fin_bloque = bloque.split('-')
            
            # Buscar horarios disponibles que se superpongan con el bloque
            horarios_disponibles = HorarioPersonalizadoDocente.objects.filter(
                docente=docente,
                dia_semana=dia,
                tipo='DISPONIBLE'
            )
            
            for horario in horarios_disponibles:
                horario_inicio_str = horario.hora_inicio.strftime('%H:%M')
                horario_fin_str = horario.hora_fin.strftime('%H:%M')
                
                # Verificar si el bloque está dentro del horario disponible
                if (horario_inicio_str <= hora_inicio_bloque and 
                    horario_fin_str >= hora_fin_bloque):
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error verificando disponibilidad personalizada: {e}")
            return False

    def _seleccionar_aula_disponible(self, aulas, dia, bloque, curso):
        """
        MEJORADO: Selecciona un aula disponible que cumpla con los requisitos del curso
        """
        aulas_disponibles = []
        for aula in aulas:
            if (aula.capacidad >= curso.capacidad_estimada and
                not self._aula_ocupada(aula, dia, bloque) and
                self._aula_cumple_requisitos(aula, curso)):
                aulas_disponibles.append(aula)

        # Priorizar aulas con capacidad similar a la requerida
        if aulas_disponibles:
            aulas_disponibles.sort(key=lambda a: abs(a.capacidad - curso.capacidad_estimada))
            return aulas_disponibles[0]

        return None

    def _aula_cumple_requisitos(self, aula, curso):
        """
        NUEVO MÉTODO: Verifica si el aula cumple con los requisitos del curso
        """
        # Verificar requisito de laboratorio
        if curso.requiere_laboratorio and aula.tipo_aula != 'LABORATORIO':
            return False
            
        # Verificar equipamiento adicional si es necesario
        if curso.requiere_laboratorio and not aula.tiene_proyector:
            return False
            
        return True

    def _docente_ocupado(self, docente, dia, bloque):
        """
        Verifica si el docente ya tiene una asignación en el mismo día y bloque
        """
        return Asignacion.objects.filter(
            horario=self.horario,
            docente=docente,
            dia_semana=dia,
            bloque_horario=bloque
        ).exists()

    def _aula_ocupada(self, aula, dia, bloque):
        """
        Verifica si el aula ya está ocupada en el mismo día y bloque
        """
        return Asignacion.objects.filter(
            horario=self.horario,
            aula=aula,
            dia_semana=dia,
            bloque_horario=bloque
        ).exists()

    def _tiene_conflictos(self, curso, docente, aula, dia, bloque):
        """
        MEJORADO: Verifica si existe algún conflicto con la asignación propuesta
        """
        # Verificar conflicto de docente
        if self._docente_ocupado(docente, dia, bloque):
            return True

        # Verificar conflicto de aula
        if self._aula_ocupada(aula, dia, bloque):
            return True

        # Verificar capacidad del aula
        if aula.capacidad < curso.capacidad_estimada:
            return True

        # Verificar requisitos de equipamiento (NUEVA VALIDACIÓN)
        if not self._aula_cumple_requisitos(aula, curso):
            return True

        return False

    def detectar_conflictos(self):
        """
        MEJORADO: Detecta y registra conflictos en el horario generado
        """
        print("🔍 Detectando conflictos...")

        asignaciones = Asignacion.objects.filter(horario=self.horario)

        for asignacion in asignaciones:
            # Verificar conflictos de capacidad
            if asignacion.aula.capacidad < asignacion.curso.capacidad_estimada:
                self._registrar_conflicto(
                    asignacion,
                    'CAPACIDAD',
                    f"El aula {asignacion.aula.nombre} tiene capacidad {asignacion.aula.capacidad} "
                    f"pero el curso requiere {asignacion.curso.capacidad_estimada} estudiantes"
                )

            # Verificar conflictos de equipamiento (NUEVA DETECCIÓN)
            if asignacion.curso.requiere_laboratorio and asignacion.aula.tipo_aula != 'LABORATORIO':
                self._registrar_conflicto(
                    asignacion,
                    'EQUIPAMIENTO',
                    f"El curso {asignacion.curso.codigo} requiere laboratorio "
                    f"pero el aula {asignacion.aula.nombre} no es un laboratorio"
                )

        print(f"✅ Detección de conflictos completada. {len(self.conflictos)} conflictos encontrados.")

    def _registrar_conflicto(self, asignacion, tipo, descripcion):
        """
        Registra un conflicto en la base de datos
        """
        conflicto = ConflictoHorario.objects.create(
            horario=self.horario,
            asignacion=asignacion,
            tipo_conflicto=tipo,
            descripcion=descripcion
        )
        self.conflictos.append(conflicto)

class ResolvedorConflictos:
    """
    Módulo para la resolución automática de conflictos
    """

    def __init__(self, horario_id):
        self.horario = Horario.objects.get(id=horario_id)

    def resolver_conflictos(self):
        """
        Intenta resolver automáticamente los conflictos detectados
        """
        conflictos = ConflictoHorario.objects.filter(
            horario=self.horario,
            resuelto=False
        )

        for conflicto in conflictos:
            if self._resolver_conflicto(conflicto):
                conflicto.resuelto = True
                conflicto.fecha_resolucion = datetime.now()
                conflicto.save()

        return conflictos.filter(resuelto=True).count()

    def _resolver_conflicto(self, conflicto):
        """
        Intenta resolver un conflicto específico
        """
        if conflicto.tipo_conflicto == 'CAPACIDAD':
            return self._resolver_conflicto_capacidad(conflicto)
        elif conflicto.tipo_conflicto == 'EQUIPAMIENTO':
            return self._resolver_conflicto_equipamiento(conflicto)

        return False

    def _resolver_conflicto_capacidad(self, conflicto):
        """
        Resuelve conflictos de capacidad buscando un aula más grande
        """
        asignacion = conflicto.asignacion
        aulas_disponibles = Aula.objects.filter(
            activa=True,
            capacidad__gte=asignacion.curso.capacidad_estimada,
            tipo_aula=asignacion.aula.tipo_aula  # Mantener mismo tipo de aula
        ).exclude(id=asignacion.aula.id)

        for aula in aulas_disponibles:
            if not self._aula_ocupada_en_horario(aula, asignacion.dia_semana, asignacion.bloque_horario):
                # Reasignar el aula
                asignacion.aula = aula
                asignacion.save()
                return True

        return False

    def _resolver_conflicto_equipamiento(self, conflicto):
        """
        NUEVO MÉTODO: Resuelve conflictos de equipamiento
        """
        asignacion = conflicto.asignacion
        aulas_disponibles = Aula.objects.filter(
            activa=True,
            tipo_aula='LABORATORIO',
            capacidad__gte=asignacion.curso.capacidad_estimada
        ).exclude(id=asignacion.aula.id)

        for aula in aulas_disponibles:
            if not self._aula_ocupada_en_horario(aula, asignacion.dia_semana, asignacion.bloque_horario):
                # Reasignar el aula
                asignacion.aula = aula
                asignacion.save()
                return True

        return False

    def _aula_ocupada_en_horario(self, aula, dia, bloque):
        """
        Verifica si un aula está ocupada en un horario específico
        """
        return Asignacion.objects.filter(
            horario=self.horario,
            aula=aula,
            dia_semana=dia,
            bloque_horario=bloque
        ).exists()