# Generated by Django 5.2 on 2025-06-22 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("documentacion", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="artefacto",
            name="contexto",
            field=models.TextField(blank=True, null=True),
        ),
    ]
