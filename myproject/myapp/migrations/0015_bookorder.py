from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0014_exchangerequest_exchangemessage_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="BookOrder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("payment_method", models.CharField(choices=[("cash", "Cash on delivery"), ("online", "Online payment")], max_length=10)),
                ("status", models.CharField(choices=[("placed", "Order placed"), ("confirmed", "Confirmed"), ("cancelled", "Cancelled")], default="placed", max_length=20)),
                ("payment_status", models.CharField(choices=[("pending", "Payment pending"), ("paid", "Paid"), ("failed", "Payment failed")], default="pending", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("book", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="orders", to="myapp.book")),
                ("buyer", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="book_orders", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]