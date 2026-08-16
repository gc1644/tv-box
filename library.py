from pathlib import Path


VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".webm", ".mov"}


def scan_library(directory):
    library = {}

    for series_dir in Path(directory).iterdir():
        if not series_dir.is_dir():
            continue

        seasons = {}

        for season_dir in series_dir.iterdir():
            if not season_dir.is_dir():
                continue

            episodes = []

            for file in season_dir.iterdir():
                if file.is_file() and file.suffix.lower() in VIDEO_EXTENSIONS:
                    episodes.append(file)

            if episodes:
                seasons[season_dir.name] = episodes

        if seasons:
            library[series_dir.name] = seasons

    return library
