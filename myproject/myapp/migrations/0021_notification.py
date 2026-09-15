from django.db import migrations, models
import django.db.models.deletion


def seed_existing_offer_notifications(apps, schema_editor):
    Notification = apps.get_model("myapp", "Notification")
    User = apps.get_model("auth", "User")
    Book = apps.get_model("myapp", "Book")

    users = list(User.objects.filter(is_active=True))
    offers = Book.objects.filter(
        status="published", price__isnull=False, offer_percentage__gt=0
    ).select_related("seller__user")
    Notification.objects.bulk_create(
        [
            Notification(user=user, book=book)
            for book in offers
            for user in users
            if user.id != book.seller.user_id
        ],
        ignore_conflicts=True,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0020_bookorder_cancellation"),
    ]

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_read", models.BooleanField(default=False)),
                ("is_removed", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "book",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to="myapp.book",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to="auth.user",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddConstraint(
            model_name="notification",
            constraint=models.UniqueConstraint(
                fields=("user", "book"), name="unique_book_notification"
            ),
        ),
        migrations.RunPython(
            seed_existing_offer_notifications, migrations.RunPython.noop
        ),
    ]
