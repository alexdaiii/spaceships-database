CREATE TABLE empire_authority (
    empire_authority_id INTEGER PRIMARY KEY,
    empire_authority_name VARCHAR NOT NULL
);

CREATE TABLE empire_ethic (
    empire_ethic_id INTEGER PRIMARY KEY,
    empire_ethic_name VARCHAR NOT NULL
);

CREATE TABLE empire (
    empire_id INTEGER PRIMARY KEY,
    empire_name VARCHAR NOT NULL,
    empire_authority_id INTEGER NOT NULL,

    FOREIGN KEY (empire_authority_id) REFERENCES empire_authority (empire_authority_id)
);

CREATE TABLE empire_to_ethic (
    empire_id INTEGER NOT NULL,
    empire_ethic_id INTEGER NOT NULL,

    FOREIGN KEY (empire_id) REFERENCES empire (empire_id),
    PRIMARY KEY (empire_id, empire_ethic_id)
);

