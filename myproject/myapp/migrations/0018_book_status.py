from django.db import migrations, models


def publish_existing_priced_books(apps, schema_editor):
    Book = apps.get_model("myapp", "Book")
    Book.objects.filter(price__isnull=False).update(status="published")


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0017_alter_bookorder_address_line2_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="book",
            name="status",
            field=models.CharField(
                choices=[("draft", "Draft"), ("published", "Published")],
                default="draft",
                max_length=20,
            ),
        ),
        migrations.RunPython(publish_existing_priced_books, migrations.RunPython.noop),
    ]