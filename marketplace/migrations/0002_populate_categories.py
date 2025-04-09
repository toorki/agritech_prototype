from django.db import migrations

def populate_categories(apps, schema_editor):
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

class Migration(migrations.Migration):
    dependencies = [
        ('marketplace', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(populate_categories),
    ]