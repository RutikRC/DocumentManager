# Generated by Django 5.0 on 2023-12-31 11:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0004_alter_job_po_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='job',
            old_name='status',
            new_name='project_status',
        ),
    ]
