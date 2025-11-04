from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Horario, Asignacion, ConflictoHorario
from academic.models import Curso, Aula

User = get_user_model()

class HorarioModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='admin',
            password='password123',
            rol='ADMIN'
        )
        self.horario = Horario.objects.create(
            nombre="Horario 2025-I",
            semestre="2025-I",
            creado_por=self.user
        )
    
    def test_horario_creation(self):
        self.assertEqual(self.horario.nombre, "Horario 2025-I")
        self.assertEqual(self.horario.semestre, "2025-I")
        self.assertEqual(self.horario.estado, "BORRADOR")

class AsignacionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='docente_test',
            password='password123',
            rol='DOCENTE'
        )
        self.horario = Horario.objects.create(
            nombre="Test Horario",
            semestre="2025-I",
            creado_por=self.user
        )
        self.curso = Curso.objects.create(
            nombre="Curso Test",
            codigo="TEST-001",
            creditos=3
        )
        self.aula = Aula.objects.create(
            nombre="Aula Test",
            capacidad=40
        )
        self.asignacion = Asignacion.objects.create(
            horario=self.horario,
            curso=self.curso,
            docente=self.user,
            aula=self.aula,
            dia_semana="LUNES",
            bloque_horario="08:00-10:00"
        )
    
    def test_asignacion_creation(self):
        self.assertEqual(self.asignacion.curso, self.curso)
        self.assertEqual(self.asignacion.docente, self.user)
        self.assertEqual(self.asignacion.dia_semana, "LUNES")
        self.assertTrue(self.asignacion.activa)

class HorarioAPITest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            password='password123',
            rol='ADMIN'
        )
        self.client.force_authenticate(user=self.admin_user)
        
        self.horario_data = {
            'nombre': 'Horario Test API',
            'semestre': '2025-I'
        }
    
    def test_create_horario(self):
        url = reverse('horario-list')
        response = self.client.post(url, self.horario_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nombre'], 'Horario Test API')
        self.assertEqual(response.data['estado'], 'BORRADOR')
    
    def test_list_horarios(self):
        Horario.objects.create(
            nombre="Horario 1",
            semestre="2025-I",
            creado_por=self.admin_user
        )
        
        url = reverse('horario-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

class AsignacionAPITest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            password='password123',
            rol='ADMIN'
        )
        self.docente_user = User.objects.create_user(
            username='docente',
            password='password123',
            rol='DOCENTE'
        )
        self.client.force_authenticate(user=self.admin_user)
        
        self.horario = Horario.objects.create(
            nombre="Test Horario",
            semestre="2025-I",
            creado_por=self.admin_user
        )
        self.curso = Curso.objects.create(
            nombre="Curso Test",
            codigo="TEST-001",
            creditos=3
        )
        self.aula = Aula.objects.create(
            nombre="Aula Test",
            capacidad=40
        )
    
    def test_create_asignacion(self):
        url = reverse('asignacion-list')
        data = {
            'horario': self.horario.id,
            'curso': self.curso.id,
            'docente': self.docente_user.id,
            'aula': self.aula.id,
            'dia_semana': 'LUNES',
            'bloque_horario': '08:00-10:00'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class AlgorithmTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            password='password123',
            rol='ADMIN'
        )
        self.horario = Horario.objects.create(
            nombre="Test Algorithm",
            semestre="2025-I",
            creado_por=self.admin_user
        )
        
        # Crear datos de prueba para el algoritmo
        self.curso1 = Curso.objects.create(
            nombre="Curso 1",
            codigo="C1",
            creditos=4,
            sesiones_semana=2,
            capacidad_estimada=30
        )
        self.curso2 = Curso.objects.create(
            nombre="Curso 2",
            codigo="C2",
            creditos=3,
            sesiones_semana=1,
            capacidad_estimada=25
        )
        
        self.aula1 = Aula.objects.create(
            nombre="Aula 1",
            capacidad=35
        )
        self.aula2 = Aula.objects.create(
            nombre="Aula 2",
            capacidad=30
        )
        
        self.docente1 = User.objects.create_user(
            username='docente1',
            password='password123',
            rol='DOCENTE'
        )
        self.docente2 = User.objects.create_user(
            username='docente2',
            password='password123',
            rol='DOCENTE'
        )
    
    def test_generador_horarios(self):
        from .core.algorithm import GeneradorHorarios
        
        generador = GeneradorHorarios(self.horario.id)
        asignaciones_creadas = generador.generar_horario()
        
        self.assertGreater(asignaciones_creadas, 0)
        self.assertEqual(self.horario.asignaciones.count(), asignaciones_creadas)
        
        # Verificar que se detectaron conflictos
        generador.detectar_conflictos()
        self.assertGreaterEqual(self.horario.conflictos.count(), 0)