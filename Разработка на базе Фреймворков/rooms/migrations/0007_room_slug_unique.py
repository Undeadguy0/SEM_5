from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rooms", "0006_populate_room_slugs"),
    ]

    operations = [
        migrations.AlterField(
            model_name="room",
            name="slug",
            field=models.SlugField(
                editable=False,
                max_length=180,
                unique=True,
                verbose_name="URL-идентификатор",
            ),
        ),
    ]
