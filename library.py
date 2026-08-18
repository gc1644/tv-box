import random
from pathlib import Path


VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".webm", ".mov"}


def scan_library(directory):
    media = Path(directory)

    library = {
        "shows": {},
        "movies": [],
        "fireplace": None,
    }

    for item in media.iterdir():
        # Fireplace
        if item.is_file() and item.name.lower() == "fireplace.mp4":
            library["fireplace"] = item
            continue

        # Movies
        if item.is_dir() and item.name.lower() == "movies":
            for movie in item.iterdir():
                if movie.is_file() and movie.suffix.lower() in VIDEO_EXTENSIONS:
                    library["movies"].append(movie)
            continue

        # TV shows
        if not item.is_dir():
            continue

        seasons = {}

        for season_dir in item.iterdir():
            if not season_dir.is_dir():
                continue

            episodes = []

            for episode in season_dir.iterdir():
                if (
                    episode.is_file()
                    and episode.suffix.lower() in VIDEO_EXTENSIONS
                ):
                    episodes.append(episode)

            if episodes:
                seasons[season_dir.name] = sorted(episodes)

        if seasons:
            library["shows"][item.name] = seasons

    return library

def random_episode(library, show_name=None):
    episodes = []

    if show_name:
        shows = library["shows"].get(show_name, {})

        for season_episodes in shows.values():
            episodes.extend(season_episodes)

    else:
        for show in library["shows"].values():
            for season_episodes in show.values():
                episodes.extend(season_episodes)

    if not episodes:
        return None

    return random.choice(episodes)
