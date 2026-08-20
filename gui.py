import tkinter as tk
from pathlib import Path

from PIL import Image, ImageTk

from library import random_episode
from player import play, play_playlist, play_random


class TVBox:
    def __init__(self, library):
        self.library = library

        self.root = tk.Tk()
        self.root.title("TV BOX")
        self.root.geometry("1280x720")
        self.root.configure(bg="#111111")

        # =========================
        # BACKGROUNDS
        # =========================

        self.background_dir = (
            Path(__file__).parent
            / "data"
            / "backgrounds"
        )

        self.backgrounds = {
            "Simpsons": self.load_background("simpsons.jpeg"),
            "Futurama": self.load_background("futurama.jpeg"),
            "Alf": self.load_background("alf.jpeg"),
            "South Park": self.load_background("south-park.jpeg"),
            "SpongeBob": self.load_background("spongebob.jpeg"),
        }

        self.background_image = None
        self.background_label = None

        self.build_main_menu()

    # =========================
    # BACKGROUND
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

    def set_background(self, show_name=None):
        if self.background_label:
            self.background_label.destroy()
            self.background_label = None

        if show_name not in self.backgrounds:
            self.root.configure(bg="#111111")
            return

        image = self.backgrounds[show_name]

        if image is None:
            self.root.configure(bg="#111111")
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

    # =========================
    # MAIN MENU
    # =========================

    def build_main_menu(self):
        self.clear()

        self.root.configure(bg="#111111")

        title = tk.Label(
            self.root,
            text="📺 TV BOX",
            font=("DejaVu Sans", 32, "bold"),
            bg="#111111",
            fg="white",
        )

        title.pack(pady=(30, 20))

        button_frame = tk.Frame(
            self.root,
            bg="#111111",
        )

        button_frame.pack(expand=True)

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
            padx=15,
            pady=10,
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
            padx=15,
            pady=10,
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
            padx=15,
            pady=10,
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
            padx=15,
            pady=10,
        )

        # SpongeBob
        self.make_button(
            button_frame,
            "SPONGEBOB",
            "#E7C600",
            "black",
            lambda: self.show_show("SpongeBob"),
        ).grid(
            row=2,
            column=0,
            padx=15,
            pady=10,
        )

        # Movies
        self.make_button(
            button_frame,
            "🎬 MOVIES",
            "#333333",
            "white",
            self.show_movies,
        ).grid(
            row=2,
            column=1,
            padx=15,
            pady=10,
        )

        # Fireplace
        self.make_button(
            button_frame,
            "🔥 FIREPLACE",
            "#8B4513",
            "white",
            self.play_fireplace,
        ).grid(
            row=3,
            column=0,
            columnspan=2,
            padx=15,
            pady=10,
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
            font=("DejaVu Sans", 32, "bold"),
            bg="#111111",
            fg="white",
        ).pack(pady=(20, 15))

        if show_name not in self.library["shows"]:

            tk.Label(
                self.root,
                text="This show isn't in the library yet.",
                font=("DejaVu Sans", 18),
                bg="#111111",
                fg="white",
            ).pack(pady=20)

        else:

            season_frame = tk.Frame(
                self.root,
                bg="#111111",
            )

            season_frame.pack(
                expand=True,
                pady=5,
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
                    lambda s=season: self.show_season(
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
                    pady=5,
                )

            # Random episode
            self.make_button(
                self.root,
                "🎲 RANDOM EPISODE",
                "#555555",
                "white",
                lambda: self.random_show_episode(
                    show_name
                ),
            ).pack(pady=8)

        tk.Button(
            self.root,
            text="← BACK",
            command=self.build_main_menu,
            font=("DejaVu Sans", 16),
            bg="#222222",
            fg="white",
            relief="flat",
            cursor="hand2",
        ).pack(
            side="bottom",
            pady=12,
        )

    # =========================
    # SEASON MENU
    # =========================

    def show_season(self, show_name, season):
        self.clear()

        self.set_background(show_name)

        tk.Label(
            self.root,
            text=f"{show_name} — {season}",
            font=("DejaVu Sans", 28, "bold"),
            bg="#111111",
            fg="white",
        ).pack(pady=25)

        episode_frame = tk.Frame(
            self.root,
            bg="#111111",
        )

        episode_frame.pack(
            expand=True,
        )

        for episode in self.library["shows"][show_name][season]:

            self.make_button(
                episode_frame,
                episode.stem,
                "#333333",
                "white",
                lambda e=episode: self.play_episode(e),
            ).pack(
                pady=6,
            )

        tk.Button(
            self.root,
            text="← BACK",
            command=lambda: self.show_show(show_name),
            font=("DejaVu Sans", 16),
            bg="#222222",
            fg="white",
            relief="flat",
            cursor="hand2",
        ).pack(
            side="bottom",
            pady=15,
        )

    # =========================
    # RANDOM EPISODE
    # =========================

    def random_show_episode(self, show_name):
        episodes = []

        for season_episodes in self.library["shows"][show_name].values():
            episodes.extend(season_episodes)

        if not episodes:
            return

        self.root.withdraw()

        audio_track = None

        if show_name == "Alf":
            audio_track = 2

        play_random(
            episodes,
            audio_track=audio_track,
        )

        self.root.deiconify()

    # =========================
    # NORMAL EPISODE PLAYBACK
    # =========================

    def play_episode(self, episode):
        show_name = None

        # Find which show the episode belongs to
        for name, seasons in self.library["shows"].items():

            for season_episodes in seasons.values():

                if episode in season_episodes:
                    show_name = name
                    break

            if show_name:
                break

        # =========================
        # MOVIE
        # =========================

        if show_name is None:

            self.root.withdraw()

            play(str(episode))

            self.root.deiconify()

            return

        # =========================
        # SHOW
        # =========================

        all_episodes = []

        for season_episodes in self.library["shows"][show_name].values():
            all_episodes.extend(season_episodes)

        if not all_episodes:
            return

        start_index = all_episodes.index(episode)

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
        self.clear()

        self.root.configure(bg="#111111")

        tk.Label(
            self.root,
            text="🎬 MOVIES",
            font=("DejaVu Sans", 30, "bold"),
            bg="#111111",
            fg="white",
        ).pack(pady=30)

        if not self.library["movies"]:

            tk.Label(
                self.root,
                text="No movies found.",
                font=("DejaVu Sans", 18),
                bg="#111111",
                fg="white",
            ).pack()

        else:

            for movie in self.library["movies"]:

                self.make_button(
                    self.root,
                    movie.stem,
                    "#333333",
                    "white",
                    lambda m=movie: self.play_episode(m),
                ).pack(
                    pady=6,
                )

        tk.Button(
            self.root,
            text="← BACK",
            command=self.build_main_menu,
            font=("DejaVu Sans", 16),
            bg="#222222",
            fg="white",
            relief="flat",
            cursor="hand2",
        ).pack(
            side="bottom",
            pady=15,
        )

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
