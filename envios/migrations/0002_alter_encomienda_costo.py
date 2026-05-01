from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('envios', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='encomienda',
            name='costo',
            field=models.DecimalField(blank=True, max_digits=10, decimal_places=2, null=True),
        ),
    ]
