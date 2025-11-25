from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("salas", "0002_add_localizacao"),
    ]

    operations = [
        migrations.AddField(
            model_name="sala",
            name="equipamentos",
            field=models.JSONField(default=list, blank=True),
        ),
        migrations.AddField(
            model_name="sala",
            name="status",
            field=models.CharField(choices=[('Disponivel', 'Disponivel'), ('Ocupada', 'Ocupada'), ('Em Manutencao', 'Em Manutencao')], default='Disponivel', max_length=20),
        ),
    ]
