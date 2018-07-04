CREATE TABLE cities (
    id serial primary key,
    name text NOT NULL
);

CREATE TABLE phones (
    id serial primary key,
    name text NOT NULL,
    surname text NOT NULL,
    phone_number text NOT NULL,
    city_id serial REFERENCES cities (id)
);