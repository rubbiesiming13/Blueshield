import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blueshield_project.settings")
django.setup()

from stations.models import District, PoliceStation


districts = {
    "Usino Bundi": [
        "Usino",
        "Walium",
        "Ramu Sugar",
        "Bundi",
    ],

    "Bogia": [
        "Bogia",
    ],

    "Sumkar": [
        "Talidig",
        "Karkar",
        "Dilup",
        "Taur Police Detect",
    ],

    "Raicoast": [
        "Saidor",
        "Ileg",
        "Tauta",
    ],

    "Madang": [
        "Jomba",
        "Mawan",
        "Town",
    ],

    "Middle Ramu": [
        "Nodobu",
        "Aiome",
        "Simbai",
    ],
}


for district_name, station_names in districts.items():

    district, created = District.objects.get_or_create(
        name=district_name,
        defaults={
            "province": "Madang",
            "is_active": True,
        }
    )

    if created:
        print(f"Created district: {district_name}")
    else:
        print(f"District already exists: {district_name}")

    for station_name in station_names:

        station, station_created = PoliceStation.objects.get_or_create(
            name=station_name,
            district=district,
            defaults={
                "province": "Madang",
                "commander_name": "",
                "phone_number": "",
                "address": "",
                "is_active": True,
            }
        )

        if station_created:
            print(
                f"  Created station: {station_name} "
                f"-> {district_name}"
            )
        else:
            print(
                f"  Station already exists: {station_name} "
                f"-> {district_name}"
            )


print("\nStation and district seeding completed successfully.")