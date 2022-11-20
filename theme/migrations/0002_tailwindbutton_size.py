# Generated by Django 3.2.14 on 2022-11-20 03:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tailwindbutton',
            name='size',
            field=models.CharField(choices=[('normal', 'normal'), ('text-xl', 'text-xl'), ('text-2xl', 'text-2xl'), ('text-5xl', 'text-5xl')], default='normal', help_text='The size of the text in the button', max_length=255, verbose_name='Size'),
        ),
    ]
