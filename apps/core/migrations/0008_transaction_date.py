# Generated by Django 3.2 on 2021-04-12 04:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_rename_userid_bucket_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='date',
            field=models.DateField(auto_now=True),
        ),
    ]