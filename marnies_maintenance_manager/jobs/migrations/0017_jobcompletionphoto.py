# Generated by Django 5.0.7 on 2024-07-31 13:23

import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import private_storage.fields
import private_storage.storage.files
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0016_alter_job_deposit_proof_of_payment_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="JobCompletionPhoto",
            fields=[
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "photo",
                    private_storage.fields.PrivateImageField(
                        storage=private_storage.storage.files.PrivateFileSystemStorage(),
                        upload_to="completion_photos/",
                    ),
                ),
                (
                    "job",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="job_completion_photos",
                        to="jobs.job",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]