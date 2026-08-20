import subprocess


def play(video, loop=False, audio_track=None):
    command = ["mpv", "--fs"]

    if loop:
        command.append("--loop-file=inf")

    if audio_track is not None:
        command.append(f"--aid={audio_track}")

    command.append(video)

    subprocess.run(command)
