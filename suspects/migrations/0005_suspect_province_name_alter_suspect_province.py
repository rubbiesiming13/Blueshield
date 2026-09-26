from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("stations", "0003_province_alter_district_province"),
        ("suspects", "0004_suspect_registered_by_suspect_station"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AddField(
                    model_name="suspect",
                    name="province_name",
                    field=models.CharField(
                        max_length=100,
                        blank=True,
                        null=True,
                    ),
                ),
                migrations.RemoveField(
                    model_name="suspect",
                    name="province",
                ),
                migrations.AddField(
                    model_name="suspect",
                    name="province",
                    field=models.ForeignKey(
                        to="stations.province",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="suspects",
                        null=True,
                        blank=True,
                    ),
                ),
            ],
        ),
    ]