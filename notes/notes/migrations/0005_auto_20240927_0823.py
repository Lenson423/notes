# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django_cryptography.fields import encrypt

app_with_model = 'notes'
model_with_column = 'Note'
column_to_encrypt = 'note_content'
column_field_class = models.TextField
column_attrs = {}
column_null_status = True
temporary_column = f'temp_{column_to_encrypt}'

def replicate_to_temporary(apps, schema_editor):
    Model = apps.get_model(app_with_model, model_with_column)
    for row in Model.objects.all():
        setattr(row, temporary_column, getattr(row, column_to_encrypt, None))
        setattr(row, column_to_encrypt, None)
        row.save(update_fields=[temporary_column, column_to_encrypt])

def replicate_to_real(apps, schema_editor):
    Model = apps.get_model(app_with_model, model_with_column)
    for row in Model.objects.all():
        setattr(row, column_to_encrypt, getattr(row, temporary_column))
        row.save(update_fields=[column_to_encrypt])

class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0004_auto_20240927_1919'),
    ]

    operations = [
        migrations.AddField(
            model_name=model_with_column.lower(),
            name=temporary_column,
            field=column_field_class(
                verbose_name=temporary_column, null=True, **column_attrs),
        ),
        migrations.AlterField(
            model_name=model_with_column.lower(),
            name=column_to_encrypt,
            field=column_field_class(
                verbose_name=column_to_encrypt, null=True, **column_attrs),
        ),
        migrations.RunPython(replicate_to_temporary),
        migrations.AlterField(
            model_name=model_with_column.lower(),
            name=column_to_encrypt,
            field=encrypt(column_field_class(
                verbose_name=column_to_encrypt, null=True, **column_attrs)),
        ),
        migrations.RunPython(replicate_to_real),
        migrations.RemoveField(
            model_name=model_with_column.lower(),
            name=temporary_column),
        migrations.AlterField(
            model_name=model_with_column.lower(),
            name=column_to_encrypt,
            field=encrypt(column_field_class(
                verbose_name=column_to_encrypt, null=column_null_status, 
                **column_attrs)),
        ),
    ]