import re

ANIME_REGEX_REPLACE_RULES = [
    # Ļ can't lower correctly with sqlite lower function hence why next line is needed
    {"input": "ļ", "replace": "[ļĻ]"},
    {"input": "l", "replace": "[l˥ļĻΛ]"},
    # Ź can't lower correctly with sqlite lower function hence why next line is needed
    {"input": "ź", "replace": "[źŹ]"},
    {"input": "z", "replace": "[zźŹ]"},
    {"input": "ou", "replace": "(ou|ō|o)"},
    {"input": "oo", "replace": "(oo|ō|o)"},
    {"input": "oh", "replace": "(oh|ō|o)"},
    {"input": "wo", "replace": "(wo|o)"},
    {"input": "o", "replace": "([oōóòöôøӨΦο]|ou|oo|oh|wo)"},
    {"input": "uu", "replace": "(uu|u|ū)"},
    {"input": "u", "replace": "([uūûúùüǖμ]|uu)"},
    {"input": "aa", "replace": "(aa|a)"},
    {"input": "ae", "replace": "(ae|æ)"},
    # Λ can't lower correctly with sqlite lower function hence why next line is needed
    {"input": "λ", "replace": "[λΛ]"},
    {"input": "a", "replace": "([aäãά@âàáạåæā∀Λ]|aa)"},
    {"input": "c", "replace": "[cςč℃Ↄ]"},
    # É can't lower correctly with sql lower function
    {"input": "é", "replace": "[éÉ]"},
    {"input": "e", "replace": "[eəéÉêёëèæē]"},
    {"input": "'", "replace": "['’ˈ]"},
    {"input": "n", "replace": "[nñ]"},
    {"input": "0", "replace": "[0Ө]"},
    {"input": "2", "replace": "[2²]"},
    {"input": "3", "replace": "[3³]"},
    {"input": "5", "replace": "[5⁵]"},
    {"input": "*", "replace": "[*✻＊✳︎]"},
    {
        "input": " ",
        "replace": "([^\\w]+|_+)",
    },
    {"input": "i", "replace": "([iíίɪ]|ii)"},
    {"input": "x", "replace": "[x×]"},
    {"input": "b", "replace": "[bßβ]"},
    {"input": "r", "replace": "[rЯ]"},
    {"input": "s", "replace": "[sς]"},
]


def escapeRegExp(str):
    str = re.escape(str)
    str = str.replace("\ ", " ")
    str = str.replace("\*", "*")
    return str


def apply_regex_rules(search):
    for rule in ANIME_REGEX_REPLACE_RULES:
        search = search.replace(rule["input"], rule["replace"])
    return search


def get_regex_search(og_search, partial_match=True, swap_words=False):
    og_search = escapeRegExp(og_search.lower())
    search = apply_regex_rules(og_search)
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

    if song[13] == 1:
        type = "Opening " + str(song[14])
    elif song[13] == 2:
        type = "Ending " + str(song[14])
    else:
        type = "Insert Song"

    artists = []
    if song[17]:
        for artist_id, line_up in zip(song[17].split(","), song[18].split(",")):
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
                added_group = set()
                for group in artist_database[str(artist_id)]["groups"]:
                    if group[0] in added_group:
                        continue
                    added_group.add(group[0])
                    current_artist["groups"].append(
                        {
                            "id": group[0],
                            "names": artist_database[str(group[0])]["names"],
                        }
                    )

            artists.append(current_artist)

    composers = []
    if song[19]:
        for composer_id in song[19].split(","):
            composers.append(
                {"id": composer_id, "names": artist_database[str(composer_id)]["names"]}
            )

    arrangers = []
    if song[20]:
        for arranger_id in song[20].split(","):
            arrangers.append(
                {"id": arranger_id, "names": artist_database[str(arranger_id)]["names"]}
            )

    songinfo = {
        "annId": song[0],
        "linked_ids": {
            "myanimelist": song[1],
            "anidb": song[2],
            "anilist": song[3],
            "kitsu": song[4],
        },
        "annSongId": song[12],
        "animeJPName": song[6] if song[6] else song[5],
        "animeENName": song[7] if song[7] else song[5],
        "animeAltName": song[8].split("\$") if song[8] else song[8],
        "animeVintage": song[9],
        "animeType": song[10],
        "songType": type,
        "songName": song[15],
        "songArtist": song[16],
        "songDifficulty": song[21],
        "songCategory": song[22],
        "songLength": song[23],
        "HQ": song[24],
        "MQ": song[25],
        "audio": song[26],
        "artists": artists,
        "composers": composers,
        "arrangers": arrangers,
    }

    return songinfo
