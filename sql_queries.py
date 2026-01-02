
# DROP TABLES
songplay_table_drop = "DROP TABLE IF EXISTS songplays"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES

songplay_table_create = ("""
CREATE TABLE IF NOT EXISTS songplays (
    songplay_id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TEXT,
    user_id INTEGER,
    level TEXT NOT NULL,
    song_id TEXT,
    artist_id TEXT,
    session_id INTEGER NOT NULL,
    location TEXT,
    user_agent TEXT,
    FOREIGN KEY (start_time) REFERENCES time(start_time),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (song_id) REFERENCES songs(song_id),
    FOREIGN KEY (artist_id) REFERENCES artists(artist_id)
);
""")

user_table_create = ("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    gender TEXT,
    level TEXT NOT NULL
);
""")

song_table_create = ("""
CREATE TABLE IF NOT EXISTS songs (
    song_id TEXT PRIMARY KEY,
    title TEXT,
    artist_id TEXT,
    year INTEGER CHECK (year >= 0),
    duration REAL,
    FOREIGN KEY (artist_id) REFERENCES artists(artist_id)
);
""")

artist_table_create = ("""
CREATE TABLE IF NOT EXISTS artists (
    artist_id TEXT PRIMARY KEY,
    name TEXT,
    location TEXT,
    latitude REAL,
    longitude REAL
);
""")

time_table_create = ("""CREATE TABLE IF NOT EXISTS  time(
	start_time  TIMESTAMP CONSTRAINT time_pk PRIMARY KEY,
	hour INT NOT NULL CHECK (hour >= 0),
	day INT NOT NULL CHECK (day >= 0),
	week INT NOT NULL CHECK (week >= 0),
	month INT NOT NULL CHECK (month >= 0),
	year INT NOT NULL CHECK (year >= 0),
	weekday VARCHAR NOT NULL
)""")

# INSERT RECORDS

songplay_table_insert = ("""
INSERT INTO songplays (
    start_time, user_id, level, song_id, artist_id,
    session_id, location, user_agent
) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
""")


# Updating the user level on conflict
user_table_insert = ("""
INSERT INTO users (user_id, first_name, last_name, gender, level)
VALUES (?, ?, ?, ?, ?)
ON CONFLICT(user_id) DO UPDATE SET
    level = excluded.level;
""")

song_table_insert = ("""
INSERT INTO songs (song_id, title, artist_id, year, duration)
VALUES (?, ?, ?, ?, ?)
ON CONFLICT(song_id) DO NOTHING;
""")


# Artist location, latitude and longitude might change and need to be updated.
artist_table_insert = ("""
INSERT INTO artists (artist_id, name, location, latitude, longitude)
VALUES (?, ?, ?, ?, ?)
ON CONFLICT(artist_id) DO UPDATE SET
    location = excluded.location,
    latitude = excluded.latitude,
    longitude = excluded.longitude;
""")

time_table_insert = ("""
INSERT INTO time (start_time, hour, day, week, month, year, weekday)
VALUES (?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(start_time) DO NOTHING;
""")

# FIND SONGS

song_select = ("""
SELECT songs.song_id, artists.artist_id
FROM songs
JOIN artists ON songs.artist_id = artists.artist_id
WHERE songs.title = ?
  AND artists.name = ?
  AND songs.duration = ?;
""")

# QUERY LISTS

create_table_queries = [user_table_create, artist_table_create, song_table_create, time_table_create, songplay_table_create]
drop_table_queries = [songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]

