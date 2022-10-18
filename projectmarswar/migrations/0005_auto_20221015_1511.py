# Generated by Django 3.2.14 on 2022-10-15 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projectmarswar', '0004_auto_20221015_0337'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='adjusted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='match',
            name='player1_rating',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='match',
            name='player2_rating',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
