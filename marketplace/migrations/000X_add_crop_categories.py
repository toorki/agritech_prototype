from django.db import migrations

def add_crop_categories(apps, schema_editor):
    ProduceCategory = apps.get_model('marketplace', 'ProduceCategory')
    categories = [
        "Cereals",
        "Legumes",
        "Vegetables",
        "Fruits",
        "Oilseeds",
        "Root Crops",
        "Herbs and Spices",
        "Nuts",
        "Fodder Crops",
        "Industrial Crops",
    ]
    for name in categories:
        ProduceCategory.objects.get_or_create(name=name)

def remove_crop_categories(apps, schema_editor):
    ProduceCategory = apps.get_model('marketplace', 'ProduceCategory')
    categories = [
        "Cereals",
        "Legumes",
        "Vegetables",
        "Fruits",
        "Oilseeds",
        "Root Crops",
        "Herbs and Spices",
        "Nuts",
        "Fodder Crops",
        "Industrial Crops",
    ]
    ProduceCategory.objects.filter(name__in=categories).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('marketplace', '0001_initial'),  # Use this if 0001_initial is the last applied migration
    ]

    operations = [
        migrations.RunPython(add_crop_categories, remove_crop_categories),
    ]