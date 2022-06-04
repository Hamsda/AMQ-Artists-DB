"""
Convert the mapping in JSON generated by process_artists scripts to an SQL database for production use
"""


import sqlite3
import json
from pathlib import Path

database = Path("../../app/data/Enhanced-AMQ-Database.db")
song_database_path = Path("../../app/data/expand_mapping.json")
artist_database_path = Path("../../app/data/artist_mapping.json")

with open(song_database_path, encoding="utf-8") as json_file:
    song_database = json.load(json_file)
with open(artist_database_path, encoding="utf-8") as json_file:
    artist_database = json.load(json_file)


RESET_DB_SQL = """
PRAGMA foreign_keys = 0;
DROP TABLE IF EXISTS animes;
DROP TABLE IF EXISTS artist_alt_names;
DROP TABLE IF EXISTS artists;
DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS link_artist_group;
DROP TABLE IF EXISTS link_song_arranger;
DROP TABLE IF EXISTS link_song_artist;
DROP TABLE IF EXISTS link_song_composer;
DROP TABLE IF EXISTS link_anime_genre;
DROP TABLE IF EXISTS link_anime_tag;
DROP TABLE IF EXISTS songs;
PRAGMA foreign_keys = 1;

CREATE TABLE animes (
    "annId" INTEGER NOT NULL PRIMARY KEY,
    "animeExpandName" VARCHAR(255) NOT NULL, 
    "animeENName" VARCHAR (255),
    "animeJPName" VARCHAR (255),
    "animeVintage" VARCHAR (255),
    "animeType" VARCHAR (255)
);

CREATE TABLE songs (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    "annSongId" INTEGER,
    "annId" INTEGER NOT NULL,
    "songType" INTEGER NOT NULL,
    "songNumber" INTEGER NOT NULL,
    "songName" VARCHAR(255) NOT NULL,
    "songArtist" VARCHAR(255) NOT NULL,
    "songDifficulty" FLOAT,
    "HQ" VARCHAR(255),
    "MQ" VARCHAR(255),
    "audio" VARCHAR(255),
    FOREIGN KEY ("annId")
        REFERENCES animes ("annId")
);

CREATE TABLE artists (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" VARCHAR(255) NOT NULL,
    "vocalist" BIT NOT NULL,
    "composer" BIT NOT NULL
);

CREATE TABLE groups (
    "artist_id" INTEGER NOT NULL,
    "alt_config_id" INTEGER NOT NULL,
    FOREIGN KEY ("artist_id")
        REFERENCES artists ("id"),
    PRIMARY KEY (artist_id, alt_config_id)
);

CREATE TABLE artist_alt_names (
    "artist_id" INTEGER NOT NULL,
    "alt_name" VARCHAR(255) NOT NULL,
    FOREIGN KEY ("artist_id")
        REFERENCES artist ("id"),
    PRIMARY KEY (artist_id, alt_name)
);

CREATE TABLE link_song_artist (
    "song_id" INTEGER NOT NULL,
    "artist_id" INTEGER NOT NULL,
    "artist_alt_members_id" INTEGER NOT NULL,
    FOREIGN KEY ("song_id")
        REFERENCES songs ("id"),
    FOREIGN KEY ("artist_id")
        REFERENCES artists ("id"),
    FOREIGN KEY ("artist_alt_members_id")
        REFERENCES artists ("alt_members_id"),
    PRIMARY KEY (song_id, artist_id, artist_alt_members_id)
);

CREATE TABLE link_song_composer (
    "song_id" INTEGER NOT NULL,
    "composer_id" INTEGER NOT NULL,
    FOREIGN KEY ("song_id")
        REFERENCES songs ("id"),
    FOREIGN KEY ("composer_id")
        REFERENCES artists ("id"),
    PRIMARY KEY (song_id, composer_id)
);

CREATE TABLE link_song_arranger (
    "song_id" INTEGER NOT NULL,
    "arranger_id" INTEGER NOT NULL,
    FOREIGN KEY ("song_id")
        REFERENCES songs ("id"),
    FOREIGN KEY ("arranger_id")
        REFERENCES artists ("id"),
    PRIMARY KEY (song_id, arranger_id)
);

create TABLE link_artist_group (
    "group_id" INTEGER NOT NULL,
    "group_alt_config_id" INTEGER NOT NULL,
    "artist_id" INTEGER NOT NULL,
    FOREIGN KEY ("artist_id")
        REFERENCES artists ("id"),
    FOREIGN KEY ("group_id")
        REFERENCES groups ("artist_id"),
    FOREIGN KEY ("group_alt_config_id")
        REFERENCES groups ("alt_config_id"),
    PRIMARY KEY (artist_id, group_id, group_alt_config_id)
);


create TABLE link_anime_genre (
    "annId" INTEGER NOT NULL,
    "genre" VARCHAR(255),
    FOREIGN KEY ("annId")
        REFERENCES animes ("annId"),
    PRIMARY KEY (annId, genre)
);


create TABLE link_anime_tag (
    "annId" INTEGER NOT NULL,
    "tag" VARCHAR(255),
    FOREIGN KEY ("annId")
        REFERENCES animes ("annId"),
    PRIMARY KEY (annId, tag)
);
"""


