import tkinter as tk
from pathlib import Path
from datetime import date
import random

from PIL import Image, ImageTk

from player import play, play_playlist


class TVBox:
    def __init__(self, library):
        self.library = library

        self.root = tk.Tk()
        self.root.title("TV BOX")
        self.root.geometry("1280x720")
        self.root.configure(bg="#151515")

        # =========================
        # DIRECTORIES
        # =========================

        self.media_dir = Path.home() / "Videos"

        self.background_dir = (
            Path(__file__).parent
            / "data"
            / "backgrounds"
        )

        # =========================
        # NORMAL BACKGROUNDS
        # =========================

        self.backgrounds = {
            "Simpsons": self.load_background("simpsons.jpeg"),
            "Futurama": self.load_background("futurama.jpeg"),
            "Alf": self.load_background("alf.jpeg"),
            "South Park": self.load_background("south-park.jpeg"),
            "SpongeBob": self.load_background("spongebob.jpeg"),
        }

        self.background_image = None
        self.background_label = None

        # =========================
        # EVENT ANIMATION
        # =========================

        self.event_background = None
        self.event_frames = []
        self.event_frame_index = 0
        self.event_animation_job = None

        self.build_main_menu()

    # =========================
    # BACKGROUNDS
    # =========================

    def load_background(self, filename):
        path = self.background_dir / filename

        if not path.exists():
            print(f"Background not found: {path}")
            return None

        image = Image.open(path)

        image = image.resize(
            (1280, 720),
            Image.Resampling.LANCZOS,
        )

        return ImageTk.PhotoImage(image)

    def stop_event_animation(self):
        if self.event_animation_job is not None:
            try:
                self.root.after_cancel(
                    self.event_animation_job
                )
            except tk.TclError:
                pass

            self.event_animation_job = None

        self.event_frames = []
        self.event_frame_index = 0

    def load_event_background(self, filename):
        self.stop_event_animation()

        path = self.background_dir / filename

        if not path.exists():
            print(f"Event background not found: {path}")
            return False

        try:
            image = Image.open(path)

            # Animated GIF
            if getattr(image, "n_frames", 1) > 1:

                self.event_frames = []

                for frame_number in range(image.n_frames):
                    image.seek(frame_number)

                    frame = image.convert("RGB")

                    frame = frame.resize(
                        (1280, 720),
                        Image.Resampling.LANCZOS,
                    )

                    self.event_frames.append(
                        ImageTk.PhotoImage(frame)
                    )

                if not self.event_frames:
                    return False

                self.event_frame_index = 0

                self.background_image = (
                    self.event_frames[0]
                )

                self.background_label = tk.Label(
                    self.root,
                    image=self.background_image,
                    borderwidth=0,
                )

                self.background_label.place(
                    x=0,
                    y=0,
                    relwidth=1,
                    relheight=1,
                )

                self.background_label.lower()

                self.animate_event_background()

                return True

            # Normal image
            image = image.resize(
                (1280, 720),
                Image.Resampling.LANCZOS,
            )

            self.event_background = ImageTk.PhotoImage(
                image
            )

            self.background_image = (
                self.event_background
            )

            self.background_label = tk.Label(
                self.root,
                image=self.background_image,
                borderwidth=0,
            )

            self.background_label.place(
                x=0,
                y=0,
                relwidth=1,
                relheight=1,
            )

            self.background_label.lower()

            return True

        except Exception as error:
            print(
                f"Could not load event background: {error}"
            )
            return False

    def animate_event_background(self):
        if not self.event_frames:
            return

        if not self.background_label:
            return

        self.event_frame_index += 1

        if (
            self.event_frame_index
            >= len(self.event_frames)
        ):
            self.event_frame_index = 0

        self.background_image = (
            self.event_frames[
                self.event_frame_index
            ]
        )

        self.background_label.configure(
            image=self.background_image
        )

        self.event_animation_job = self.root.after(
            100,
            self.animate_event_background,
        )

    def set_background(self, show_name=None):
        self.stop_event_animation()

        if self.background_label:
            self.background_label.destroy()
            self.background_label = None

        if show_name not in self.backgrounds:
            self.root.configure(bg="#151515")
            return

        image = self.backgrounds[show_name]

        if image is None:
            self.root.configure(bg="#151515")
            return

        self.background_image = image

        self.background_label = tk.Label(
            self.root,
            image=self.background_image,
            borderwidth=0,
        )

        self.background_label.place(
            x=0,
            y=0,
            relwidth=1,
            relheight=1,
        )

        self.background_label.lower()

    # =========================
    # GENERAL
    # =========================

    def clear(self):
        self.stop_event_animation()

        for widget in self.root.winfo_children():
            widget.destroy()

        self.background_label = None
        self.background_image = None

    def make_button(
        self,
        parent,
        text,
        bg,
        fg,
        command,
    ):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("DejaVu Sans", 20, "bold"),
            bg=bg,
            fg=fg,
            activebackground="#555555",
            activeforeground="white",
            width=18,
            height=3,
            relief="flat",
            cursor="hand2",
        )

    def make_back_button(self, command):
        tk.Button(
            self.root,
            text="← BACK",
            command=command,
            font=("DejaVu Sans", 12, "bold"),
            bg="#222222",
            fg="white",
            activebackground="#444444",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            width=9,
        ).place(
            relx=0.98,
            rely=0.02,
            anchor="ne",
        )

    def make_small_button(
        self,
        parent,
        text,
        bg,
        fg,
        command,
    ):
        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=("DejaVu Sans", 16, "bold"),
            bg=bg,
            fg=fg,
            activebackground="#555555",
            activeforeground="white",
            width=12,
            height=2,
            relief="flat",
            cursor="hand2",
        )

        return button

    # =========================
    # EVENT DATES
    # =========================

    def get_current_event(self):
        today = date.today()
        # for testing dates use examle below:
        # today = date(2026, 12, 31)

        # Halloween:
        # October 30 - November 1
        if (
            today.month == 10
            and today.day >= 30
        ):
            return "halloween"

        if (
            today.month == 11
            and today.day == 1
        ):
            return "halloween"

        # Christmas:
        # December 1 - January 10
        if today.month == 12:
            return "christmas"

        if (
            today.month == 1
            and today.day <= 10
        ):
            return "christmas"

        return None

    def get_event_button_text(self):
        event = self.get_current_event()

        if event == "halloween":
            return "🎃 ?"

        if event == "christmas":
            return "🎄 ?"

        return "?"

    def get_event_button_color(self):
        event = self.get_current_event()

        if event == "halloween":
            return "#6A1B9A"

        if event == "christmas":
            return "#B71C1C"

        return "#666666"

    def handle_event_button(self):
        event = self.get_current_event()

        if event:
            self.show_event_screen(event)
        else:
            self.show_random_normal()

    # =========================
    # MAIN MENU
    # =========================

    def build_main_menu(self):
        self.clear()

        self.root.configure(bg="#151515")

        title = tk.Label(
            self.root,
            text="📺 TV BOX",
            font=("DejaVu Sans", 30, "bold"),
            bg="#151515",
            fg="white",
        )

        title.pack(pady=(25, 15))

        button_frame = tk.Frame(
            self.root,
            bg="#151515",
        )

        button_frame.pack()

        # Simpsons
        self.make_button(
            button_frame,
            "SIMPSONS",
            "#F5C518",
            "black",
            lambda: self.show_show("Simpsons"),
        ).grid(
            row=0,
            column=0,
            padx=8,
            pady=5,
        )

        # Futurama
        self.make_button(
            button_frame,
            "FUTURAMA",
            "#245A9C",
            "white",
            lambda: self.show_show("Futurama"),
        ).grid(
            row=0,
            column=1,
            padx=8,
            pady=5,
        )

        # Alf
        self.make_button(
            button_frame,
            "ALF",
            "#A0522D",
            "white",
            lambda: self.show_show("Alf"),
        ).grid(
            row=1,
            column=0,
            padx=8,
            pady=5,
        )

        # South Park
        self.make_button(
            button_frame,
            "SOUTH PARK",
            "#356B3D",
            "white",
            lambda: self.show_show("South Park"),
        ).grid(
            row=1,
            column=1,
            padx=8,
            pady=5,
        )

        # SpongeBob
        self.make_button(
            button_frame,
            "SPONGEBOB",
            "#F0806B",
            "white",
            lambda: self.show_show("SpongeBob"),
        ).grid(
            row=2,
            column=0,
            padx=8,
            pady=5,
        )

        # Mystery / Event
        self.make_button(
            button_frame,
            self.get_event_button_text(),
            self.get_event_button_color(),
            "white",
            self.handle_event_button,
        ).grid(
            row=2,
            column=1,
            padx=8,
            pady=5,
        )

        # =========================
        # EXTRAS
        # =========================

        extras_frame = tk.Frame(
            self.root,
            bg="#151515",
        )

        extras_frame.pack(
            pady=(16, 0),
        )

        # Movies
        self.make_button(
            extras_frame,
            "🎬 MOVIES",
            "#333333",
            "white",
            self.show_movies,
        ).grid(
            row=0,
            column=0,
            padx=8,
        )

        # Fireplace
        self.make_button(
            extras_frame,
            "🔥 FIREPLACE",
            "#C62828",
            "white",
            self.play_fireplace,
        ).grid(
            row=0,
            column=1,
            padx=8,
        )

    # =========================
    # NORMAL RANDOM
    # =========================

    def get_normal_random_media(self):
        media = []

        for show_name, seasons in self.library["shows"].items():

            if show_name in (
                "Halloween",
                "Christmas",
            ):
                continue

            for season_episodes in seasons.values():
                media.extend(season_episodes)

        media.extend(self.library["movies"])

        return media

    def show_random_normal(self):
        media = self.get_normal_random_media()

        if not media:
            return

        selected = random.choice(media)

        self.clear()

        self.root.configure(bg="#151515")

        tk.Label(
            self.root,
            text="❔ RANDOM",
            font=("DejaVu Sans", 30, "bold"),
            bg="#151515",
            fg="white",
        ).pack(
            pady=(70, 25),
        )

        tk.Label(
            self.root,
            text=selected.stem,
            font=("DejaVu Sans", 22, "bold"),
            bg="#333333",
            fg="white",
            padx=35,
            pady=20,
        ).pack(
            pady=20,
        )

        self.make_small_button(
            self.root,
            "🎲 REROLL",
            "#555555",
            "white",
            self.show_random_normal,
        ).pack(
            pady=5,
        )

        self.make_small_button(
            self.root,
            "▶ PLAY",
            "#356B3D",
            "white",
            lambda: self.play_random_normal(
                selected
            ),
        ).pack(
            pady=5,
        )

        self.make_back_button(
            self.build_main_menu
        )

    def play_random_normal(self, selected):
        self.root.withdraw()

        play(str(selected))

        self.root.deiconify()

    # =========================
    # EVENT FILES
    # =========================

    def get_event_files(self, event):
        if event == "halloween":
            folder_name = "Halloween"
        else:
            folder_name = "Christmas"

        event_dir = self.media_dir / folder_name

        if not event_dir.exists():
            print(
                f"Event folder not found: {event_dir}"
            )
            return []

        extensions = {
            ".mp4",
            ".mkv",
            ".avi",
            ".webm",
            ".mov",
        }

        return sorted(
            [
                path
                for path in event_dir.iterdir()
                if path.is_file()
                and path.suffix.lower()
                in extensions
            ],
            key=lambda path: path.name.lower(),
        )

    # =========================
    # EVENT RANDOM SCREEN
    # =========================

    def show_event_screen(
        self,
        event,
        selected=None,
    ):
        self.clear()

        if event == "halloween":

            background_file = "halloween.gif"

            title = "🎃 HALLOWEEN 🎃"
            reroll_text = "🎃 REROLL"
            play_text = "👻 PLAY"

            fallback_bg = "#180B20"
            title_color = "#FF8C00"
            reroll_color = "#6A1B9A"
            play_color = "#8B4513"

        else:

            background_file = "christmas.gif"

            title = "🎄 CHRISTMAS 🎄"
            reroll_text = "🎁 REROLL"
            play_text = "🎄 PLAY"

            fallback_bg = "#102018"
            title_color = "#E53935"
            reroll_color = "#B71C1C"
            play_color = "#2E7D32"

        self.root.configure(bg=fallback_bg)

        self.load_event_background(
            background_file
        )

        files = self.get_event_files(event)

        if not files:

            tk.Label(
                self.root,
                text=title,
                font=("DejaVu Sans", 32, "bold"),
                bg=fallback_bg,
                fg=title_color,
            ).pack(
                pady=(80, 25),
            )

            tk.Label(
                self.root,
                text=(
                    "Nothing here yet.\n"
                    f"Put your files in media/"
                    f"{'Halloween' if event == 'halloween' else 'Christmas'}/"
                ),
                font=("DejaVu Sans", 16),
                bg=fallback_bg,
                fg="white",
            ).pack(
                pady=20,
            )

            self.make_back_button(
                self.build_main_menu
            )

            return

        if selected is None:
            selected = random.choice(files)

        # =========================
        # TITLE
        # =========================

        info_frame = tk.Frame(
            self.root,
            bg="#111111",
        )

        info_frame.pack(
            pady=(55, 15),
        )

        tk.Label(
            info_frame,
            text=title,
            font=("DejaVu Sans", 30, "bold"),
            bg="#111111",
            fg=title_color,
            padx=25,
            pady=8,
        ).pack()

        tk.Label(
            info_frame,
            text=selected.stem,
            font=("DejaVu Sans", 20, "bold"),
            bg="#111111",
            fg="white",
            padx=30,
            pady=15,
        ).pack()

        # =========================
        # BUTTONS
        # =========================

        self.make_small_button(
            self.root,
            reroll_text,
            reroll_color,
            "white",
            lambda: self.show_event_screen(
                event
            ),
        ).pack(
            pady=4,
        )

        self.make_small_button(
            self.root,
            play_text,
            play_color,
            "white",
            lambda: self.play_event_file(
                selected
            ),
        ).pack(
            pady=4,
        )

        self.make_small_button(
            self.root,
            "📂 BROWSE",
            "#333333",
            "white",
            lambda: self.show_event_browse(
                event,
                page=0,
            ),
        ).pack(
            pady=4,
        )

        self.make_back_button(
            self.build_main_menu
        )

    def play_event_file(self, selected):
        self.root.withdraw()

        play(str(selected))

        self.root.deiconify()

    # =========================
    # EVENT BROWSE
    # =========================

    def show_event_browse(
        self,
        event,
        page=0,
    ):
        self.clear()

        if event == "halloween":

            background_file = "halloween.gif"
            title = "🎃 HALLOWEEN"
            fallback_bg = "#180B20"
            title_color = "#FF8C00"
            button_color = "#6A1B9A"

        else:

            background_file = "christmas.gif"
            title = "🎄 CHRISTMAS"
            fallback_bg = "#102018"
            title_color = "#E53935"
            button_color = "#B71C1C"

        self.root.configure(bg=fallback_bg)

        self.load_event_background(
            background_file
        )

        files = self.get_event_files(event)

        FILES_PER_PAGE = 10

        start = page * FILES_PER_PAGE
        end = start + FILES_PER_PAGE

        page_files = files[start:end]

        total_pages = (
            len(files)
            + FILES_PER_PAGE
            - 1
        ) // FILES_PER_PAGE

        # =========================
        # TITLE
        # =========================

        tk.Label(
            self.root,
            text=title,
            font=("DejaVu Sans", 26, "bold"),
            bg="#111111",
            fg=title_color,
        ).pack(
            pady=(12, 3),
        )

        if total_pages > 1:

            tk.Label(
                self.root,
                text=f"Page {page + 1} / {total_pages}",
                font=("DejaVu Sans", 10),
                bg="#111111",
                fg="#AAAAAA",
            ).pack(
                pady=(0, 3),
            )

        # =========================
        # PAGE NAVIGATION
        # =========================

        navigation = tk.Frame(
            self.root,
            bg="#111111",
        )

        navigation.pack(
            pady=2,
        )

        if page > 0:

            tk.Button(
                navigation,
                text="← PREV",
                command=lambda: self.show_event_browse(
                    event,
                    page - 1,
                ),
                font=("DejaVu Sans", 11, "bold"),
                bg="#222222",
                fg="white",
                activebackground="#444444",
                activeforeground="white",
                relief="flat",
                cursor="hand2",
                width=10,
                height=1,
            ).grid(
                row=0,
                column=0,
                padx=5,
            )

        if page < total_pages - 1:

            tk.Button(
                navigation,
                text="NEXT →",
                command=lambda: self.show_event_browse(
                    event,
                    page + 1,
                ),
                font=("DejaVu Sans", 11, "bold"),
                bg="#222222",
                fg="white",
                activebackground="#444444",
                activeforeground="white",
                relief="flat",
                cursor="hand2",
                width=10,
                height=1,
            ).grid(
                row=0,
                column=1,
                padx=5,
            )

        # =========================
        # FILE LIST
        # =========================

        file_frame = tk.Frame(
            self.root,
            bg="#111111",
        )

        file_frame.pack(
            pady=2,
        )

        if not files:

            tk.Label(
                file_frame,
                text="No files found.",
                font=("DejaVu Sans", 16),
                bg="#111111",
                fg="white",
            ).pack(
                pady=20,
            )

        else:

            for media_file in page_files:

                button = self.make_small_button(
                    file_frame,
                    media_file.stem,
                    "#333333",
                    "white",
                    lambda f=media_file:
                        self.play_event_file(f),
                )

                button.config(
                    width=42,
                    height=1,
                    font=("DejaVu Sans", 12, "bold"),
                )

                button.pack(
                    pady=2,
                )

        # =========================
        # BACK
        # =========================

        self.make_back_button(
            lambda: self.show_event_screen(event)
        )

    # =========================
    # SHOW MENU
    # =========================

    def show_show(self, show_name):
        self.clear()

        self.set_background(show_name)

        tk.Label(
            self.root,
            text=show_name,
            font=("DejaVu Sans", 28, "bold"),
            bg="#111111",
            fg="white",
        ).pack(
            pady=(15, 10),
        )

        if show_name not in self.library["shows"]:

            tk.Label(
                self.root,
                text="This show isn't in the library yet.",
                font=("DejaVu Sans", 18),
                bg="#111111",
                fg="white",
            ).pack(
                pady=20,
            )

        else:

            season_frame = tk.Frame(
                self.root,
                bg="#111111",
            )

            season_frame.pack(
                expand=True,
                pady=3,
            )

            seasons = list(
                self.library["shows"][show_name].keys()
            )

            for index, season in enumerate(seasons):

                row = index // 4
                column = index % 4

                button = self.make_button(
                    season_frame,
                    season,
                    "#333333",
                    "white",
                    lambda s=season:
                        self.show_season(
                            show_name,
                            s,
                        ),
                )

                button.config(
                    width=12,
                    height=2,
                    font=("DejaVu Sans", 16, "bold"),
                )

                button.grid(
                    row=row,
                    column=column,
                    padx=8,
                    pady=4,
                )

            self.make_button(
                self.root,
                "🎲 RANDOM EPISODE",
                "#555555",
                "white",
                lambda: self.random_show_episode(
                    show_name
                ),
            ).pack(
                pady=6,
            )

        self.make_back_button(
            self.build_main_menu
        )

    # =========================
    # SEASON MENU
    # =========================

    def show_season(
        self,
        show_name,
        season,
    ):
        self.show_episode_page(
            show_name,
            season,
            page=0,
        )

    # =========================
    # EPISODE PAGES
    # =========================

    def show_episode_page(
        self,
        show_name,
        season,
        page=0,
    ):
        self.clear()

        self.set_background(show_name)

        episodes = self.library["shows"][show_name][season]

        EPISODES_PER_PAGE = 10

        start = page * EPISODES_PER_PAGE
        end = start + EPISODES_PER_PAGE

        page_episodes = episodes[start:end]

        total_pages = (
            len(episodes)
            + EPISODES_PER_PAGE
            - 1
        ) // EPISODES_PER_PAGE

        tk.Label(
            self.root,
            text=f"{show_name} — {season}",
            font=("DejaVu Sans", 24, "bold"),
            bg="#111111",
            fg="white",
        ).pack(
            pady=(10, 2),
        )

        if total_pages > 1:

            tk.Label(
                self.root,
                text=f"Page {page + 1} / {total_pages}",
                font=("DejaVu Sans", 10),
                bg="#111111",
                fg="#AAAAAA",
            ).pack(
                pady=(0, 2),
            )

        navigation = tk.Frame(
            self.root,
            bg="#111111",
        )

        navigation.pack(
            pady=(2, 5),
        )

        if page > 0:

            tk.Button(
                navigation,
                text="← PREV",
                command=lambda:
                    self.show_episode_page(
                        show_name,
                        season,
                        page - 1,
                    ),
                font=("DejaVu Sans", 11, "bold"),
                bg="#222222",
                fg="white",
                activebackground="#444444",
                activeforeground="white",
                relief="flat",
                cursor="hand2",
                width=10,
                height=1,
            ).grid(
                row=0,
                column=0,
                padx=5,
            )

        if page < total_pages - 1:

            tk.Button(
                navigation,
                text="NEXT →",
                command=lambda:
                    self.show_episode_page(
                        show_name,
                        season,
                        page + 1,
                    ),
                font=("DejaVu Sans", 11, "bold"),
                bg="#222222",
                fg="white",
                activebackground="#444444",
                activeforeground="white",
                relief="flat",
                cursor="hand2",
                width=10,
                height=1,
            ).grid(
                row=0,
                column=1,
                padx=5,
            )

        episode_frame = tk.Frame(
            self.root,
            bg="#111111",
        )

        episode_frame.pack(
            pady=2,
        )

        for episode in page_episodes:

            button = self.make_button(
                episode_frame,
                episode.stem,
                "#333333",
                "white",
                lambda e=episode:
                    self.play_episode(e),
            )

            button.config(
                width=42,
                height=1,
                font=("DejaVu Sans", 12, "bold"),
            )

            button.pack(
                pady=2,
            )

        self.make_back_button(
            lambda:
                self.show_show(show_name)
        )

    # =========================
    # RANDOM EPISODE
    # =========================

    def random_show_episode(self, show_name):
        episodes = []

        for season_episodes in (
            self.library["shows"][show_name].values()
        ):
            episodes.extend(season_episodes)

        if not episodes:
            return

        self.show_random_episode(
            show_name,
            episodes,
        )

    def show_random_episode(
        self,
        show_name,
        episodes,
    ):
        self.clear()

        self.set_background(show_name)

        episode = random.choice(episodes)

        tk.Label(
            self.root,
            text="🎲 RANDOM EPISODE",
            font=("DejaVu Sans", 28, "bold"),
            bg="#111111",
            fg="white",
        ).pack(
            pady=(80, 20),
        )

        tk.Label(
            self.root,
            text=episode.stem,
            font=("DejaVu Sans", 22, "bold"),
            bg="#333333",
            fg="white",
            padx=30,
            pady=20,
        ).pack(
            pady=20,
        )

        self.make_small_button(
            self.root,
            "🎲 REROLL",
            "#555555",
            "white",
            lambda:
                self.show_random_episode(
                    show_name,
                    episodes,
                ),
        ).pack(
            pady=5,
        )

        self.make_small_button(
            self.root,
            "▶ PLAY",
            "#356B3D",
            "white",
            lambda:
                self.play_random_selected(
                    episode,
                    show_name,
                ),
        ).pack(
            pady=5,
        )

        self.make_back_button(
            lambda:
                self.show_show(show_name)
        )

    def play_random_selected(
        self,
        episode,
        show_name,
    ):
        all_episodes = []

        for season_episodes in (
            self.library["shows"][show_name].values()
        ):
            all_episodes.extend(season_episodes)

        if not all_episodes:
            return

        start_index = all_episodes.index(
            episode
        )

        audio_track = None

        if show_name == "Alf":
            audio_track = 2

        self.root.withdraw()

        play_playlist(
            all_episodes,
            start_index=start_index,
            audio_track=audio_track,
        )

        self.root.deiconify()

    # =========================
    # NORMAL EPISODE PLAYBACK
    # =========================

    def play_episode(self, episode):
        show_name = None

        for name, seasons in (
            self.library["shows"].items()
        ):
            for season_episodes in seasons.values():

                if episode in season_episodes:
                    show_name = name
                    break

            if show_name:
                break

        # Movie
        if show_name is None:

            self.root.withdraw()

            play(str(episode))

            self.root.deiconify()

            return

        # Show
        all_episodes = []

        for season_episodes in (
            self.library["shows"][show_name].values()
        ):
            all_episodes.extend(
                season_episodes
            )

        if not all_episodes:
            return

        start_index = all_episodes.index(
            episode
        )

        audio_track = None

        if show_name == "Alf":
            audio_track = 2

        self.root.withdraw()

        play_playlist(
            all_episodes,
            start_index=start_index,
            audio_track=audio_track,
        )

        self.root.deiconify()

    # =========================
    # MOVIES
    # =========================

    def show_movies(self):
        self.show_movie_page(page=0)

    def show_movie_page(self, page=0):
        self.clear()

        self.root.configure(bg="#111111")

        movies = self.library["movies"]

        MOVIES_PER_PAGE = 10

        start = page * MOVIES_PER_PAGE
        end = start + MOVIES_PER_PAGE

        page_movies = movies[start:end]

        total_pages = (
            len(movies)
            + MOVIES_PER_PAGE
            - 1
        ) // MOVIES_PER_PAGE

        tk.Label(
            self.root,
            text="🎬 MOVIES",
            font=("DejaVu Sans", 28, "bold"),
            bg="#111111",
            fg="white",
        ).pack(
            pady=(15, 5),
        )

        if total_pages > 1:

            tk.Label(
                self.root,
                text=f"Page {page + 1} / {total_pages}",
                font=("DejaVu Sans", 10),
                bg="#111111",
                fg="#AAAAAA",
            ).pack(
                pady=(0, 3),
            )

        navigation = tk.Frame(
            self.root,
            bg="#111111",
        )

        navigation.pack(
            pady=(2, 4),
        )

        if page > 0:

            tk.Button(
                navigation,
                text="← PREV",
                command=lambda:
                    self.show_movie_page(
                        page - 1
                    ),
                font=("DejaVu Sans", 11, "bold"),
                bg="#222222",
                fg="white",
                activebackground="#444444",
                activeforeground="white",
                relief="flat",
                cursor="hand2",
                width=10,
                height=1,
            ).grid(
                row=0,
                column=0,
                padx=5,
            )

        if page < total_pages - 1:

            tk.Button(
                navigation,
                text="NEXT →",
                command=lambda:
                    self.show_movie_page(
                        page + 1
                    ),
                font=("DejaVu Sans", 11, "bold"),
                bg="#222222",
                fg="white",
                activebackground="#444444",
                activeforeground="white",
                relief="flat",
                cursor="hand2",
                width=10,
                height=1,
            ).grid(
                row=0,
                column=1,
                padx=5,
            )

        if movies:

            self.make_small_button(
                self.root,
                "🎲 RANDOM MOVIE",
                "#555555",
                "white",
                self.play_random_movie,
            ).pack(
                pady=(2, 5),
            )

        movie_frame = tk.Frame(
            self.root,
            bg="#111111",
        )

        movie_frame.pack(
            pady=2,
        )

        if not movies:

            tk.Label(
                movie_frame,
                text="No movies found.",
                font=("DejaVu Sans", 16),
                bg="#111111",
                fg="white",
            ).pack(
                pady=20,
            )

        else:

            for movie in page_movies:

                button = self.make_button(
                    movie_frame,
                    movie.stem,
                    "#333333",
                    "white",
                    lambda m=movie:
                        self.play_episode(m),
                )

                button.config(
                    width=42,
                    height=1,
                    font=("DejaVu Sans", 12, "bold"),
                )

                button.pack(
                    pady=2,
                )

        self.make_back_button(
            self.build_main_menu
        )

    # =========================
    # RANDOM MOVIE
    # =========================

    def play_random_movie(self):
        movies = self.library["movies"]

        if not movies:
            return

        self.show_random_movie(movies)

    def show_random_movie(self, movies):
        self.clear()

        self.root.configure(bg="#111111")

        movie = random.choice(movies)

        tk.Label(
            self.root,
            text="🎲 RANDOM MOVIE",
            font=("DejaVu Sans", 28, "bold"),
            bg="#111111",
            fg="white",
        ).pack(
            pady=(80, 20),
        )

        tk.Label(
            self.root,
            text=movie.stem,
            font=("DejaVu Sans", 22, "bold"),
            bg="#333333",
            fg="white",
            padx=30,
            pady=20,
        ).pack(
            pady=20,
        )

        self.make_small_button(
            self.root,
            "🎲 REROLL",
            "#555555",
            "white",
            lambda:
                self.show_random_movie(
                    movies
                ),
        ).pack(
            pady=5,
        )

        self.make_small_button(
            self.root,
            "▶ PLAY",
            "#356B3D",
            "white",
            lambda:
                self.play_selected_movie(
                    movie
                ),
        ).pack(
            pady=5,
        )

        self.make_back_button(
            self.show_movies
        )

    def play_selected_movie(self, movie):
        self.root.withdraw()

        play(str(movie))

        self.root.deiconify()

    # =========================
    # FIREPLACE
    # =========================

    def play_fireplace(self):
        if self.library["fireplace"]:

            self.root.withdraw()

            play(
                str(self.library["fireplace"]),
                loop=True,
            )

            self.root.deiconify()

    # =========================
    # RUN
    # =========================

    def run(self):
        self.root.mainloop()
