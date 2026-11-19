from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('oficios', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='oficios',
            constraint=models.UniqueConstraint(
                fields=('ano', 'numero_sequencial'),
                name='oficio_numero_unico_por_ano',
            ),
        ),
    ]
