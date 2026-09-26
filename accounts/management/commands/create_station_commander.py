
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.models import User
from stations.models import District, PoliceStation


class Command(BaseCommand):
    help = (
        "Create or update the 18 demo Station Commander accounts "
        "and assign them to their correct police stations and districts."
    )

    COMMANDERS = [
        {
            "district": "Usino Bundi",
            "station": "Usino",
            "first_name": "Peter",
            "last_name": "Wama",
            "username": "commander.usino",
            "sevispass_id": "261001",
            "badge_number": "SC-001",
        },
        {
            "district": "Usino Bundi",
            "station": "Walium",
            "first_name": "Daniel",
            "last_name": "Kora",
            "username": "commander.walium",
            "sevispass_id": "261002",
            "badge_number": "SC-002",
        },
        {
            "district": "Usino Bundi",
            "station": "Ramu Sugar",
            "first_name": "Michael",
            "last_name": "Yaro",
            "username": "commander.ramu_sugar",
            "sevispass_id": "261003",
            "badge_number": "SC-003",
        },
        {
            "district": "Usino Bundi",
            "station": "Bundi",
            "first_name": "Joseph",
            "last_name": "Namo",
            "username": "commander.bundi",
            "sevispass_id": "261004",
            "badge_number": "SC-004",
        },
        {
            "district": "Bogia",
            "station": "Bogia",
            "first_name": "Samuel",
            "last_name": "Kila",
            "username": "commander.bogia",
            "sevispass_id": "261005",
            "badge_number": "SC-005",
        },
        {
            "district": "Sumkar",
            "station": "Talidig",
            "first_name": "Thomas",
            "last_name": "Wari",
            "username": "commander.talidig",
            "sevispass_id": "261006",
            "badge_number": "SC-006",
        },
        {
            "district": "Sumkar",
            "station": "Karkar",
            "first_name": "Andrew",
            "last_name": "Saki",
            "username": "commander.karkar",
            "sevispass_id": "261007",
            "badge_number": "SC-007",
        },
        {
            "district": "Sumkar",
            "station": "Dilup",
            "first_name": "Martin",
            "last_name": "Kewa",
            "username": "commander.dilup",
            "sevispass_id": "261008",
            "badge_number": "SC-008",
        },
        {
            "district": "Sumkar",
            "station": "Taur Police Detect",
            "first_name": "David",
            "last_name": "Mako",
            "username": "commander.taur",
            "sevispass_id": "261009",
            "badge_number": "SC-009",
        },
        {
            "district": "Raicoast",
            "station": "Saidor",
            "first_name": "John",
            "last_name": "Ravu",
            "username": "commander.saidor",
            "sevispass_id": "261010",
            "badge_number": "SC-010",
        },
        {
            "district": "Raicoast",
            "station": "Ileg",
            "first_name": "Francis",
            "last_name": "Wama",
            "username": "commander.ileg",
            "sevispass_id": "261011",
            "badge_number": "SC-011",
        },
        {
            "district": "Raicoast",
            "station": "Tauta",
            "first_name": "Benjamin",
            "last_name": "Kila",
            "username": "commander.tauta",
            "sevispass_id": "261012",
            "badge_number": "SC-012",
        },
        {
            "district": "Madang",
            "station": "Jomba",
            "first_name": "Robert",
            "last_name": "Yama",
            "username": "commander.jomba",
            "sevispass_id": "261013",
            "badge_number": "SC-013",
        },
        {
            "district": "Madang",
            "station": "Mawan",
            "first_name": "William",
            "last_name": "Saro",
            "username": "commander.mawan",
            "sevispass_id": "261014",
            "badge_number": "SC-014",
        },
        {
            "district": "Madang",
            "station": "Town",
            "first_name": "Patrick",
            "last_name": "Nori",
            "username": "commander.town",
            "sevispass_id": "261015",
            "badge_number": "SC-015",
        },
        {
            "district": "Middle Ramu",
            "station": "Nodobu",
            "first_name": "George",
            "last_name": "Waku",
            "username": "commander.nodobu",
            "sevispass_id": "261016",
            "badge_number": "SC-016",
        },
        {
            "district": "Middle Ramu",
            "station": "Aiome",
            "first_name": "Philip",
            "last_name": "Karo",
            "username": "commander.aiome",
            "sevispass_id": "261017",
            "badge_number": "SC-017",
        },
        {
            "district": "Middle Ramu",
            "station": "Simbai",
            "first_name": "Anthony",
            "last_name": "Mera",
            "username": "commander.simbai",
            "sevispass_id": "261018",
            "badge_number": "SC-018",
        },
    ]

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write("")
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "BlueShield Station Commander Setup"
            )
        )

        self.stdout.write(
            "Creating/updating 18 demo Station Commander accounts..."
        )
        self.stdout.write("")

        created_count = 0
        updated_count = 0

        for data in self.COMMANDERS:

            district_name = data["district"]
            station_name = data["station"]

            # =================================================
            # FIND DISTRICT
            # =================================================

            try:
                district = District.objects.get(
                    name__iexact=district_name
                )
            except District.DoesNotExist:
                raise CommandError(
                    f"District not found: {district_name}"
                )

            # =================================================
            # FIND STATION
            # =================================================

            try:
                station = PoliceStation.objects.get(
                    name__iexact=station_name,
                    district=district,
                )
            except PoliceStation.DoesNotExist:

                other_station = PoliceStation.objects.filter(
                    name__iexact=station_name
                ).first()

                if other_station:
                    raise CommandError(
                        f"Station '{station_name}' exists, but belongs "
                        f"to '{other_station.district.name}', not "
                        f"'{district_name}'."
                    )

                raise CommandError(
                    f"Police station not found: "
                    f"{station_name} ({district_name})"
                )

            # =================================================
            # FIND USER
            #
            # First search by SevisPass ID.
            # Then search by username.
            # This prevents duplicate SevisPass IDs.
            # =================================================

            user = User.objects.filter(
                sevispass_id=data["sevispass_id"]
            ).first()

            if user is None:
                user = User.objects.filter(
                    username=data["username"]
                ).first()

            created = False

            # =================================================
            # CREATE USER IF IT DOES NOT EXIST
            # =================================================

            if user is None:

                user = User(
                    username=data["username"],
                    first_name=data["first_name"],
                    last_name=data["last_name"],
                    role="STATION_COMMANDER",
                    badge_number=data["badge_number"],
                    rank="Station Commander",
                    district=district,
                    station=station,
                    sevispass_id=data["sevispass_id"],
                    sevispass_verified=False,
                    is_active=True,
                )

                user.set_password("BlueShieldDemo123!")
                user.save()

                created = True
                created_count += 1

            # =================================================
            # UPDATE EXISTING USER
            # =================================================

            else:

                user.first_name = data["first_name"]
                user.last_name = data["last_name"]

                user.role = "STATION_COMMANDER"

                user.badge_number = data["badge_number"]
                user.rank = "Station Commander"

                user.district = district
                user.station = station

                user.sevispass_id = data["sevispass_id"]

                user.is_active = True

                # Do not bypass SevisPass authentication.
                user.sevispass_verified = False
                user.sevispass_verified_at = None

                user.save()

                updated_count += 1

            # =================================================
            # UPDATE POLICE STATION COMMANDER NAME
            # =================================================

            full_name = (
                f"{data['first_name']} "
                f"{data['last_name']}"
            )

            station.commander_name = full_name

            station.save(
                update_fields=["commander_name"]
            )

            # =================================================
            # DISPLAY RESULT
            # =================================================

            if created:
                action = "CREATED"
            else:
                action = "UPDATED"

            self.stdout.write(
                self.style.SUCCESS(
                    f"[{action}] "
                    f"{full_name} | "
                    f"SevisPass: {data['sevispass_id']} | "
                    f"Station: {station.name} | "
                    f"District: {district.name}"
                )
            )

        # =====================================================
        # FINAL SUMMARY
        # =====================================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "=============================================="
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Station Commander setup completed successfully."
            )
        )

        self.stdout.write(
            f"Created: {created_count}"
        )

        self.stdout.write(
            f"Updated: {updated_count}"
        )

        self.stdout.write(
            f"Total processed: {len(self.COMMANDERS)}"
        )

        self.stdout.write(
            self.style.SUCCESS(
                "=============================================="
            )
        )

        self.stdout.write("")

        self.stdout.write(
            "SevisPass verification remains FALSE for "
            "all demo commanders."
        )

        self.stdout.write(
            "New accounts use the local demo password:"
        )

        self.stdout.write(
            "BlueShieldDemo123!"
        )

        self.stdout.write("")

