from django.db import migrations


def make_default_user_superuser(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    username = 'Andre'
    password = 'Humberto1234'

    user, created = User.objects.get_or_create(username=username)
    if created:
        user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.save()


def revert_default_user_superuser(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    username = 'Andre'
    try:
        user = User.objects.get(username=username)
        user.is_staff = True
        user.is_superuser = False
        user.save()
    except User.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('envios', '0005_create_default_user'),
    ]

    operations = [
        migrations.RunPython(make_default_user_superuser, revert_default_user_superuser),
    ]
