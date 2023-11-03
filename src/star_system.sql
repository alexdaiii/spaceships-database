CREATE TABLE star_system (
    star_system_id INTEGER PRIMARY KEY,
    star_system_name VARCHAR NOT NULL,
    system_trade_value INTEGER NOT NULL,
    system_energy_value INTEGER NOT NULL,
    system_minerals_value INTEGER NOT NULL,
    system_research_value INTEGER NOT NULL,
    empire_owner INTEGER NOT NULL,

    FOREIGN KEY (empire_owner) REFERENCES empire (empire_id)
);

CREATE TABLE patrolled_systems (
    star_system_id INTEGER NOT NULL,
    fleet_id INTEGER NOT NULL,
    last_patrol_date DATE NOT NULL,

    FOREIGN KEY (star_system_id) REFERENCES star_system (star_system_id),
    FOREIGN KEY (fleet_id) REFERENCES fleet (fleet_id),
    PRIMARY KEY (star_system_id, fleet_id)
);

CREATE TABLE planet_biome (
    biome_id INTEGER PRIMARY KEY,
    biome_name VARCHAR NOT NULL
);

CREATE TABLE planet (
    planet_id INTEGER PRIMARY KEY,
    planet_name VARCHAR NOT NULL,
    planet_size INTEGER NOT NULL,
    star_system_id INTEGER NOT NULL,
    biome_id INTEGER NOT NULL,

    FOREIGN KEY (star_system_id) REFERENCES star_system (star_system_id)
);