def run_sql_command(cursor, sql_command, data=None):

    """
    Run the SQL command with nice looking print when failed (no)
    """

    try:
        if data is not None:
            cursor.execute(sql_command, data)
        else:
            cursor.execute(sql_command)

        record = cursor.fetchall()

        return record

    except sqlite3.Error as error:

        if data is not None:
            for param in data:
                if type(param) == str:
                    sql_command = sql_command.replace("?", '"' + str(param) + '"', 1)
                else:
                    sql_command = sql_command.replace("?", str(param), 1)

        print(
            "\nError while running this command: \n",
            sql_command,
            "\n",
            error,
            "\nData: ",
            data,
            "\n",
        )
        return None


def insert_new_artist(cursor, name, is_vocalist, is_composer):

    """
    Insert a new artist in the database
    """

    sql_insert_artist = "INSERT INTO artists(name, vocalist, composer) VALUES(?, ?, ?);"

    run_sql_command(cursor, sql_insert_artist, [name, is_vocalist, is_composer])

    return cursor.lastrowid


def insert_new_group(cursor, artist_id, set_id):

    """
    Add a new group configuration
    """

    command = "INSERT INTO groups(artist_id, alt_config_id) VALUES(?, ?);"
    run_sql_command(cursor, command, [artist_id, set_id])


def insert_artist_alt_names(cursor, id, names):

    """
    Insert all alternative names corresponding to a single artist
    """

    for name in names:

        sql_insert_artist_name = (
            "INSERT INTO artist_alt_names(artist_id, alt_name) VALUES(?, ?);"
        )

        run_sql_command(cursor, sql_insert_artist_name, (id, name))


def add_artist_to_group(cursor, artist_id, group_id, group_alt_id):

    """
    Add an artist to a group
    """

    sql_add_artist_to_group = "INSERT INTO link_artist_group(artist_id, group_id, group_alt_config_id) VALUES(?, ?, ?)"

    run_sql_command(
        cursor, sql_add_artist_to_group, (artist_id, group_id, group_alt_id)
    )


def get_anime_ID(cursor, animeExpandName, animeJPName):

    """
    Get the first anime it finds that matches the provided parameters
    """

    sql_get_anime_ID = "SELECT annId WHERE animeExpandName = ? and animeJPName = ?;"

    anime_id = run_sql_command(cursor, sql_get_anime_ID, (animeExpandName, animeJPName))
    if anime_id is not None and len(anime_id) > 0:
        return anime_id[0][0]
    return None


def insert_anime(
    cursor, annId, animeExpandName, animeENName, animeJPName, animeVintage, animeType
):

    """
    Insert a new anime in the database
    """

    sql_insert_anime = "INSERT INTO animes(annId, animeExpandName, animeENName, animeJPName, animeVintage, animeType) VALUES(?, ?, ?, ?, ?, ?);"

    run_sql_command(
        cursor,
        sql_insert_anime,
        (annId, animeExpandName, animeENName, animeJPName, animeVintage, animeType),
    )


def insert_song(
    cursor,
    annSongId,
    annId,
    songType,
    songNumber,
    songName,
    songArtist,
    songDifficulty,
    HQ,
    MQ,
    audio,
):

    """
    Insert a new song in the database and return the newly created song ID
    """

    sql_insert_song = "INSERT INTO songs(annSongId, annId, songType, songNumber, songName, songArtist, songDifficulty, HQ, MQ, audio) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"

    run_sql_command(
        cursor,
        sql_insert_song,
        (
            annSongId,
            annId,
            songType,
            songNumber,
            songName,
            songArtist,
            songDifficulty,
            HQ,
            MQ,
            audio,
        ),
    )

    return cursor.lastrowid


