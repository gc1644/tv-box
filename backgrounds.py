#!/usr/bin/env python3

import random
import subprocess
import sys
import tempfile
from pathlib import Path

import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageTk


# ============================================================
# CONFIG
# ============================================================

OUTPUT_DIR = (
    Path.home()
    / "Downloads"
    / "tv-box"
    / "data"
    / "backgrounds"
    / "movies"
)

VIDEO_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".avi",
    ".webm",
    ".mov",
    ".m4v",
}

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

IMAGE_WIDTH = 370
IMAGE_HEIGHT = 470


# ============================================================
# VIDEO FUNCTIONS
# ============================================================

def get_video_duration(video):
    """Get video duration in seconds using ffprobe."""

    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    return float(result.stdout.strip())


def take_screenshot(video, timestamp, output):
    """Extract one frame from a video using ffmpeg."""

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            str(timestamp),
            "-i",
            str(video),
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(output),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )


def get_random_screenshots(video, temp_dir):
    """Generate three random screenshots from a video."""

    duration = get_video_duration(video)

    # Avoid the very beginning and end.
    start = duration * 0.05
    end = duration * 0.95

    if end <= start:
        start = 0
        end = duration

    timestamps = [
        random.uniform(start, end)
        for _ in range(3)
    ]

    screenshots = []

    for i, timestamp in enumerate(timestamps):

        output = temp_dir / f"screenshot_{i}.jpg"

        try:
            take_screenshot(
                video,
                timestamp,
                output,
            )

            screenshots.append(output)

        except subprocess.CalledProcessError:
            pass

    return screenshots


# ============================================================
# FILE FUNCTIONS
# ============================================================

def find_videos(path):
    """Find video files in a file or folder."""

    if path.is_file():

        if path.suffix.lower() in VIDEO_EXTENSIONS:
            return [path]

        return []

    if path.is_dir():

        return sorted(
            [
                file
                for file in path.iterdir()
                if (
                    file.is_file()
                    and file.suffix.lower() in VIDEO_EXTENSIONS
                )
            ],
            key=lambda file: file.name.lower(),
        )

    return []


# ============================================================
# GUI
# ============================================================

