# Generated by Django 3.2.5 on 2022-03-25 16:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bookclub', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rating',
            options={'ordering': ['book']},
        ),
    ]