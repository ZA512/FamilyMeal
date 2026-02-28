# Generated manually on 2026-03-01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0006_variant_ingredients'),
    ]

    operations = [
        migrations.AddField(
            model_name='preference',
            name='ingredient_variant',
            field=models.ForeignKey(
                blank=True,
                help_text='Variant concerné (ex: Penne dans Bolognaise). Null = préférence générale du plat.',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='preferences_variant',
                to='meals.ingredient',
            ),
        ),
        migrations.AlterUniqueTogether(
            name='preference',
            unique_together={('membre', 'plat', 'ingredient_variant')},
        ),
    ]
