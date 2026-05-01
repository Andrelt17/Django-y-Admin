from django.db import migrations


def rename_table_forward(apps, schema_editor):
    cursor = schema_editor.connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clientes_cliente'")
    if cursor.fetchone():
        cursor.execute("ALTER TABLE clientes_cliente RENAME TO clientes")


def rename_table_backward(apps, schema_editor):
    cursor = schema_editor.connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clientes'")
    if cursor.fetchone():
        cursor.execute("ALTER TABLE clientes RENAME TO clientes_cliente")


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(rename_table_forward, rename_table_backward),
    ]
