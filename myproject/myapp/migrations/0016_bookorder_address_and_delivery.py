from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("myapp", "0015_bookorder")]

    operations = [
        migrations.AddField(
            model_name="bookorder",
            name="address_line1",
            field=models.CharField(default="", max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="bookorder",
            name="address_line2",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
        migrations.AddField(
            model_name="bookorder",
            name="city",
            field=models.CharField(default="", max_length=80),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="bookorder",
            name="delivery_note",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="bookorder",
            name="delivery_status",
            field=models.CharField(choices=[("pending", "Delivery pending"), ("packed", "Packed"), ("shipped", "Shipped"), ("out_for_delivery", "Out for delivery"), ("delivered", "Delivered")], default="pending", max_length=20),
        ),
        migrations.AddField(
            model_name="bookorder",
            name="payment_reference",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="bookorder",
            name="postal_code",
            field=models.CharField(default="", max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="bookorder",
            name="recipient_name",
            field=models.CharField(default="", max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="bookorder",
            name="recipient_phone",
            field=models.CharField(default="", max_length=15),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="bookorder",
            name="state",
            field=models.CharField(default="", max_length=80),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="bookorder",
            name="tracking_reference",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
    ]