def link_song_artist(cursor, song_id, artist_id, artist_alt_id):

    """
    Add a new link between an song and an artist in the table
    """

    sql_link_song_artist = "INSERT INTO link_song_artist(song_id, artist_id, artist_alt_members_id) VALUES(?, ?, ?);"

    run_sql_command(cursor, sql_link_song_artist, (song_id, artist_id, artist_alt_id))


def link_song_composer(cursor, song_id, composer_id):

    """
    Add a new link between an song and a composer in the table
    """

    sql_link_song_composer = (
        "INSERT INTO link_song_composer(song_id, composer_id) VALUES(?, ?);"
    )

    run_sql_command(cursor, sql_link_song_composer, (song_id, composer_id))


def link_song_arranger(cursor, song_id, arranger_id):

    """
    Add a new link between an song and an arranger in the table
    """

    sql_link_song_arranger = (
        "INSERT INTO link_song_arranger(song_id, arranger_id) VALUES(?, ?);"
    )

    run_sql_command(cursor, sql_link_song_arranger, (song_id, arranger_id))


def link_anime_tag(cursor, annId, tag):

    """
    Add a new link between an anime and a tag
    """

    sql_link_song_arranger = "INSERT INTO link_anime_tag(annId, tag) VALUES(?, ?);"

    run_sql_command(cursor, sql_link_song_arranger, (annId, tag))


def link_anime_genre(cursor, annId, genre):

    """
    Add a new link between an anime and a genre
    """

    sql_link_song_arranger = "INSERT INTO link_anime_genre(annId, genre) VALUES(?, ?);"

    run_sql_command(cursor, sql_link_song_arranger, (annId, genre))


try:
    sqliteConnection = sqlite3.connect(database)
    cursor = sqliteConnection.cursor()
    for command in RESET_DB_SQL.split(";"):
        run_sql_command(cursor, command)
    sqliteConnection.commit()
    cursor.close()
    sqliteConnection.close()
    print("Reset successful :)")
except sqlite3.Error as error:
    print("\n", error, "\n")

try:
    sqliteConnection = sqlite3.connect(database)
    cursor = sqliteConnection.cursor()
    print("Connection successful :)")
except sqlite3.Error as error:
    print("\n", error, "\n")


for artist_id in artist_database:

    new_artist_id = insert_new_artist(
        cursor,
        artist_database[artist_id]["names"][0],
        artist_database[artist_id]["vocalist"],
        artist_database[artist_id]["composer"],
    )

    if len(artist_database[artist_id]["names"]) > 1:
        insert_artist_alt_names(
            cursor, new_artist_id, artist_database[artist_id]["names"][1:]
        )

    if len(artist_database[artist_id]["members"]) > 0:
        for i, member_sets in enumerate(artist_database[artist_id]["members"]):
            insert_new_group(cursor, new_artist_id, i)
            for member_id in member_sets:
                add_artist_to_group(cursor, int(member_id) + 1, new_artist_id, i)

for anime in song_database:

    insert_anime(
        cursor,
        anime["annId"],
        anime["animeExpandName"],
        anime["animeJPName"] if "animeJPName" in anime else None,
        anime["animeENName"] if "animeENName" in anime else None,
        anime["animeVintage"] if "animeVintage" in anime else None,
        anime["animeType"] if "animeType" in anime else None,
    )

    if "tags" in anime and anime["tags"]:
        for tag in anime["tags"]:
            link_anime_tag(cursor, anime["annId"], tag)

    if "genres" in anime and anime["genres"]:
        for genre in anime["genres"]:
            link_anime_genre(cursor, anime["annId"], genre)

    for song in anime["songs"]:

        links = song["links"]

        song_id = insert_song(
            cursor,
            song["annSongId"],
            anime["annId"],
            song["songType"],
            song["songNumber"],
            song["songName"],
            song["songArtist"],
            song["songDifficulty"] if "songDifficulty" in song else None,
            links["HQ"] if "HQ" in links.keys() else None,
            links["MQ"] if "MQ" in links.keys() else None,
            links["audio"] if "audio" in links.keys() else None,
        )

        for artist in song["artist_ids"]:

            link_song_artist(cursor, song_id, artist[0] + 1, artist[1])

        if "composer_ids" in song:
            for composer in song["composer_ids"]:
                link_song_composer(cursor, song_id, int(composer) + 1)

        if "arranger_ids" in song:
            for arranger in song["arranger_ids"]:
                link_song_arranger(cursor, song_id, int(arranger) + 1)


sqliteConnection.commit()
cursor.close()
sqliteConnection.close()
print("Convertion Done :)")
