from django.db import migrations, models
import django_cryptography.fields


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0008_auto_20240927_1804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='note_content',
            field=django_cryptography.fields.encrypt(models.TextField(blank=True, null=True)),
        ),
    ]
