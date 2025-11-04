from django.db import models
from django.contrib.auth.models import AbstractUser, Group # <-- 1. Importa Group
from django.core.validators import RegexValidator

class User(AbstractUser):
    ROL_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('DOCENTE', 'Docente'),
    ]
    
    # Validador personalizado que acepte espacios, ñ y caracteres especiales
    username_validator = RegexValidator(
        regex=r'^[\w\sñÑáéíóúÁÉÍÓÚüÜ.,@+-]+$',
        message='El nombre de usuario puede contener letras, números, espacios y caracteres especiales'
    )
    
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text='Requerido. 150 caracteres o menos. Letras, dígitos, espacios y @/./+/-/_ solamente.',
        validators=[username_validator],
        error_messages={
            'unique': "Ya existe un usuario con ese nombre.",
        },
    )
    
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='DOCENTE')
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"

    # --- INICIO DE LA OPTIMIZACIÓN ---
    # Este método se ejecutará automáticamente CADA VEZ que
    # un usuario se cree o se actualice (guarde).
    def save(self, *args, **kwargs):
        # Primero, guarda el objeto de usuario
        super().save(*args, **kwargs) 

        try:
            # 2. Asigna automáticamente al grupo correcto basado en el ROL
            # NOTA: Los nombres 'Administradores' y 'Docentes' deben
            # existir en tu panel de admin de Django.
            
            if self.rol == 'ADMIN':
                grupo_admin, _ = Group.objects.get_or_create(name='Administradores')
                grupo_docente = Group.objects.filter(name='Docentes').first()
                
                self.groups.add(grupo_admin)
                if grupo_docente:
                    self.groups.remove(grupo_docente)

            elif self.rol == 'DOCENTE':
                grupo_docente, _ = Group.objects.get_or_create(name='Docentes')
                grupo_admin = Group.objects.filter(name='Administradores').first()
                
                self.groups.add(grupo_docente)
                if grupo_admin:
                    self.groups.remove(grupo_admin)

        except Exception as e:
            # Es bueno dejar un print en caso de que algo falle,
            # como que los grupos no estén creados.
            print(f"Error al asignar grupo automático: {e}")
            pass
    # --- FIN DE LA OPTIMIZACIÓN ---