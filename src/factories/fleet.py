from src.factories.utils import get_location, STARTING_ID, load_file
from src.models import Fleet
from faker import Faker


def create_fleets(
    fake: Faker,
    *,
    max_num_fleets: int,
    num_empires: int,
):
    location = get_location()
    fleet_prefix = "fleets_prefix.txt"
    fleet_suffix = "fleets_suffix.txt"

    docked_percent = 70

    fleets = []

    for i in range(STARTING_ID, num_empires + 1):
        num_fleets = fake.random_int(min=0, max=max_num_fleets)

        fleets.extend(
            [
                Fleet(
                    fleet_id=j,
                    fleet_name=f"{prefix} {suffix}",
                    fleet_empire_owner=i,
                    fleet_cloak_strength=fake.random_int(min=0, max=100),
                    fleet_is_docked=fake.random_int(min=0, max=100)
                    < docked_percent,
                )
                for j, (prefix, suffix) in enumerate(
                    zip(
                        fake.random_elements(
                            elements=load_file(
                                location=location,
                                filename=fleet_prefix,
                            ),
                            length=num_fleets,
                            unique=True,
                        ),
                        fake.random_elements(
                            elements=load_file(
                                location=location,
                                filename=fleet_suffix,
                            ),
                            length=num_fleets,
                            unique=True,
                        ),
                    ),
                    start=len(fleets) + 1,
                )
            ]
        )

    return fleets


__all__ = [
    "create_fleets",
]
