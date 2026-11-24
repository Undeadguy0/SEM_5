from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rooms", "0004_room_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="room",
            name="is_large",
            field=models.GeneratedField(
                db_persist=True,
                expression=models.Case(
                    models.When(
                        capacity__gte=50,
                        then=models.Value(True),
                    ),
                    default=models.Value(False),
                    output_field=models.BooleanField(),
                ),
                output_field=models.BooleanField(),
                verbose_name="Большое помещение",
            ),
        ),
    ]
