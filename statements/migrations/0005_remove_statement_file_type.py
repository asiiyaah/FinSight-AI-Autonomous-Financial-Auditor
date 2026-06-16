# Generated migration to remove file_type field

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statements', '0004_remove_statement_audit_result_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='statement',
            name='file_type',
        ),
    ]
