from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("salas", "0003_add_equip_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="sala",
            name="descricao",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="sala",
            name="localizacao",
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name="Localizacao (Bloco/Andar)"),
        ),
    ]
