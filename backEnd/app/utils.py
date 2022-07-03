import re
import sql_calls

ANIME_REGEX_REPLACE_RULES = [
    {"input": "ou", "replace": "(ou|ō|o)"},
    {"input": "oo", "replace": "(oo|ō|o)"},
    {"input": "oh", "replace": "(oh|ō|o)"},
    {"input": "wo", "replace": "(wo|o)"},
    {"input": "o", "replace": "([oōóòöôøΦο]|ou|oo|oh|wo)"},
    {"input": "uu", "replace": "(uu|u|ū)"},
    {"input": "u", "replace": "([uūûúùüǖ]|uu)"},
    {"input": "aa", "replace": "(aa|a)"},
    {"input": "a", "replace": "([aä@âàáạåæā∀]|aa)"},
    {"input": "c", "replace": "[cč]"},
    {"input": "e", "replace": "[eéêёëèæē]"},
    {"input": "'", "replace": "['’]"},
    {"input": "n", "replace": "[nñ]"},
    {"input": "2", "replace": "[2²]"},
    {"input": " ", "replace": "( ?[²★☆\\/\\*=\\+·♥'♡∽・±⇔≒〜†×♪→␣:∞;~\\-?,.!@_] ?| )"},
    {"input": "i", "replace": "([iíί]|ii)"},
    {"input": "3", "replace": "[3³]"},
    {"input": "x", "replace": "[x×]"},
    {"input": "b", "replace": "[bßβ]"},
    {"input": "r", "replace": "[rЯ]"},
    {"input": "s", "replace": "[sς]"},
    {"input": "l", "replace": "[l˥]"},
]


def escapeRegExp(str):
    str = re.escape(str)
    str = str.replace("\ ", " ")
    return str


def apply_regex_rules(search):
    for rule in ANIME_REGEX_REPLACE_RULES:
        search = search.replace(rule["input"], rule["replace"])
    return search


def get_regex_search(og_search, partial_match=True, swap_words=False):

    search = og_search.lower()
    search = escapeRegExp(search)
    search = apply_regex_rules(search)
    search = "^" + search + "$" if not partial_match else ".*" + search + ".*"

    if swap_words:
        alt_search = og_search.split(" ")
        if len(alt_search) == 2:
            alt_search = " ".join([alt_search[1], alt_search[0]])
            alt_search = apply_regex_rules(alt_search)
            alt_search = (
                "^" + alt_search + "$"
                if not partial_match
                else ".*" + alt_search + ".*"
            )
            search = f"({search})|({alt_search})"
    return search


def format_song(artist_database, song):

    if song[8] == 1:
        type = "Opening " + str(song[9])
    elif song[8] == 2:
        type = "Ending " + str(song[9])
    else:
        type = "Insert Song"

    artists = []
    if song[12]:
        for artist_id, line_up in zip(song[12].split(","), song[13].split(",")):

            line_up = int(line_up)

            current_artist = {
                "id": artist_id,
                "names": artist_database[str(artist_id)]["names"],
                "line_up_id": line_up,
            }

            if (
                artist_database[str(artist_id)]["members"]
                and len(artist_database[str(artist_id)]["members"]) >= line_up
            ):
                current_artist["members"] = []
                for member in artist_database[str(artist_id)]["members"][line_up]:
                    current_artist["members"].append(
                        {
                            "id": member[0],
                            "names": artist_database[str(member[0])]["names"],
                        }
                    )

            if artist_database[str(artist_id)]["groups"]:
                current_artist["groups"] = []
                for group in artist_database[str(artist_id)]["groups"]:
                    current_artist["groups"].append(
                        {
                            "id": group[0],
                            "names": artist_database[str(group[0])]["names"],
                        }
                    )

            artists.append(current_artist)

    composers = []
    if song[14]:
        for composer_id in song[14].split(","):
            composers.append(
                {"id": composer_id, "names": artist_database[str(composer_id)]["names"]}
            )

    arrangers = []
    if song[15]:
        for arranger_id in song[15].split(","):
            arrangers.append(
                {"id": arranger_id, "names": artist_database[str(arranger_id)]["names"]}
            )

    songinfo = {
        "annId": song[0],
        "annSongId": song[7],
        "animeExpandName": song[1],
        "animeJPName": song[2],
        "animeENName": song[3],
        "animeVintage": song[4],
        "animeType": song[5],
        "songType": type,
        "songName": song[10],
        "songArtist": song[11],
        "songDifficulty": song[16],
        "HQ": song[17],
        "MQ": song[18],
        "audio": song[19],
        "artists": artists,
        "composers": composers,
        "arrangers": arrangers,
        # TODO artists_ids/arranger_ids/composer_ids
    }

    return songinfo
