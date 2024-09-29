from django.db import migrations, models
import django_cryptography.fields


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0007_auto_20240927_0845'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='note_content',
            field=django_cryptography.fields.encrypt(models.TextField(default='Test')),
            preserve_default=False,
        ),
    ]
