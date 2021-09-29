from pathlib import Path
import json
import re
import os

# ______ General Configuration ______

# Relative path of the .json file you downloaded,
# if it's in the same folder as this script, then it's just the file name.
song_list_path = "_mylife of spring_nobodyk_SongList.json"

# Set what you want to download: mp3, webm, mp4, custom
# if custom, you need to set your custom parameters further down
download_type = "mp3"

# Relative output path where your downloaded files will go
output_path = "downloaded/"

# If True: it will overwrite automatically if the downloaded file name already exist
# If not: it will throw an error and go to the next song
overwrite_already_existing_name = False

# ______ General Configuration ______


# ___________ Advanced Settings ____________
# Only if download_type set to custom
# Here it is an example if you wanted to make all webm 720p (upscale 480p if not available)
custom_parameters = '-c:a copy -crf 20 -c:v libvpx-vp9 -vf "scale=-1:720"'
custom_extension = ".webm"
# what it needs to take as source ("video" = 720 or 480, "audio" = mp3)
custom_input = "video"

# If your ffmpeg isn't in the environment variable path, set the right value you need here
# If you can do "ffmpeg -h" in your terminal, then don't touch this
ffmpeg = "ffmpeg"
# ___________ Advanced Settings ____________


default_mp3_parameters = "-c:a copy"
default_mp3_extension = ".mp3"

default_webm_parameters = "-c copy -map_metadata -1 -map_chapters -1"
default_webm_extension = ".webm"

default_mp4_parameters = "-c:a aac -c:v libx264 -map_metadata -1 -map_chapters -1"
default_mp4_extension = ".mp4"


def create_file_name_Windows(songTitle, path, extension, allowance=255):
    """
    Creates a windows-compliant filename by removing all bad characters
    and maintaining the windows path length limit (which by default is 255)
    """
    allowance -= (
        len(str(path)) + 1
    )  # by default, windows is sensitive to long total paths.
    bad_characters = re.compile(r"\\|/|<|>|:|\"|\||\?|\*|&|\^|\$|" + "\0")
    return create_file_name_common(
        songTitle, path, bad_characters, extension, allowance
    )


def create_file_name_common(songTitle, path, bad_characters, extension, allowance=255):
    if allowance > 255:
        allowance = 255  # on most common filesystems, including NTFS a filename can not exceed 255 characters
    # assign allowance for things that must be in the file name
    allowance -= len(extension)  # accounting for separators (-_) for .webm
    if allowance < 0:
        raise ValueError(
            """It is not possible to give a reasonable file name, due to length limitations.
        Consider changing location to somewhere with a shorter path."""
        )

    # make sure that user input doesn't contain bad characters
    songTitle = bad_characters.sub("", songTitle)
    ret = ""
    for string in [songTitle]:
        length = len(string)
        if allowance - length < 0:
            string = string[:allowance]
            length = len(string)
        ret += string
        allowance -= length

    ret = path + ret + extension

    return ret


def execute_command(command):
    os.system(command)


if __name__ == "__main__":

    with open(song_list_path, encoding="utf-8") as json_file:
        song_list_json = json.load(json_file)

        Path(output_path).mkdir(exist_ok=True)

        for song in song_list_json:

            if overwrite_already_existing_name:
                ignore_parameter = "-y"
            else:
                ignore_parameter = "-n"

            file_name = (
                str(song["annId"])
                + " "
                + song["Anime"]
                + " "
                + song["Type"]
                + " - "
                + song["SongName"]
                + " by "
                + song["Artist"]
            )

            try:

                if download_type == "mp3":

                    link = song["mptrois"] if "mptrois" in song else None

                    if link:

                        command = [
                            "%s" % ffmpeg,
                            ignore_parameter,
                            "-i",
                            link,
                            default_mp3_parameters,
                            '"%s"'
                            % create_file_name_Windows(
                                file_name, output_path, default_mp3_extension
                            ),
                        ]

                    else:
                        link = (
                            song["sept"]
                            if "sept" in song and song["sept"] != None
                            else song["quatre"]
                            if "quatre" in song
                            else None
                        )

                        if link:

                            command = [
                                "%s" % ffmpeg,
                                ignore_parameter,
                                "-i",
                                link,
                                "-codec:a libmp3lame -b:a 320k -compression_level 7",
                                '"%s"'
                                % create_file_name_Windows(
                                    file_name, output_path, default_mp3_extension
                                ),
                            ]
                        else:
                            raise ValueError("Warning:", file_name, "is not uploaded")

                elif download_type == "webm":

                    link = (
                        song["sept"]
                        if "sept" in song and song["sept"] != None
                        else song["quatre"]
                        if "quatre" in song
                        else None
                    )

                    if link:

                        command = [
                            "%s" % ffmpeg,
                            ignore_parameter,
                            "-i",
                            link,
                            default_webm_parameters,
                            '"%s"'
                            % create_file_name_Windows(
                                file_name, output_path, default_webm_extension
                            ),
                        ]
                    else:
                        raise ValueError(
                            "Warning:", file_name, "doesn't have any video uploaded"
                        )

                elif download_type == "mp4":

                    link = (
                        song["sept"]
                        if "sept" in song and song["sept"] != None
                        else song["quatre"]
                        if "quatre" in song
                        else None
                    )

                    if link:
                        command = [
                            "%s" % ffmpeg,
                            ignore_parameter,
                            "-i",
                            link,
                            default_mp4_parameters,
                            '"%s"'
                            % create_file_name_Windows(
                                file_name, output_path, default_mp4_extension
                            ),
                        ]
                    else:
                        raise ValueError(
                            "Warning:", file_name, "doesn't have any video uploaded"
                        )

                elif download_type == "custom":

                    if custom_input == "video":

                        link = (
                            song["sept"]
                            if "sept" in song and song["sept"] != None
                            else song["quatre"]
                            if "quatre" in song
                            else None
                        )

                        if link:

                            command = [
                                "%s" % ffmpeg,
                                ignore_parameter,
                                "-i",
                                link,
                                custom_parameters,
                                '"%s"'
                                % create_file_name_Windows(
                                    file_name, output_path, custom_extension
                                ),
                            ]
                        else:
                            raise ValueError(
                                "Warning:",
                                file_name,
                                "doesn't have any video uploaded",
                            )

                    elif custom_input == "audio":

                        link = song["mptrois"] if "mptrois" in song else None

                        if link:
                            command = [
                                "%s" % ffmpeg,
                                ignore_parameter,
                                "-i",
                                link,
                                custom_parameters,
                                '"%s"'
                                % create_file_name_Windows(
                                    file_name, output_path, custom_extension
                                ),
                            ]

                        else:
                            raise ValueError(
                                "Warning:", file_name, "doesn't have mp3 uploaded",
                            )
                    else:
                        raise ValueError(
                            "Warning:", custom_input, "is set to a wrong value"
                        )

                else:
                    raise ValueError("Warning, download_type is set to a wrong value")

                print(" ".join(command))
                execute_command(" ".join(command))
                print()

            except Exception as e:
                print(e)
                print("Failed for", link, "(" + file_name + ")")
                print()

