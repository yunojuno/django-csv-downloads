# Generated by Django 4.2.6 on 2023-10-10 16:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("django_csv", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="csvdownload",
            name="columns",
            field=models.TextField(
                help_text="The list of source columns included in the download",
            ),
        ),
    ]
