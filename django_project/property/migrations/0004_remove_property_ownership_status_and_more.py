# Generated by Django 4.1.7 on 2023-06-30 11:45

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("property", "0003_parcel_farm_name_parcel_farm_number_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="property",
            name="ownership_status",
        ),
        migrations.DeleteModel(
            name="OwnershipStatus",
        ),
    ]
