from django.db import migrations, models
import django.db.models.deletion


def copy_salas_forward(apps, schema_editor):
    OldSala = apps.get_model('reservas', 'Sala')
    NewSala = apps.get_model('salas', 'Sala')
    Reserva = apps.get_model('reservas', 'Reserva')

    # Map old tipo values to new app's tipo choices (best-effort)
    tipo_map = {
        'ESTUDO_INDIVIDUAL': 'Sala de Aula',
        'ESTUDO_GRUPO': 'Sala de Aula',
        'LABORATORIO': 'Laboratorio',
        'SALA_AULA': 'Sala de Aula',
    }

    id_map = {}

    for old in OldSala.objects.all():
        new_tipo = tipo_map.get(getattr(old, 'tipo', None), 'Sala de Aula')
        new = NewSala.objects.create(
            nome=old.nome,
            capacidade=getattr(old, 'capacidade', 1) or 1,
            tipo=new_tipo,
        )
        id_map[old.id] = new.id

    # Update Reserva entries to point to the new Sala ids
    for r in Reserva.objects.all():
        old_id = r.sala_id
        if old_id in id_map:
            r.sala_id = id_map[old_id]
            r.save()
        else:
            # Fallback: try match by name, else assign first Sala
            try:
                # r.sala may be a relation to old model; try to access name
                nome = getattr(r.sala, 'nome', None)
            except Exception:
                nome = None
            if nome:
                try:
                    candidate = NewSala.objects.get(nome=nome)
                    r.sala_id = candidate.id
                    r.save()
                    continue
                except NewSala.DoesNotExist:
                    pass
            first = NewSala.objects.first()
            if first:
                r.sala_id = first.id
                r.save()


def copy_salas_backward(apps, schema_editor):
    # Best-effort reverse: recreate reservas.Sala entries from salas.Sala
    OldSala = apps.get_model('reservas', 'Sala')
    NewSala = apps.get_model('salas', 'Sala')
    Reserva = apps.get_model('reservas', 'Reserva')

    id_map = {}
    for new in NewSala.objects.all():
        old = OldSala.objects.create(
            nome=new.nome,
            capacidade=getattr(new, 'capacidade', 1) or 1,
            tipo='ESTUDO_GRUPO',
            localizacao='',
        )
        id_map[new.id] = old.id

    for r in Reserva.objects.all():
        new_id = r.sala_id
        if new_id in id_map:
            r.sala_id = id_map[new_id]
            r.save()


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0002_reserva'),
        ('salas', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(copy_salas_forward, reverse_code=copy_salas_backward),
        migrations.AlterField(
            model_name='reserva',
            name='sala',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservas', to='salas.sala'),
        ),
        migrations.DeleteModel(
            name='Sala',
        ),
    ]
