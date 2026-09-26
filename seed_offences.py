import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "blueshield_project.settings"
)

django.setup()

from records.models import CriminalOffence


offences = [
    {
        "code": "OFF-001",
        "title": "Theft",
        "category": "PROPERTY",
        "penalty_summary": "Unlawful taking or appropriation of property belonging to another person.",
    },
    {
        "code": "OFF-002",
        "title": "Assault",
        "category": "PERSON",
        "penalty_summary": "An unlawful act involving physical harm or threat of harm against another person.",
    },
    {
        "code": "OFF-003",
        "title": "Burglary",
        "category": "PROPERTY",
        "penalty_summary": "Unlawful entry into a building or premises with intent to commit an offence.",
    },
    {
        "code": "OFF-004",
        "title": "Robbery",
        "category": "PROPERTY",
        "penalty_summary": "Taking property from another person through force, threat, or intimidation.",
    },
    {
        "code": "OFF-005",
        "title": "Murder",
        "category": "PERSON",
        "penalty_summary": "Unlawful killing of another person.",
    },
    {
        "code": "OFF-006",
        "title": "Manslaughter",
        "category": "PERSON",
        "penalty_summary": "Unlawful killing of another person under circumstances distinguished from murder.",
    },
    {
        "code": "OFF-007",
        "title": "Sexual Offence",
        "category": "PERSON",
        "penalty_summary": "An unlawful sexual act or conduct against another person.",
    },
    {
        "code": "OFF-008",
        "title": "Domestic Violence",
        "category": "PERSON",
        "penalty_summary": "Violence, threats, or abusive conduct occurring within a domestic or family relationship.",
    },
    {
        "code": "OFF-009",
        "title": "Property Damage",
        "category": "PROPERTY",
        "penalty_summary": "Unlawful destruction, damage, or interference with property.",
    },
    {
        "code": "OFF-010",
        "title": "Drug Offence",
        "category": "DRUG",
        "penalty_summary": "An offence involving the unlawful possession, supply, production, or use of controlled substances.",
    },
    {
        "code": "OFF-011",
        "title": "Fraud",
        "category": "FINANCIAL",
        "penalty_summary": "Obtaining property, money, or advantage through deception or dishonest conduct.",
    },
    {
        "code": "OFF-012",
        "title": "Possession of Stolen Property",
        "category": "PROPERTY",
        "penalty_summary": "Possessing property suspected or known to have been unlawfully obtained.",
    },
    {
        "code": "OFF-013",
        "title": "Trespassing",
        "category": "PROPERTY",
        "penalty_summary": "Unlawfully entering or remaining on property without authorization.",
    },
    {
        "code": "OFF-014",
        "title": "Unlawful Possession of Weapon",
        "category": "WEAPON",
        "penalty_summary": "Possession of a weapon in circumstances where such possession is unlawful.",
    },
    {
        "code": "OFF-015",
        "title": "Traffic Offence",
        "category": "TRAFFIC",
        "penalty_summary": "An offence involving the unlawful operation or use of a motor vehicle or road-related conduct.",
    },
]


for offence_data in offences:

    offence, created = CriminalOffence.objects.get_or_create(
        code=offence_data["code"],
        defaults={
            "title": offence_data["title"],
            "category": offence_data["category"],
            "penalty_summary": offence_data["penalty_summary"],
        }
    )

    if created:
        print(
            f"Created offence: "
            f"{offence.code} - {offence.title}"
        )
    else:
        print(
            f"Offence already exists: "
            f"{offence.code} - {offence.title}"
        )


print("\nCriminal offence seeding completed successfully.")