CREATE SCHEMA IF NOT EXISTS public;
CREATE SCHEMA IF NOT EXISTS content;
ALTER ROLE "app" SET search_path TO content, public;

CREATE TABLE IF NOT EXISTS public.users_user (
    id uuid NOT NULL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    last_login timestamp with time zone NULL,
    is_active boolean NOT NULL,
    is_admin boolean NOT NULL,
    first_name TEXT NULL,
    last_name TEXT NULL,
    roles TEXT[] NOT NULL,
    is_staff boolean NOT NULL);

CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date timestamp with time zone,
    rating FLOAT,
    type TEXT NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    full_name TEXT NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL REFERENCES content.film_work (id) ON DELETE CASCADE,
    person_id uuid NOT NULL REFERENCES content.person (id) ON DELETE CASCADE,
    role TEXT,
    created timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL REFERENCES content.film_work (id) ON DELETE CASCADE,
    genre_id uuid NOT NULL REFERENCES content.genre (id) ON DELETE CASCADE,
    created timestamp with time zone
);

CREATE INDEX IF NOT EXISTS film_work_creation_date_idx ON content.film_work(creation_date);

CREATE UNIQUE INDEX IF NOT EXISTS genre_name_idx ON content.genre (name);

CREATE UNIQUE INDEX IF NOT EXISTS person_full_name_idx ON content.person (full_name);

CREATE UNIQUE INDEX IF NOT EXISTS film_work_genre_idx ON content.genre_film_work (film_work_id, genre_id);

CREATE UNIQUE INDEX IF NOT EXISTS film_work_person_role_idx ON content.person_film_work (film_work_id, person_id, role);
