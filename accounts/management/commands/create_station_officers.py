
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.models import User
from stations.models import District, PoliceStation


class Command(BaseCommand):
    help = (
        "Create or update 90 demo Police Officers "
        "with 5 officers assigned to each of the 18 police stations."
    )

    # =========================================================
    # 18 STATIONS × 5 OFFICERS = 90 OFFICERS
    # =========================================================

    OFFICERS = [

        # =====================================================
        # USINO BUNDI DISTRICT
        # =====================================================

        {
            "district": "Usino Bundi",
            "station": "Usino",
            "first_name": "Peter",
            "last_name": "Kila",
            "username": "officer.usino.01",
            "sevispass_id": "271001",
            "badge_number": "PO-001",
        },
        {
            "district": "Usino Bundi",
            "station": "Usino",
            "first_name": "Grace",
            "last_name": "Wama",
            "username": "officer.usino.02",
            "sevispass_id": "271002",
            "badge_number": "PO-002",
        },
        {
            "district": "Usino Bundi",
            "station": "Usino",
            "first_name": "Joseph",
            "last_name": "Saro",
            "username": "officer.usino.03",
            "sevispass_id": "271003",
            "badge_number": "PO-003",
        },
        {
            "district": "Usino Bundi",
            "station": "Usino",
            "first_name": "Maria",
            "last_name": "Kewa",
            "username": "officer.usino.04",
            "sevispass_id": "271004",
            "badge_number": "PO-004",
        },
        {
            "district": "Usino Bundi",
            "station": "Usino",
            "first_name": "Daniel",
            "last_name": "Yaro",
            "username": "officer.usino.05",
            "sevispass_id": "271005",
            "badge_number": "PO-005",
        },

        {
            "district": "Usino Bundi",
            "station": "Walium",
            "first_name": "Thomas",
            "last_name": "Mako",
            "username": "officer.walium.01",
            "sevispass_id": "271006",
            "badge_number": "PO-006",
        },
        {
            "district": "Usino Bundi",
            "station": "Walium",
            "first_name": "Alice",
            "last_name": "Ravu",
            "username": "officer.walium.02",
            "sevispass_id": "271007",
            "badge_number": "PO-007",
        },
        {
            "district": "Usino Bundi",
            "station": "Walium",
            "first_name": "Benjamin",
            "last_name": "Kora",
            "username": "officer.walium.03",
            "sevispass_id": "271008",
            "badge_number": "PO-008",
        },
        {
            "district": "Usino Bundi",
            "station": "Walium",
            "first_name": "Ruth",
            "last_name": "Namo",
            "username": "officer.walium.04",
            "sevispass_id": "271009",
            "badge_number": "PO-009",
        },
        {
            "district": "Usino Bundi",
            "station": "Walium",
            "first_name": "Samuel",
            "last_name": "Wari",
            "username": "officer.walium.05",
            "sevispass_id": "271010",
            "badge_number": "PO-010",
        },

        {
            "district": "Usino Bundi",
            "station": "Ramu Sugar",
            "first_name": "Mark",
            "last_name": "Kewa",
            "username": "officer.ramu_sugar.01",
            "sevispass_id": "271011",
            "badge_number": "PO-011",
        },
        {
            "district": "Usino Bundi",
            "station": "Ramu Sugar",
            "first_name": "Helen",
            "last_name": "Saki",
            "username": "officer.ramu_sugar.02",
            "sevispass_id": "271012",
            "badge_number": "PO-012",
        },
        {
            "district": "Usino Bundi",
            "station": "Ramu Sugar",
            "first_name": "Patrick",
            "last_name": "Mera",
            "username": "officer.ramu_sugar.03",
            "sevispass_id": "271013",
            "badge_number": "PO-013",
        },
        {
            "district": "Usino Bundi",
            "station": "Ramu Sugar",
            "first_name": "Janet",
            "last_name": "Waku",
            "username": "officer.ramu_sugar.04",
            "sevispass_id": "271014",
            "badge_number": "PO-014",
        },
        {
            "district": "Usino Bundi",
            "station": "Ramu Sugar",
            "first_name": "George",
            "last_name": "Kila",
            "username": "officer.ramu_sugar.05",
            "sevispass_id": "271015",
            "badge_number": "PO-015",
        },

        {
            "district": "Usino Bundi",
            "station": "Bundi",
            "first_name": "Anthony",
            "last_name": "Saro",
            "username": "officer.bundi.01",
            "sevispass_id": "271016",
            "badge_number": "PO-016",
        },
        {
            "district": "Usino Bundi",
            "station": "Bundi",
            "first_name": "Lucy",
            "last_name": "Kora",
            "username": "officer.bundi.02",
            "sevispass_id": "271017",
            "badge_number": "PO-017",
        },
        {
            "district": "Usino Bundi",
            "station": "Bundi",
            "first_name": "Richard",
            "last_name": "Mako",
            "username": "officer.bundi.03",
            "sevispass_id": "271018",
            "badge_number": "PO-018",
        },
        {
            "district": "Usino Bundi",
            "station": "Bundi",
            "first_name": "Sarah",
            "last_name": "Yaro",
            "username": "officer.bundi.04",
            "sevispass_id": "271019",
            "badge_number": "PO-019",
        },
        {
            "district": "Usino Bundi",
            "station": "Bundi",
            "first_name": "Francis",
            "last_name": "Ravu",
            "username": "officer.bundi.05",
            "sevispass_id": "271020",
            "badge_number": "PO-020",
        },

        # =====================================================
        # BOGIA DISTRICT
        # =====================================================

        {
            "district": "Bogia",
            "station": "Bogia",
            "first_name": "Michael",
            "last_name": "Karo",
            "username": "officer.bogia.01",
            "sevispass_id": "271021",
            "badge_number": "PO-021",
        },
        {
            "district": "Bogia",
            "station": "Bogia",
            "first_name": "Mary",
            "last_name": "Wari",
            "username": "officer.bogia.02",
            "sevispass_id": "271022",
            "badge_number": "PO-022",
        },
        {
            "district": "Bogia",
            "station": "Bogia",
            "first_name": "David",
            "last_name": "Namo",
            "username": "officer.bogia.03",
            "sevispass_id": "271023",
            "badge_number": "PO-023",
        },
        {
            "district": "Bogia",
            "station": "Bogia",
            "first_name": "Elizabeth",
            "last_name": "Saro",
            "username": "officer.bogia.04",
            "sevispass_id": "271024",
            "badge_number": "PO-024",
        },
        {
            "district": "Bogia",
            "station": "Bogia",
            "first_name": "William",
            "last_name": "Mera",
            "username": "officer.bogia.05",
            "sevispass_id": "271025",
            "badge_number": "PO-025",
        },

        # =====================================================
        # SUMKAR DISTRICT
        # =====================================================

        {
            "district": "Sumkar",
            "station": "Talidig",
            "first_name": "Christopher",
            "last_name": "Waku",
            "username": "officer.talidig.01",
            "sevispass_id": "271026",
            "badge_number": "PO-026",
        },
        {
            "district": "Sumkar",
            "station": "Talidig",
            "first_name": "Anna",
            "last_name": "Kila",
            "username": "officer.talidig.02",
            "sevispass_id": "271027",
            "badge_number": "PO-027",
        },
        {
            "district": "Sumkar",
            "station": "Talidig",
            "first_name": "Steven",
            "last_name": "Ravu",
            "username": "officer.talidig.03",
            "sevispass_id": "271028",
            "badge_number": "PO-028",
        },
        {
            "district": "Sumkar",
            "station": "Talidig",
            "first_name": "Rose",
            "last_name": "Mako",
            "username": "officer.talidig.04",
            "sevispass_id": "271029",
            "badge_number": "PO-029",
        },
        {
            "district": "Sumkar",
            "station": "Talidig",
            "first_name": "Joseph",
            "last_name": "Kora",
            "username": "officer.talidig.05",
            "sevispass_id": "271030",
            "badge_number": "PO-030",
        },

        {
            "district": "Sumkar",
            "station": "Karkar",
            "first_name": "Brian",
            "last_name": "Yaro",
            "username": "officer.karkar.01",
            "sevispass_id": "271031",
            "badge_number": "PO-031",
        },
        {
            "district": "Sumkar",
            "station": "Karkar",
            "first_name": "Catherine",
            "last_name": "Wama",
            "username": "officer.karkar.02",
            "sevispass_id": "271032",
            "badge_number": "PO-032",
        },
        {
            "district": "Sumkar",
            "station": "Karkar",
            "first_name": "Martin",
            "last_name": "Saki",
            "username": "officer.karkar.03",
            "sevispass_id": "271033",
            "badge_number": "PO-033",
        },
        {
            "district": "Sumkar",
            "station": "Karkar",
            "first_name": "Linda",
            "last_name": "Kewa",
            "username": "officer.karkar.04",
            "sevispass_id": "271034",
            "badge_number": "PO-034",
        },
        {
            "district": "Sumkar",
            "station": "Karkar",
            "first_name": "Paul",
            "last_name": "Nori",
            "username": "officer.karkar.05",
            "sevispass_id": "271035",
            "badge_number": "PO-035",
        },

        {
            "district": "Sumkar",
            "station": "Dilup",
            "first_name": "Andrew",
            "last_name": "Karo",
            "username": "officer.dilup.01",
            "sevispass_id": "271036",
            "badge_number": "PO-036",
        },
        {
            "district": "Sumkar",
            "station": "Dilup",
            "first_name": "Rebecca",
            "last_name": "Saro",
            "username": "officer.dilup.02",
            "sevispass_id": "271037",
            "badge_number": "PO-037",
        },
        {
            "district": "Sumkar",
            "station": "Dilup",
            "first_name": "Matthew",
            "last_name": "Wari",
            "username": "officer.dilup.03",
            "sevispass_id": "271038",
            "badge_number": "PO-038",
        },
        {
            "district": "Sumkar",
            "station": "Dilup",
            "first_name": "Susan",
            "last_name": "Mako",
            "username": "officer.dilup.04",
            "sevispass_id": "271039",
            "badge_number": "PO-039",
        },
        {
            "district": "Sumkar",
            "station": "Dilup",
            "first_name": "Kevin",
            "last_name": "Ravu",
            "username": "officer.dilup.05",
            "sevispass_id": "271040",
            "badge_number": "PO-040",
        },

        {
            "district": "Sumkar",
            "station": "Taur Police Detect",
            "first_name": "Simon",
            "last_name": "Kila",
            "username": "officer.taur.01",
            "sevispass_id": "271041",
            "badge_number": "PO-041",
        },
        {
            "district": "Sumkar",
            "station": "Taur Police Detect",
            "first_name": "Esther",
            "last_name": "Yama",
            "username": "officer.taur.02",
            "sevispass_id": "271042",
            "badge_number": "PO-042",
        },
        {
            "district": "Sumkar",
            "station": "Taur Police Detect",
            "first_name": "Andrew",
            "last_name": "Mera",
            "username": "officer.taur.03",
            "sevispass_id": "271043",
            "badge_number": "PO-043",
        },
        {
            "district": "Sumkar",
            "station": "Taur Police Detect",
            "first_name": "Martha",
            "last_name": "Waku",
            "username": "officer.taur.04",
            "sevispass_id": "271044",
            "badge_number": "PO-044",
        },
        {
            "district": "Sumkar",
            "station": "Taur Police Detect",
            "first_name": "Jonathan",
            "last_name": "Kora",
            "username": "officer.taur.05",
            "sevispass_id": "271045",
            "badge_number": "PO-045",
        },

        # =====================================================
        # RAICOAST DISTRICT
        # =====================================================

        {
            "district": "Raicoast",
            "station": "Saidor",
            "first_name": "Daniel",
            "last_name": "Saki",
            "username": "officer.saidor.01",
            "sevispass_id": "271046",
            "badge_number": "PO-046",
        },
        {
            "district": "Raicoast",
            "station": "Saidor",
            "first_name": "Julia",
            "last_name": "Kewa",
            "username": "officer.saidor.02",
            "sevispass_id": "271047",
            "badge_number": "PO-047",
        },
        {
            "district": "Raicoast",
            "station": "Saidor",
            "first_name": "Francis",
            "last_name": "Wama",
            "username": "officer.saidor.03",
            "sevispass_id": "271048",
            "badge_number": "PO-048",
        },
        {
            "district": "Raicoast",
            "station": "Saidor",
            "first_name": "Naomi",
            "last_name": "Kila",
            "username": "officer.saidor.04",
            "sevispass_id": "271049",
            "badge_number": "PO-049",
        },
        {
            "district": "Raicoast",
            "station": "Saidor",
            "first_name": "Mark",
            "last_name": "Ravu",
            "username": "officer.saidor.05",
            "sevispass_id": "271050",
            "badge_number": "PO-050",
        },

        {
            "district": "Raicoast",
            "station": "Ileg",
            "first_name": "George",
            "last_name": "Namo",
            "username": "officer.ileg.01",
            "sevispass_id": "271051",
            "badge_number": "PO-051",
        },
        {
            "district": "Raicoast",
            "station": "Ileg",
            "first_name": "Angela",
            "last_name": "Mera",
            "username": "officer.ileg.02",
            "sevispass_id": "271052",
            "badge_number": "PO-052",
        },
        {
            "district": "Raicoast",
            "station": "Ileg",
            "first_name": "Richard",
            "last_name": "Wari",
            "username": "officer.ileg.03",
            "sevispass_id": "271053",
            "badge_number": "PO-053",
        },
        {
            "district": "Raicoast",
            "station": "Ileg",
            "first_name": "Dorothy",
            "last_name": "Karo",
            "username": "officer.ileg.04",
            "sevispass_id": "271054",
            "badge_number": "PO-054",
        },
        {
            "district": "Raicoast",
            "station": "Ileg",
            "first_name": "Peter",
            "last_name": "Yama",
            "username": "officer.ileg.05",
            "sevispass_id": "271055",
            "badge_number": "PO-055",
        },

        {
            "district": "Raicoast",
            "station": "Tauta",
            "first_name": "Steven",
            "last_name": "Kila",
            "username": "officer.tauta.01",
            "sevispass_id": "271056",
            "badge_number": "PO-056",
        },
        {
            "district": "Raicoast",
            "station": "Tauta",
            "first_name": "Rebecca",
            "last_name": "Saro",
            "username": "officer.tauta.02",
            "sevispass_id": "271057",
            "badge_number": "PO-057",
        },
        {
            "district": "Raicoast",
            "station": "Tauta",
            "first_name": "Andrew",
            "last_name": "Waku",
            "username": "officer.tauta.03",
            "sevispass_id": "271058",
            "badge_number": "PO-058",
        },
        {
            "district": "Raicoast",
            "station": "Tauta",
            "first_name": "Patricia",
            "last_name": "Mako",
            "username": "officer.tauta.04",
            "sevispass_id": "271059",
            "badge_number": "PO-059",
        },
        {
            "district": "Raicoast",
            "station": "Tauta",
            "first_name": "James",
            "last_name": "Kora",
            "username": "officer.tauta.05",
            "sevispass_id": "271060",
            "badge_number": "PO-060",
        },

        # =====================================================
        # MADANG DISTRICT
        # =====================================================

        {
            "district": "Madang",
            "station": "Jomba",
            "first_name": "William",
            "last_name": "Ravu",
            "username": "officer.jomba.01",
            "sevispass_id": "271061",
            "badge_number": "PO-061",
        },
        {
            "district": "Madang",
            "station": "Jomba",
            "first_name": "Christine",
            "last_name": "Wama",
            "username": "officer.jomba.02",
            "sevispass_id": "271062",
            "badge_number": "PO-062",
        },
        {
            "district": "Madang",
            "station": "Jomba",
            "first_name": "Joseph",
            "last_name": "Kila",
            "username": "officer.jomba.03",
            "sevispass_id": "271063",
            "badge_number": "PO-063",
        },
        {
            "district": "Madang",
            "station": "Jomba",
            "first_name": "Monica",
            "last_name": "Saki",
            "username": "officer.jomba.04",
            "sevispass_id": "271064",
            "badge_number": "PO-064",
        },
        {
            "district": "Madang",
            "station": "Jomba",
            "first_name": "Paul",
            "last_name": "Mera",
            "username": "officer.jomba.05",
            "sevispass_id": "271065",
            "badge_number": "PO-065",
        },

        {
            "district": "Madang",
            "station": "Mawan",
            "first_name": "Martin",
            "last_name": "Kewa",
            "username": "officer.mawan.01",
            "sevispass_id": "271066",
            "badge_number": "PO-066",
        },
        {
            "district": "Madang",
            "station": "Mawan",
            "first_name": "Sarah",
            "last_name": "Namo",
            "username": "officer.mawan.02",
            "sevispass_id": "271067",
            "badge_number": "PO-067",
        },
        {
            "district": "Madang",
            "station": "Mawan",
            "first_name": "Anthony",
            "last_name": "Yaro",
            "username": "officer.mawan.03",
            "sevispass_id": "271068",
            "badge_number": "PO-068",
        },
        {
            "district": "Madang",
            "station": "Mawan",
            "first_name": "Helen",
            "last_name": "Kora",
            "username": "officer.mawan.04",
            "sevispass_id": "271069",
            "badge_number": "PO-069",
        },
        {
            "district": "Madang",
            "station": "Mawan",
            "first_name": "Francis",
            "last_name": "Waku",
            "username": "officer.mawan.05",
            "sevispass_id": "271070",
            "badge_number": "PO-070",
        },

        {
            "district": "Madang",
            "station": "Town",
            "first_name": "Robert",
            "last_name": "Saro",
            "username": "officer.town.01",
            "sevispass_id": "271071",
            "badge_number": "PO-071",
        },
        {
            "district": "Madang",
            "station": "Town",
            "first_name": "Grace",
            "last_name": "Mako",
            "username": "officer.town.02",
            "sevispass_id": "271072",
            "badge_number": "PO-072",
        },
        {
            "district": "Madang",
            "station": "Town",
            "first_name": "Daniel",
            "last_name": "Karo",
            "username": "officer.town.03",
            "sevispass_id": "271073",
            "badge_number": "PO-073",
        },
        {
            "district": "Madang",
            "station": "Town",
            "first_name": "Elizabeth",
            "last_name": "Ravu",
            "username": "officer.town.04",
            "sevispass_id": "271074",
            "badge_number": "PO-074",
        },
        {
            "district": "Madang",
            "station": "Town",
            "first_name": "Michael",
            "last_name": "Wari",
            "username": "officer.town.05",
            "sevispass_id": "271075",
            "badge_number": "PO-075",
        },

        # =====================================================
        # MIDDLE RAMU DISTRICT
        # =====================================================

        {
            "district": "Middle Ramu",
            "station": "Nodobu",
            "first_name": "Jonathan",
            "last_name": "Kila",
            "username": "officer.nodobu.01",
            "sevispass_id": "271076",
            "badge_number": "PO-076",
        },
        {
            "district": "Middle Ramu",
            "station": "Nodobu",
            "first_name": "Mary",
            "last_name": "Saro",
            "username": "officer.nodobu.02",
            "sevispass_id": "271077",
            "badge_number": "PO-077",
        },
        {
            "district": "Middle Ramu",
            "station": "Nodobu",
            "first_name": "George",
            "last_name": "Kewa",
            "username": "officer.nodobu.03",
            "sevispass_id": "271078",
            "badge_number": "PO-078",
        },
        {
            "district": "Middle Ramu",
            "station": "Nodobu",
            "first_name": "Rachel",
            "last_name": "Wama",
            "username": "officer.nodobu.04",
            "sevispass_id": "271079",
            "badge_number": "PO-079",
        },
        {
            "district": "Middle Ramu",
            "station": "Nodobu",
            "first_name": "Samuel",
            "last_name": "Mera",
            "username": "officer.nodobu.05",
            "sevispass_id": "271080",
            "badge_number": "PO-080",
        },

        {
            "district": "Middle Ramu",
            "station": "Aiome",
            "first_name": "Kevin",
            "last_name": "Yaro",
            "username": "officer.aiome.01",
            "sevispass_id": "271081",
            "badge_number": "PO-081",
        },
        {
            "district": "Middle Ramu",
            "station": "Aiome",
            "first_name": "Susan",
            "last_name": "Kora",
            "username": "officer.aiome.02",
            "sevispass_id": "271082",
            "badge_number": "PO-082",
        },
        {
            "district": "Middle Ramu",
            "station": "Aiome",
            "first_name": "Brian",
            "last_name": "Ravu",
            "username": "officer.aiome.03",
            "sevispass_id": "271083",
            "badge_number": "PO-083",
        },
        {
            "district": "Middle Ramu",
            "station": "Aiome",
            "first_name": "Esther",
            "last_name": "Namo",
            "username": "officer.aiome.04",
            "sevispass_id": "271084",
            "badge_number": "PO-084",
        },
        {
            "district": "Middle Ramu",
            "station": "Aiome",
            "first_name": "Matthew",
            "last_name": "Waku",
            "username": "officer.aiome.05",
            "sevispass_id": "271085",
            "badge_number": "PO-085",
        },

        {
            "district": "Middle Ramu",
            "station": "Simbai",
            "first_name": "David",
            "last_name": "Karo",
            "username": "officer.simbai.01",
            "sevispass_id": "271086",
            "badge_number": "PO-086",
        },
        {
            "district": "Middle Ramu",
            "station": "Simbai",
            "first_name": "Lucy",
            "last_name": "Wari",
            "username": "officer.simbai.02",
            "sevispass_id": "271087",
            "badge_number": "PO-087",
        },
        {
            "district": "Middle Ramu",
            "station": "Simbai",
            "first_name": "Patrick",
            "last_name": "Saki",
            "username": "officer.simbai.03",
            "sevispass_id": "271088",
            "badge_number": "PO-088",
        },
        {
            "district": "Middle Ramu",
            "station": "Simbai",
            "first_name": "Angela",
            "last_name": "Mako",
            "username": "officer.simbai.04",
            "sevispass_id": "271089",
            "badge_number": "PO-089",
        },
        {
            "district": "Middle Ramu",
            "station": "Simbai",
            "first_name": "Richard",
            "last_name": "Yama",
            "username": "officer.simbai.05",
            "sevispass_id": "271090",
            "badge_number": "PO-090",
        },
    ]

    # =========================================================
    # COMMAND
    # =========================================================

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write("")
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "BlueShield Police Officer Setup"
            )
        )

        self.stdout.write(
            "Creating/updating 90 demo Police Officer accounts..."
        )
        self.stdout.write("")

        created_count = 0
        updated_count = 0

        for data in self.OFFICERS:

            district_name = data["district"]
            station_name = data["station"]

            # -------------------------------------------------
            # FIND DISTRICT
            # -------------------------------------------------

            try:
                district = District.objects.get(
                    name__iexact=district_name
                )
            except District.DoesNotExist:
                raise CommandError(
                    f"District not found: {district_name}"
                )

            # -------------------------------------------------
            # FIND STATION
            # -------------------------------------------------

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
                        f"Station '{station_name}' exists, but "
                        f"belongs to '{other_station.district.name}', "
                        f"not '{district_name}'."
                    )

                raise CommandError(
                    f"Police station not found: "
                    f"{station_name} ({district_name})"
                )

            # -------------------------------------------------
            # FIND EXISTING USER
            #
            # Search by SevisPass first so duplicate IDs
            # cannot be created.
            # -------------------------------------------------

            user = User.objects.filter(
                sevispass_id=data["sevispass_id"]
            ).first()

            if user is None:
                user = User.objects.filter(
                    username=data["username"]
                ).first()

            created = False

            # -------------------------------------------------
            # CREATE USER
            # -------------------------------------------------

            if user is None:

                user = User(
                    username=data["username"],
                    first_name=data["first_name"],
                    last_name=data["last_name"],
                    role="OFFICER",
                    badge_number=data["badge_number"],
                    rank="Police Officer",
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

            # -------------------------------------------------
            # UPDATE EXISTING USER
            # -------------------------------------------------

            else:

                user.first_name = data["first_name"]
                user.last_name = data["last_name"]

                user.role = "OFFICER"

                user.badge_number = data["badge_number"]
                user.rank = "Police Officer"

                user.district = district
                user.station = station

                user.sevispass_id = data["sevispass_id"]

                user.is_active = True

                # Keep SevisPass verification controlled by
                # the actual verification process.
                user.sevispass_verified = False
                user.sevispass_verified_at = None

                user.save()

                updated_count += 1

            # -------------------------------------------------
            # DISPLAY RESULT
            # -------------------------------------------------

            full_name = (
                f"{data['first_name']} "
                f"{data['last_name']}"
            )

            action = "CREATED" if created else "UPDATED"

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
                "Police Officer setup completed successfully."
            )
        )

        self.stdout.write(
            f"Created: {created_count}"
        )

        self.stdout.write(
            f"Updated: {updated_count}"
        )

        self.stdout.write(
            f"Total processed: {len(self.OFFICERS)}"
        )

        self.stdout.write(
            self.style.SUCCESS(
                "=============================================="
            )
        )

        self.stdout.write("")

        self.stdout.write(
            "Each police station now has 5 assigned demo officers."
        )

        self.stdout.write(
            "SevisPass verification remains FALSE."
        )

        self.stdout.write(
            "New accounts use the local demo password:"
        )

        self.stdout.write(
            "BlueShieldDemo123!"
        )

        self.stdout.write("")
