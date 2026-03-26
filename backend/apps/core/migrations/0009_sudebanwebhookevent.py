from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_seed_complete_actividades_economicas"),
    ]

    operations = [
        migrations.CreateModel(
            name="SudebanWebhookEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "api",
                    models.CharField(
                        choices=[
                            ("API-01", "API-01"),
                            ("API-02", "API-02"),
                            ("API-03", "API-03"),
                            ("API-04", "API-04"),
                        ],
                        max_length=10,
                    ),
                ),
                ("path", models.CharField(blank=True, default="", max_length=200)),
                ("remote_addr", models.CharField(blank=True, default="", max_length=80)),
                ("headers", models.JSONField(blank=True, default=dict)),
                ("raw_body", models.TextField(blank=True, default="")),
                ("payload", models.JSONField(blank=True, null=True)),
                ("parse_success", models.BooleanField(default=True)),
                ("error_code", models.BigIntegerField(blank=True, null=True)),
                ("decoded_errors", models.JSONField(blank=True, default=list)),
            ],
            options={
                "db_table": "core_sudeban_webhook_events",
                "ordering": ["-created_at"],
            },
        ),
    ]
