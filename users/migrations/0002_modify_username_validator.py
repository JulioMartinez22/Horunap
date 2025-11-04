# users/migrations/0002_modify_username_validator.py
from django.db import migrations
from django.core.validators import RegexValidator

def modify_username_validator(apps, schema_editor):
    User = apps.get_model('users', 'User')
    
    # Actualizar el validador del campo username
    for field in User._meta.fields:
        if field.name == 'username':
            field.validators = [
                RegexValidator(
                    regex=r'^[\w\sñÑáéíóúÁÉÍÓÚüÜ.,@+-]+$',
                    message='El nombre de usuario puede contener letras, números, espacios y caracteres especiales'
                )
            ]
            break

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(modify_username_validator),
    ]