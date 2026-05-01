from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('envios', '0002_alter_encomienda_costo'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS envios_empleado (
                    id bigserial PRIMARY KEY,
                    nombres varchar(100) NOT NULL,
                    apellidos varchar(100) NOT NULL,
                    email varchar(254) NOT NULL UNIQUE,
                    estado integer NOT NULL
                );
                CREATE TABLE IF NOT EXISTS envios_historialestado (
                    id bigserial PRIMARY KEY,
                    encomienda_id bigint NOT NULL REFERENCES envios_encomienda(id) ON DELETE CASCADE,
                    estado_anterior varchar(2) NOT NULL,
                    estado_nuevo varchar(2) NOT NULL,
                    fecha timestamp with time zone NOT NULL
                );
            """,
            reverse_sql="""
                DROP TABLE IF EXISTS envios_historialestado CASCADE;
                DROP TABLE IF EXISTS envios_empleado CASCADE;
            """,
        ),
    ]
