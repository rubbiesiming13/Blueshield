from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0002_district_alter_policestation_district'),
    ]

    operations = [
        migrations.CreateModel(
            name='Province',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID'
                    )
                ),
                (
                    'name',
                    models.CharField(
                        max_length=100,
                        unique=True
                    )
                ),
                (
                    'code',
                    models.CharField(
                        blank=True,
                        max_length=20,
                        unique=True
                    )
                ),
                (
                    'is_active',
                    models.BooleanField(
                        default=True
                    )
                ),
                (
                    'created_at',
                    models.DateTimeField(
                        auto_now_add=True
                    )
                ),
                (
                    'updated_at',
                    models.DateTimeField(
                        auto_now=True
                    )
                ),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]