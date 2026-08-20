import random
import subprocess


def play(video, loop=False, audio_track=None):
    command = ["mpv", "--fs"]

    if loop:
        command.append("--loop-file=inf")

    if audio_track is not None:
        command.append(f"--aid={audio_track}")

    command.append(video)

    subprocess.run(command)


def play_playlist(episodes, start_index=0, audio_track=None):
    if not episodes:
        return

    # Start at the selected episode
    playlist = (
        episodes[start_index:]
        + episodes[:start_index]
    )

    command = [
        "mpv",
        "--fs",
        "--loop-playlist=inf",
    ]

    if audio_track is not None:
        command.append(f"--aid={audio_track}")

    command.extend(str(episode) for episode in playlist)

    subprocess.run(command)


def play_random(episodes, audio_track=None):
    if not episodes:
        return

    playlist = list(episodes)
    random.shuffle(playlist)

    command = [
        "mpv",
        "--fs",
        "--loop-playlist=inf",
        "--shuffle",
    ]

    if audio_track is not None:
        command.append(f"--aid={audio_track}")

    command.extend(str(episode) for episode in playlist)

    subprocess.run(command)
