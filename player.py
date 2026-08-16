import subprocess

def play(video):
    subprocess.run(["mpv", "--fs", video])
