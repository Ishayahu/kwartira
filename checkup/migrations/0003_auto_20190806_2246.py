# Generated by Django 2.1.7 on 2019-08-06 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkup', '0002_auto_20190806_2151'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visit',
            name='date',
            field=models.DateField(),
        ),
    ]