from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("salas", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="sala",
            name="localizacao",
            field=models.CharField(max_length=255, null=True, blank=True, verbose_name='Localização (Bloco/Andar)'),
        ),
    ]
