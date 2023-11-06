CREATE TABLE crew (
    crew_id INTEGER PRIMARY KEY,
    crew_name VARCHAR NOT NULL,
    spaceship_id INTEGER NOT NULL,
    base_command_points INTEGER NOT NULL,
    reports_to INTEGER NOT NULL,
    birth_date DATE NOT NULL,
    hire_date DATE NOT NULL,
    planet_of_birth_id INTEGER NOT NULL,

    FOREIGN KEY (spaceship_id) REFERENCES spaceship (spaceship_id),
    FOREIGN KEY (reports_to) REFERENCES crew (crew_id),
    FOREIGN KEY (planet_of_birth_id) REFERENCES planet (planet_id)
);

CREATE TABLE crew_friend (
    crew_id INTEGER NOT NULL,
    friend_id INTEGER NOT NULL,

    FOREIGN KEY (crew_id) REFERENCES crew (crew_id),
    FOREIGN KEY (friend_id) REFERENCES crew (crew_id),
    PRIMARY KEY (crew_id, friend_id)
);