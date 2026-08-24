import tkinter as tk
from pathlib import Path
import random

from PIL import Image, ImageTk

from player import play, play_playlist, play_random


class TVBox:
    def __init__(self, library):
        self.library = library

        self.root = tk.Tk()
        self.root.title("TV BOX")
        self.root.geometry("1280x720")
        self.root.configure(bg="#151515")

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
            "Friends": self.load_background("friends.jpeg"),
        }

        self.background_image = None
        self.background_label = None

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

    def set_background(self, show_name=None):
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

        # =========================
        # SHOWS
        # =========================

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

        # Friends
        self.make_button(
            button_frame,
            "FRIENDS",
            "#666666",
            "white",
            lambda: self.show_show("Friends"),
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
                    pady=4,
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
            ).pack(
                pady=6,
            )

        self.make_back_button(
            self.build_main_menu
        )

    # =========================
    # SEASON MENU
    # =========================

    def show_season(self, show_name, season):
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
            len(episodes) + EPISODES_PER_PAGE - 1
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

        # =========================
        # PAGE NAVIGATION
        # =========================

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
                command=lambda: self.show_episode_page(
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
                command=lambda: self.show_episode_page(
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

        # =========================
        # EPISODES
        # =========================

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
                lambda e=episode: self.play_episode(e),
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
            lambda: self.show_show(show_name)
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

        self.show_random_episode(
            show_name,
            episodes,
        )

    def show_random_episode(self, show_name, episodes):
        self.clear()

        self.set_background(show_name)

        episode = random.choice(episodes)

        self.random_episodes = episodes
        self.random_episode = episode
        self.random_show_name = show_name

        # =========================
        # TITLE
        # =========================

        tk.Label(
            self.root,
            text="🎲 RANDOM EPISODE",
            font=("DejaVu Sans", 28, "bold"),
            bg="#111111",
            fg="white",
        ).pack(
            pady=(80, 20),
        )

        # =========================
        # SELECTED EPISODE
        # =========================

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

        # =========================
        # REROLL
        # =========================

        tk.Button(
            self.root,
            text="🎲 REROLL",
            command=lambda: self.reroll_episode(
                show_name,
                episodes,
            ),
            font=("DejaVu Sans", 16, "bold"),
            bg="#555555",
            fg="white",
            activebackground="#666666",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            width=16,
            height=2,
        ).pack(
            pady=8,
        )

        # =========================
        # PLAY
        # =========================

        tk.Button(
            self.root,
            text="▶ PLAY",
            command=lambda: self.play_random_selected(
                episode,
                show_name,
            ),
            font=("DejaVu Sans", 16, "bold"),
            bg="#356B3D",
            fg="white",
            activebackground="#467C4D",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            width=16,
            height=2,
        ).pack(
            pady=8,
        )

        self.make_back_button(
            lambda: self.show_show(show_name)
        )

    def reroll_episode(self, show_name, episodes):
        self.clear()

        self.set_background(show_name)

        episode = random.choice(episodes)

        self.random_episodes = episodes
        self.random_episode = episode
        self.random_show_name = show_name

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

        tk.Button(
            self.root,
            text="🎲 REROLL",
            command=lambda: self.reroll_episode(
                show_name,
                episodes,
            ),
            font=("DejaVu Sans", 16, "bold"),
            bg="#555555",
            fg="white",
            activebackground="#666666",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            width=16,
            height=2,
        ).pack(
            pady=8,
        )

        tk.Button(
            self.root,
            text="▶ PLAY",
            command=lambda: self.play_random_selected(
                episode,
                show_name,
            ),
            font=("DejaVu Sans", 16, "bold"),
            bg="#356B3D",
            fg="white",
            activebackground="#467C4D",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            width=16,
            height=2,
        ).pack(
            pady=8,
        )

        self.make_back_button(
            lambda: self.show_show(show_name)
        )

    def play_random_selected(self, episode, show_name):
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
    # NORMAL EPISODE PLAYBACK
    # =========================

    def play_episode(self, episode):
        show_name = None

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
            len(movies) + MOVIES_PER_PAGE - 1
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

        # =========================
        # PAGE NAVIGATION
        # =========================

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
                command=lambda: self.show_movie_page(
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
                command=lambda: self.show_movie_page(
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

        # =========================
        # RANDOM MOVIE
        # =========================

        if movies:

            tk.Button(
                self.root,
                text="🎲 RANDOM MOVIE",
                command=self.play_random_movie,
                font=("DejaVu Sans", 11, "bold"),
                bg="#555555",
                fg="white",
                activebackground="#666666",
                activeforeground="white",
                relief="flat",
                cursor="hand2",
                width=18,
                height=1,
            ).pack(
                pady=(2, 5),
            )

        # =========================
        # MOVIE LIST
        # =========================

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
                    lambda m=movie: self.play_episode(m),
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

        self.random_movie = movie
        self.random_movies = movies

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

        # REROLL
        tk.Button(
            self.root,
            text="🎲 REROLL",
            command=lambda: self.show_random_movie(movies),
            font=("DejaVu Sans", 16, "bold"),
            bg="#555555",
            fg="white",
            activebackground="#666666",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            width=16,
            height=2,
        ).pack(
            pady=8,
        )

        # PLAY
        tk.Button(
            self.root,
            text="▶ PLAY",
            command=lambda: self.play_selected_movie(movie),
            font=("DejaVu Sans", 16, "bold"),
            bg="#356B3D",
            fg="white",
            activebackground="#467C4D",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            width=16,
            height=2,
        ).pack(
            pady=8,
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
