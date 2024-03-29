# Generated by Django 3.1.2 on 2020-10-15 05:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CsvDownload",
            options={"verbose_name": "CSV Download"},
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("filename", models.CharField(max_length=100)),
                (
                    "timestamp",
                    models.DateTimeField(
                        auto_now_add=True, help_text="When the download took place."
                    ),
                ),
                (
                    "row_count",
                    models.IntegerField(
                        blank=True, help_text="Rows downloaded", null=True
                    ),
                ),
                (
                    "columns",
                    models.CharField(
                        help_text="The list of source columns included in the download",
                        max_length=500,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="User who initiated the download.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
