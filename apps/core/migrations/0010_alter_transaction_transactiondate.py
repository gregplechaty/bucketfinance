# Generated by Django 3.2 on 2021-04-12 04:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_rename_date_transaction_transactiondate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transactionDate',
            field=models.DateField(),
        ),
    ]