class ScreenshotPicker:

    def __init__(self, root, videos):

        self.root = root
        self.videos = videos
        self.current_index = 0

        self.temp_dir = Path(
            tempfile.mkdtemp(
                prefix="tv-box-screenshot-picker-"
            )
        )

        self.images = []
        self.image_labels = []
        self.choose_buttons = []

        # ----------------------------------------------------
        # Window
        # ----------------------------------------------------

        self.root.title(
            "TV Box Screenshot Picker"
        )

        self.root.geometry(
            f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
        )

        self.root.minsize(
            900,
            600,
        )

        self.root.configure(
            bg="#111111"
        )

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close,
        )

        # ----------------------------------------------------
        # Title
        # ----------------------------------------------------

        self.title_label = tk.Label(
            self.root,
            text="",
            font=(
                "DejaVu Sans",
                16,
                "bold",
            ),
            bg="#111111",
            fg="white",
        )

        self.title_label.pack(
            pady=(5, 1)
        )

        # ----------------------------------------------------
        # Info
        # ----------------------------------------------------

        self.info_label = tk.Label(
            self.root,
            text="",
            font=(
                "DejaVu Sans",
                9,
            ),
            bg="#111111",
            fg="#aaaaaa",
        )

        self.info_label.pack(
            pady=(0, 3)
        )

        # ----------------------------------------------------
        # TOP CONTROLS
        # ----------------------------------------------------

        controls = tk.Frame(
            self.root,
            bg="#111111",
        )

        controls.pack(
            pady=(0, 5)
        )

        tk.Button(
            controls,
            text="New 3",
            font=(
                "DejaVu Sans",
                9,
            ),
            width=8,
            height=1,
            padx=2,
            pady=1,
            command=self.new_screenshots,
        ).grid(
            row=0,
            column=0,
            padx=4,
        )

        tk.Button(
            controls,
            text="Skip",
            font=(
                "DejaVu Sans",
                9,
            ),
            width=8,
            height=1,
            padx=2,
            pady=1,
            command=self.skip,
        ).grid(
            row=0,
            column=1,
            padx=4,
        )

        tk.Button(
            controls,
            text="Quit",
            font=(
                "DejaVu Sans",
                9,
            ),
            width=8,
            height=1,
            padx=2,
            pady=1,
            command=self.close,
        ).grid(
            row=0,
            column=2,
            padx=4,
        )

        # ----------------------------------------------------
        # SCREENSHOT AREA
        # ----------------------------------------------------

        self.preview_frame = tk.Frame(
            self.root,
            bg="#111111",
        )

        self.preview_frame.pack(
            expand=True
        )

        for i in range(3):

            frame = tk.Frame(
                self.preview_frame,
                bg="#111111",
                padx=4,
            )

            frame.grid(
                row=0,
                column=i,
            )

            # Image

            label = tk.Label(
                frame,
                bg="black",
                cursor="hand2",
            )

            label.pack()

            label.bind(
                "<Button-1>",
                lambda event, index=i:
                self.choose(index),
            )

            self.image_labels.append(
                label
            )

            # Pick button

            button = tk.Button(
                frame,
                text=f"Pick {i + 1}",
                font=(
                    "DejaVu Sans",
                    9,
                    "bold",
                ),
                width=10,
                height=1,
                padx=2,
                pady=1,
                command=lambda index=i:
                self.choose(index),
            )

            button.pack(
                pady=(3, 0)
            )

            self.choose_buttons.append(
                button
            )

        # Start

        self.load_video()

    # ========================================================
    # VIDEO NAVIGATION
    # ========================================================

    def load_video(self):

        if self.current_index >= len(self.videos):

            self.finished()

            return

        video = self.videos[
            self.current_index
        ]

        self.title_label.config(
            text=video.stem
        )

        self.info_label.config(
            text=(
                f"Movie "
                f"{self.current_index + 1}"
                f" of "
                f"{len(self.videos)}"
            )
        )

        self.new_screenshots()

    # ========================================================
    # SCREENSHOT GENERATION
    # ========================================================

    def new_screenshots(self):

        video = self.videos[
            self.current_index
        ]

        self.info_label.config(
            text="Generating 3 random screenshots..."
        )

        self.root.update_idletasks()

        # Delete old temporary screenshots.

        for file in self.temp_dir.iterdir():

            try:
                file.unlink()

            except OSError:
                pass

        try:

            screenshots = get_random_screenshots(
                video,
                self.temp_dir,
            )

        except Exception as error:

            messagebox.showerror(
                "Error",
                (
                    "Couldn't read the video:\n\n"
                    f"{video}\n\n"
                    f"{error}"
                ),
            )

            self.skip()

            return

        if len(screenshots) != 3:

            messagebox.showerror(
                "Error",
                (
                    "Couldn't create three screenshots "
                    "for:\n\n"
                    f"{video}"
                ),
            )

            self.skip()

            return

        self.images.clear()

        # Display screenshots.

        for i, screenshot in enumerate(
            screenshots
        ):

            image = Image.open(
                screenshot
            ).convert("RGB")

            image.thumbnail(
                (
                    IMAGE_WIDTH,
                    IMAGE_HEIGHT,
                ),
                Image.Resampling.LANCZOS,
            )

            # Black canvas keeps previews
            # the same size.

            canvas = Image.new(
                "RGB",
                (
                    IMAGE_WIDTH,
                    IMAGE_HEIGHT,
                ),
                "black",
            )

            x = (
                IMAGE_WIDTH
                - image.width
            ) // 2

            y = (
                IMAGE_HEIGHT
                - image.height
            ) // 2

            canvas.paste(
                image,
                (x, y),
            )

            photo = ImageTk.PhotoImage(
                canvas
            )

            self.images.append(
                photo
            )

            self.image_labels[i].config(
                image=photo
            )

        self.info_label.config(
            text=(
                f"Movie "
                f"{self.current_index + 1}"
                f" of "
                f"{len(self.videos)}"
                " — pick your favorite"
            )
        )

    # ========================================================
    # CHOOSE SCREENSHOT
    # ========================================================

    def choose(self, index):

        if len(self.images) != 3:
            return

        video = self.videos[
            self.current_index
        ]

        source = (
            self.temp_dir
            / f"screenshot_{index}.jpg"
        )

        OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        output = (
            OUTPUT_DIR
            / f"{video.stem}.jpg"
        )

        try:

            image = Image.open(
                source
            ).convert("RGB")

            image.save(
                output,
                "JPEG",
                quality=95,
            )

        except Exception as error:

            messagebox.showerror(
                "Save error",
                (
                    "Couldn't save screenshot:\n\n"
                    f"{output}\n\n"
                    f"{error}"
                ),
            )

            return

        # Next movie.

        self.current_index += 1

        self.load_video()

    # ========================================================
    # SKIP
    # ========================================================

    def skip(self):

        self.current_index += 1

        self.load_video()

    # ========================================================
    # FINISHED
    # ========================================================

    def finished(self):

        messagebox.showinfo(
            "Finished!",
            (
                "All movies have been processed.\n\n"
                "Screenshots were saved to:\n\n"
                f"{OUTPUT_DIR}"
            ),
        )

        self.close()

    # ========================================================
    # CLOSE
    # ========================================================

    def close(self):

        # Delete temporary screenshots.

        try:

            for file in self.temp_dir.iterdir():

                try:
                    file.unlink()
                except OSError:
                    pass

            self.temp_dir.rmdir()

        except OSError:
            pass

        self.root.destroy()


# ============================================================
# MAIN
# ============================================================

def main():

    if len(sys.argv) != 2:

        print(
            "Usage:"
        )

        print(
            "  python3 screenshot_picker.py <video-or-folder>"
        )

        print()

        print(
            "Examples:"
        )

        print(
            "  python3 screenshot_picker.py movie.mp4"
        )

        print(
            "  python3 screenshot_picker.py media/movies"
        )

        sys.exit(1)

    input_path = Path(
        sys.argv[1]
    ).expanduser().resolve()

    videos = find_videos(
        input_path
    )

    if not videos:

        print(
            f"No video files found: {input_path}"
        )

        sys.exit(1)

    print(
        f"Found {len(videos)} video(s)."
    )

    print(
        "Screenshots will be saved to:"
    )

    print(
        f"  {OUTPUT_DIR}"
    )

    root = tk.Tk()

    ScreenshotPicker(
        root,
        videos,
    )

    root.mainloop()


if __name__ == "__main__":
    main()
