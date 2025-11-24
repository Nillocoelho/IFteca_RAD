from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Sala",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=255)),
                ("capacidade", models.PositiveIntegerField()),
                (
                    "tipo",
                    models.CharField(
                        choices=[
                            ("Sala de Aula", "Sala de Aula"),
                            ("Laboratório", "Laboratório"),
                            ("Auditório", "Auditório"),
                        ],
                        max_length=50,
                    ),
                ),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["nome"]},
        ),
    ]
