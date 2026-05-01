from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import migrations


def create_default_user(apps, schema_editor):
    username = 'Andre'
    password = 'Humberto1234'
    if not User.objects.filter(username=username).exists():
        User.objects.create(
            username=username,
            password=make_password(password),
            is_staff=True,
            is_superuser=False,
        )


def delete_default_user(apps, schema_editor):
    User.objects.filter(username='Andre').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('envios', '0004_alter_empleado_apellidos_alter_empleado_nombres'),
    ]

    operations = [
        migrations.RunPython(create_default_user, delete_default_user),
    ]
