from django.db import migrations, models


def remap_tipo_individual(apps, schema_editor):
    Sala = apps.get_model("salas", "Sala")
    Sala.objects.filter(tipo="Individual").update(tipo="Coletiva")


class Migration(migrations.Migration):

    dependencies = [
        ("salas", "0006_update_tipo_status_choices"),
    ]

    operations = [
        migrations.RunPython(remap_tipo_individual, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="sala",
            name="tipo",
            field=models.CharField(choices=[("Coletiva", "Coletiva"), ("Auditorio", "Auditorio")], max_length=50),
        ),
    ]
