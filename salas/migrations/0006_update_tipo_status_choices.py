from django.db import migrations, models


def migrate_tipo_status(apps, schema_editor):
    Sala = apps.get_model("salas", "Sala")
    allowed_tipos = {"Individual", "Coletiva", "Auditorio"}
    tipo_map = {
        "Sala de Aula": "Coletiva",
        "Laboratorio": "Coletiva",
        "Auditorio": "Auditorio",
    }
    status_map = {"Ocupada": "Em Manutencao"}

    for sala in Sala.objects.all():
        new_tipo = tipo_map.get(sala.tipo, sala.tipo)
        if new_tipo not in allowed_tipos:
            new_tipo = "Coletiva"

        new_status = status_map.get(sala.status, sala.status)
        if new_status not in {"Disponivel", "Em Manutencao"}:
            new_status = "Disponivel"

        if new_tipo != sala.tipo or new_status != sala.status:
            sala.tipo = new_tipo
            sala.status = new_status
            sala.save(update_fields=["tipo", "status"])


class Migration(migrations.Migration):

    dependencies = [
        ("salas", "0005_alter_sala_capacidade_alter_sala_nome"),
    ]

    operations = [
        migrations.RunPython(migrate_tipo_status, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="sala",
            name="tipo",
            field=models.CharField(
                choices=[("Individual", "Individual"), ("Coletiva", "Coletiva"), ("Auditorio", "Auditorio")],
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="sala",
            name="status",
            field=models.CharField(
                choices=[("Disponivel", "Disponivel"), ("Em Manutencao", "Em Manutencao")],
                default="Disponivel",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="sala",
            name="localizacao",
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name="Localizacao"),
        ),
    ]
