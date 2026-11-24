from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rooms", "0003_remove_room_n"),
    ]

    operations = [
        migrations.AddField(
            model_name="room",
            name="slug",
            field=models.SlugField(
                blank=True,
                default="",
                max_length=180,
                verbose_name="URL-идентификатор",
            ),
        ),
    ]
