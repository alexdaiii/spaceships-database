import math

import colorful as cf
import networkx as nx
import numpy as np
from faker import Faker
from sqlalchemy import Engine, insert

from src.database.db import get_session
from src.models.star_system import StarSystem, StarType
from src.util import (
    MAX_NUM_STARS,
    MIN_NUM_STARS,
    get_location,
    get_m_and_b,
    get_yhat,
)

from src.settings import get_settings
from .celestial_bodies_util import stars_type_df
from .utils import load_file


def load_star_prefix():
    star_prefix = "assets/stars_prefix.txt"

    return load_file(get_location(), star_prefix)


def create_star_types(
    engine: Engine,
):
    print(cf.yellow("Adding star types..."))

    with get_session(engine) as session:
        session.execute(
            insert(StarType), stars_type_df().reset_index().to_dict("records")
        )


def create_stars(
    *,
    fake: Faker,
    rng: np.random.Generator,
    engine: Engine,
    num_stars: int,
):
    print(cf.yellow("Generating stars..."))

    create_star_types(engine)

    star_base_names = fake.words(
        nb=min(num_stars // 10, len(load_star_prefix()), 1000),
        unique=True,
        ext_word_list=load_star_prefix(),
    )

    page_size = len(star_base_names)
    num_pages = math.ceil(num_stars / page_size)

    is_chokepoint_p = get_is_chokepoint_p(rng)

    for i in range(num_pages):
        if i == num_pages - 1 and num_stars % page_size != 0:
            page_size = num_stars % page_size

        add_stars(
            engine=engine,
            rng=rng,
            i=i,
            star_base_names=star_base_names,
            page_size=page_size,
            is_chokepoint_p=is_chokepoint_p,
        )


def add_stars(
    *,
    engine: Engine,
    rng: np.random.Generator,
    i: int,
    star_base_names: list[str],
    page_size: int,
    is_chokepoint_p: float,
):
    star_ids = stars_type_df().index
    star_id_weights = stars_type_df()["star_type_weight_pct"]

    sep = 50

    with get_session(engine) as session:
        session.execute(
            insert(StarSystem),
            [
                {
                    "star_system_name": f"{star_base_name}-{suffix}",
                    "star_type_id": star_type_id,
                    "system_is_choke_point": is_chokepoint,
                }
                for star_base_name, star_type_id, suffix, is_chokepoint in zip(
                    star_base_names,
                    rng.choice(
                        star_ids,
                        size=page_size,
                        p=star_id_weights,
                        replace=True,
                    ).tolist(),
                    rng.integers(
                        size=page_size, low=i * sep + 1, high=i * sep + sep
                    ),
                    rng.binomial(
                        1,
                        p=is_chokepoint_p,
                        size=page_size,
                    ).astype(bool),
                )
            ],
        )


def connect_graph(g: nx.Graph):
    while not nx.is_connected(g):
        # get the connected components
        connected_components = list(nx.connected_components(g))
        # get the nodes in the first component
        nodes = list(connected_components[0])
        # get the nodes in the second component
        nodes2 = list(connected_components[1])
        # add an edge between the two nodes
        g.add_edge(nodes[0], nodes2[0])


def generate_clusters(rng: np.random.Generator, n_clusters: int):
    print("Generating clusters...")

    nodes_per_cluster = 12
    clusters = [
        nx.fast_gnp_random_graph(nodes_per_cluster, p, seed=rng)
        for p in rng.normal(0.25, 0.005, n_clusters)
    ]
    # relabel the nodes
    clusters = [
        nx.relabel_nodes(g, {n: f"node_{i}_{n}" for n in g.nodes})
        for i, g in enumerate(clusters)
    ]
    # make sure each cluster is connected
    for g in clusters:
        connect_graph(g)

    return clusters


def connect_clusters(
    combined: nx.Graph, rng: np.random.Generator, n_clusters: int
):
    hyperlanes_between_cluster = rng.poisson(
        get_settings().hyperlane_density + 1, n_clusters
    )
    connected_components = list(nx.connected_components(combined))
    for i, (cc, n_hyper) in enumerate(
        zip(connected_components, hyperlanes_between_cluster)
    ):
        j = i + 1 if i + 1 < len(connected_components) else 0

        # make sure don't choose too many nodes
        cc2 = connected_components[j]
        n_conn = min(len(cc), len(cc2), n_hyper)

        # randomly choose n_hyper nodes from each cluster
        nodes1 = rng.choice(list(cc), n_conn, replace=False)
        nodes2 = rng.choice(list(cc2), n_conn, replace=False)

        # add edges between the two nodes
        for n1, n2 in zip(nodes1, nodes2):
            combined.add_edge(n1, n2)

    connect_graph(combined)


def generate_hyperlane_map(rng: np.random.Generator, n_clusters: int):
    # n_stars is how many clusters to simulate
    print("Generating galaxy map...")
    # mean number of edges to draw between clusters

    combined = nx.compose_all(generate_clusters(rng, n_clusters))
    connect_clusters(combined, rng, n_clusters)

    return combined


def get_is_chokepoint_p(rng: np.random.Generator):
    n_clusters = int(
        get_yhat(
            get_settings().num_stars,
            *get_m_and_b(MIN_NUM_STARS, 1000, MAX_NUM_STARS, 2000),
        )
    )

    g = generate_hyperlane_map(rng, n_clusters)

    # get the pct of num verticies with degree 1
    return sum([1 for v in g.nodes if g.degree[v] == 1]) / len(g.nodes)


__all__ = [
    "create_stars",
]
