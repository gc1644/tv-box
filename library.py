from pathlib import Path
import random


VIDEO_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".avi",
    ".webm",
    ".mov",
}


def scan_library(media_path):
    """
    Scan the media directory.

    Expected structure:

        Videos/
        ├── Simpsons/
        │   ├── Season 1/
        │   └── Season 2/
        ├── Futurama/
        ├── Movies/
        ├── Halloween/
        ├── Christmas/
        └── fireplace.mp4

    Returns:

        {
            "shows": {
                "Simpsons": {
                    "Season 1": [...],
                    "Season 2": [...]
                }
            },
            "movies": [...],
            "fireplace": Path(...)
        }
    """

    media = Path(media_path)

    library = {
        "shows": {},
        "movies": [],
        "fireplace": None,
    }

    if not media.exists():
        print(f"Media directory not found: {media}")
        return library

    for item in media.iterdir():

        # =========================
        # FIREPLACE
        # =========================

        if (
            item.is_file()
            and item.stem.lower() == "fireplace"
            and item.suffix.lower() in VIDEO_EXTENSIONS
        ):
            library["fireplace"] = item
            continue

        # =========================
        # MOVIES
        # =========================

        if item.is_dir() and item.name.lower() == "movies":

            for movie in item.rglob("*"):

                if (
                    movie.is_file()
                    and movie.suffix.lower()
                    in VIDEO_EXTENSIONS
                ):
                    library["movies"].append(movie)

            continue

        # =========================
        # SHOWS
        # =========================

        if not item.is_dir():
            continue

        show_name = item.name

        seasons = {}

        for season_dir in item.iterdir():

            if not season_dir.is_dir():
                continue

            episodes = []

            for episode in season_dir.rglob("*"):

                if (
                    episode.is_file()
                    and episode.suffix.lower()
                    in VIDEO_EXTENSIONS
                ):
                    episodes.append(episode)

            if episodes:

                episodes.sort(
                    key=lambda path: path.name.lower()
                )

                seasons[season_dir.name] = episodes

        if seasons:
            library["shows"][show_name] = seasons

    # Keep movies sorted
    library["movies"].sort(
        key=lambda path: path.name.lower()
    )

    return library


def random_episode(library, show_name):
    """
    Return a random episode from a show.
    """

    episodes = []

    for season_episodes in (
        library["shows"][show_name].values()
    ):
        episodes.extend(season_episodes)

    if not episodes:
        return None

    return random.choice(episodes)


def scan_all_media(media_path):
    """
    Recursively find every playable video under
    the media directory.

    This is used by the ? randomizer.

    It does NOT care what folder the video is in.

    Example:

        Videos/Simpsons/Season 1/a.mp4
        Videos/Movies/Home Alone.mkv
        Videos/Halloween/treehouse.mp4
        Videos/Christmas/home-alone.mp4

    All of them are valid random choices.
    """

    media = Path(media_path)

    if not media.exists():
        return []

    files = [
        path
        for path in media.rglob("*")
        if (
            path.is_file()
            and path.suffix.lower()
            in VIDEO_EXTENSIONS
        )
    ]

    files.sort(
        key=lambda path: path.name.lower()
    )

    return files
