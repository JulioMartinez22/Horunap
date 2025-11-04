from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Curso, Aula

class CursoModelTest(TestCase):
    def setUp(self):
        self.curso = Curso.objects.create(
            nombre="Base de Datos II",
            codigo="BD2-2024",
            creditos=4,
            sesiones_semana=2,
            capacidad_estimada=40
        )
    
    def test_curso_creation(self):
        self.assertEqual(self.curso.nombre, "Base de Datos II")
        self.assertEqual(self.curso.codigo, "BD2-2024")
        self.assertTrue(self.curso.activo)

class AulaModelTest(TestCase):
    def setUp(self):
        self.aula = Aula.objects.create(
            nombre="A-101",
            capacidad=50,
            edificio="Edificio A",
            tiene_proyector=True
        )
    
    def test_aula_creation(self):
        self.assertEqual(self.aula.nombre, "A-101")
        self.assertEqual(self.aula.capacidad, 50)
        self.assertTrue(self.aula.tiene_proyector)

class CursoAPITest(APITestCase):
    def setUp(self):
        self.curso_data = {
            'nombre': 'Gerencia de Sistemas',
            'codigo': 'GS-2024',
            'creditos': 3,
            'sesiones_semana': 1,
            'capacidad_estimada': 35
        }
        self.curso = Curso.objects.create(**self.curso_data)
    
    def test_list_cursos(self):
        url = reverse('curso-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_curso(self):
        url = reverse('curso-list')
        new_curso = {
            'nombre': 'Inteligencia Artificial',
            'codigo': 'IA-2024',
            'creditos': 4,
            'sesiones_semana': 2,
            'capacidad_estimada': 30
        }
        response = self.client.post(url, new_curso, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class AulaAPITest(APITestCase):
    def setUp(self):
        self.aula_data = {
            'nombre': 'Lab-201',
            'capacidad': 25,
            'tipo': 'LABORATORIO',
            'tiene_computadoras': True
        }
        self.aula = Aula.objects.create(**self.aula_data)
    
    def test_list_aulas(self):
        url = reverse('aula-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_aulas_by_capacity(self):
        url = reverse('aula-list') + '?capacidad_min=20'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)