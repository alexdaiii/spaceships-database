CREATE TABLE spaceship_classification (
    spaceship_classification_id INTEGER PRIMARY KEY,
    spaceship_classification_name VARCHAR NOT NULL,
);

CREATE TABLE spaceship (
    spaceship_id INTEGER PRIMARY KEY,
    spaceship_name VARCHAR NOT NULL,
    spaceship_fleet_id INTEGER NOT NULL,
    spaceship_classification_id INTEGER NOT NULL,
    spaceship_experience INTEGER NOT NULL,

    FOREIGN KEY (spaceship_fleet_id) REFERENCES fleet (fleet_id),
    FOREIGN KEY (spaceship_classification_id) REFERENCES spaceship_classification (spaceship_classification_id)
);

CREATE TABLE spaceship_module (
    spaceship_module_id INTEGER PRIMARY KEY,
    spaceship_module_name VARCHAR NOT NULL,
    spaceship_module_weight INTEGER NOT NULL,
    spaceship_module_power INTEGER NOT NULL,
    spaceship_module_trade_protection INTEGER NOT NULL
);


CREATE TABLE spaceship_to_module (
    spaceship_id INTEGER NOT NULL,
    spaceship_module_id INTEGER NOT NULL,

    FOREIGN KEY (spaceship_id) REFERENCES spaceship (spaceship_id),
    PRIMARY KEY (spaceship_id, spaceship_module_id)
);

CREATE TABLE spaceship_rank (
    spaceship_rank_id INTEGER PRIMARY KEY,
    spaceship_rank_name VARCHAR NOT NULL,
    spaceship_min_experience INTEGER NOT NULL,
    spaceship_max_experience INTEGER NOT NULL
);

CREATE TABLE spaceship_weight_class (
    spaceship_weight_class_id INTEGER PRIMARY KEY,
    spaceship_weight_class_name VARCHAR NOT NULL,
    spaceship_min_weight INTEGER NOT NULL,
    spaceship_max_weight INTEGER NOT NULL,
    spaceship_command_cost INTEGER NOT NULL
);