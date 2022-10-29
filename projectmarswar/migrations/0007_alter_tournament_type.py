# Generated by Django 3.2.14 on 2022-10-27 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projectmarswar', '0006_match_rating_change'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournament',
            name='type',
            field=models.CharField(choices=[('SG', 'Start.gg'), ('CH', 'Challonge')], max_length=2),
        ),
    ]