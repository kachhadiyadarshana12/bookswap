from django.db import migrations


def seed_book_catalogs(apps, schema_editor):
    BookCategory = apps.get_model("myapp", "BookCategory")
    BookLanguage = apps.get_model("myapp", "BookLanguage")

    BookCategory.objects.bulk_create(
        [
            BookCategory(code=code, name=name)
            for code, name in [
                ("fiction", "Fiction"),
                ("non-fiction", "Non-Fiction"),
                ("finance", "Finance"),
                ("history", "History"),
                ("biography", "Biography"),
                ("science", "Science"),
                ("technology", "Technology"),
                ("self-help", "Self Help"),
                ("romance", "Romance"),
                ("education", "Education"),
                ("other", "Other"),
            ]
        ],
        ignore_conflicts=True,
    )
    BookLanguage.objects.bulk_create(
        [
            BookLanguage(code=code, name=name)
            for code, name in [
                ("English", "English"),
                ("Gujarati", "Gujarati"),
                ("Hindi", "Hindi"),
                ("Marathi", "Marathi"),
                ("Bengali", "Bengali"),
                ("Tamil", "Tamil"),
                ("Telugu", "Telugu"),
                ("Other", "Other"),
            ]
        ],
        ignore_conflicts=True,
    )


class Migration(migrations.Migration):
    dependencies = [("myapp", "0011_bookcategory_booklanguage")]

    operations = [migrations.RunPython(seed_book_catalogs, migrations.RunPython.noop)]