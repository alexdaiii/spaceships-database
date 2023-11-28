import colorful as cf
import numpy as np
import pandas as pd
from sqlalchemy import Engine, insert

from src.database.db import get_session
from src.models import Fleet
from src.util import get_location

from .utils.empires_util import empires_info
from .utils.util import load_file


def calculate_num_fleets(df: pd.DataFrame):
    # bucket each empire by the resources they have - 10 buckets / resource
    n_bins = {
        "total_energy": 5,
        "total_minerals": 12,
        "total_research": 3,
        "total_trade": 10,
    }

    def resource_rank(col: str, bins):
        return pd.cut(
            df[col],
            bins=bins,
            labels=range(1, bins + 1),
        ).astype(int)

    # max total fleets is 30 (sum of all bins)
    df["total_fleets"] = (
        resource_rank("total_energy", bins=n_bins["total_energy"])
        + resource_rank("total_minerals", bins=n_bins["total_minerals"])
        + resource_rank("total_research", bins=n_bins["total_research"])
        + resource_rank("total_trade", bins=n_bins["total_trade"])
    ) // 2

    # max fleet size dependent on tech level and civics (gov_efficiency_bonus)
    df["max_fleet_size"] = (
        20
        + resource_rank("total_research", bins=6) * 20
        + 10 * df["gov_efficiency_bonus"]
    ) // 10


def create_fleets(rng: np.random.Generator, engine: Engine):
    location = get_location()
    fleet_prefix = "assets/fleets_prefix.txt"
    fleet_suffix = "assets/fleets_suffix.txt"

    docked_percent = 70

    min_fleets = empires_info(engine).total_fleets.min()

    with get_session(engine) as session:
        for _, empire in empires_info(engine).iterrows():
            fleet_cloak_mu = 1 / (empire.total_fleets - min_fleets + 1) * 100

            session.execute(
                insert(Fleet),
                [
                    {
                        "fleet_name": f"{prefix} {suffix}",
                        "fleet_empire_owner": empire.empire_id,
                        "fleet_is_docked": docked < docked_percent,
                        # inversely proportional to the number of fleets
                        "fleet_cloak_strength": int(fleet_cloak),
                    }
                    for prefix, suffix, docked, fleet_cloak in zip(
                        rng.choice(
                            load_file(
                                location=location, filename=fleet_prefix
                            ),
                            size=empire.total_fleets,
                        ),
                        rng.choice(
                            load_file(
                                location=location, filename=fleet_suffix
                            ),
                            size=empire.total_fleets,
                        ),
                        rng.integers(0, 100, empire.total_fleets),
                        rng.normal(
                            fleet_cloak_mu,
                            5,
                            empire.total_fleets,
                        ).clip(0, 100),
                    )
                ],
            )


def add_fleets(rng: np.random.Generator, engine: Engine):
    print(cf.yellow("Adding empire fleets"))

    empires = empires_info(engine)
    calculate_num_fleets(empires)

    create_fleets(rng=rng, engine=engine)


__all__ = ["add_fleets"]
