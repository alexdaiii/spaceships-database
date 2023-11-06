CREATE TABLE fleet (
    fleet_id INTEGER PRIMARY KEY,
    fleet_name VARCHAR NOT NULL,
    empire_id INTEGER NOT NULL,

    FOREIGN KEY (empire_id) REFERENCES empire (empire_id)
);