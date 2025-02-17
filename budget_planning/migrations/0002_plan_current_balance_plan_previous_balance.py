# Generated by Django 5.0.7 on 2024-07-24 03:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget_planning', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='current_balance',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='plan',
            name='previous_balance',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
