import tkinter as tk
from pathlib import Path

from PIL import Image, ImageTk

from library import random_episode
from player import play


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

        self.background_dir = Path(__file__).parent / "data" / "backgrounds"

        self.backgrounds = {
            "Simpsons": self.load_background("simpsons.jpeg"),
            "Alf": self.load_background("alf.jpeg"),
            "South Park": self.load_background("south-park.jpeg"),
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
        image = image.resize((1280, 720), Image.Resampling.LANCZOS)

        return ImageTk.PhotoImage(image)

    def set_background(self, show_name=None):
        # Remove old background
        if self.background_label:
            self.background_label.destroy()
            self.background_label = None

        # Main menu / screens without a background
        if show_name not in self.backgrounds:
            self.root.configure(bg="#111111")
            return

        self.background_image = self.backgrounds[show_name]

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

        # Keep background behind everything else
        self.background_label.lower()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.background_label = None
        self.background_image = None

    def make_button(self, parent, text, bg, fg, command):
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
        title.pack(pady=(40, 30))

        button_frame = tk.Frame(
            self.root,
            bg="#111111"
        )
        button_frame.pack(expand=True)

        # Simpsons
        self.make_button(
            button_frame,
            "SIMPSONS",
            "#F5C518",
            "black",
            lambda: self.show_show("Simpsons"),
        ).grid(row=0, column=0, padx=15, pady=15)

        # Alf
        self.make_button(
            button_frame,
            "ALF",
            "#A0522D",
            "white",
            lambda: self.show_show("Alf"),
        ).grid(row=0, column=1, padx=15, pady=15)

        # South Park
        self.make_button(
            button_frame,
            "SOUTH PARK",
            "#356B3D",
            "white",
            lambda: self.show_show("South Park"),
        ).grid(row=1, column=0, padx=15, pady=15)

        # Movies
        self.make_button(
            button_frame,
            "🎬 MOVIES",
            "#333333",
            "white",
            self.show_movies,
        ).grid(row=1, column=1, padx=15, pady=15)

        # Random TV
        self.make_button(
            button_frame,
            "🎲 RANDOM TV",
            "#5C3A8A",
            "white",
            self.random_tv,
        ).grid(
            row=2,
            column=0,
            padx=15,
            pady=15,
        )

        # Fireplace
        self.make_button(
            button_frame,
            "🔥 FIREPLACE",
            "#8B4513",
            "white",
            self.play_fireplace,
        ).grid(
            row=2,
            column=1,
            padx=15,
            pady=15,
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
        ).pack(pady=30)

        if show_name not in self.library["shows"]:

            tk.Label(
                self.root,
                text="This show isn't in the library yet.",
                font=("DejaVu Sans", 18),
                bg="#111111",
                fg="white",
            ).pack(pady=20)

        else:

            for season in self.library["shows"][show_name]:

                self.make_button(
                    self.root,
                    season,
                    "#333333",
                    "white",
                    lambda s=season: self.show_season(
                        show_name,
                        s,
                    ),
                ).pack(pady=6)

            # Random episode
            self.make_button(
                self.root,
                "🎲 RANDOM EPISODE",
                "#555555",
                "white",
                lambda: self.random_show_episode(show_name),
            ).pack(pady=20)

        tk.Button(
            self.root,
            text="← BACK",
            command=self.build_main_menu,
            font=("DejaVu Sans", 16),
            bg="#222222",
            fg="white",
            relief="flat",
            cursor="hand2",
        ).pack(side="bottom", pady=30)

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
        ).pack(pady=30)

        for episode in self.library["shows"][show_name][season]:

            self.make_button(
                self.root,
                episode.stem,
                "#333333",
                "white",
                lambda e=episode: self.play_episode(e),
            ).pack(pady=6)

        tk.Button(
            self.root,
            text="← BACK",
            command=lambda: self.show_show(show_name),
            font=("DejaVu Sans", 16),
            bg="#222222",
            fg="white",
            relief="flat",
            cursor="hand2",
        ).pack(side="bottom", pady=30)

    # =========================
    # RANDOM EPISODE
    # =========================

    def random_show_episode(self, show_name):
        episode = random_episode(
            self.library,
            show_name,
        )

        if episode:
            self.show_random_result(
                episode,
                show_name,
            )

    def show_random_result(self, episode, show_name):
        self.clear()

        self.set_background(show_name)

        tk.Label(
            self.root,
            text="🎲 RANDOM EPISODE",
            font=("DejaVu Sans", 30, "bold"),
            bg="#111111",
            fg="white",
        ).pack(pady=(50, 25))

        tk.Label(
            self.root,
            text=show_name,
            font=("DejaVu Sans", 20, "bold"),
            bg="#111111",
            fg="#AAAAAA",
        ).pack()

        tk.Label(
            self.root,
            text=episode.stem,
            font=("DejaVu Sans", 22),
            bg="#111111",
            fg="white",
            wraplength=900,
        ).pack(pady=20)

        button_frame = tk.Frame(
            self.root,
            bg="#111111",
        )

        button_frame.pack(pady=30)

        # WATCH
        self.make_button(
            button_frame,
            "▶ WATCH",
            "#2E7D32",
            "white",
            lambda: self.play_episode(episode),
        ).grid(
            row=0,
            column=0,
            padx=10,
        )

        # REROLL
        self.make_button(
            button_frame,
            "🎲 REROLL",
            "#555555",
            "white",
            lambda: self.reroll_episode(
                episode,
                show_name,
            ),
        ).grid(
            row=0,
            column=1,
            padx=10,
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
        ).pack(side="bottom", pady=30)

    def reroll_episode(self, current_episode, show_name):
        new_episode = random_episode(
            self.library,
            show_name,
        )

        while (
            new_episode == current_episode
            and len(self.library["shows"][show_name]) > 0
        ):
            new_episode = random_episode(
                self.library,
                show_name,
            )

        self.show_random_result(
            new_episode,
            show_name,
        )

    # =========================
    # RANDOM TV
    # =========================

    def random_tv(self):
        episode = random_episode(self.library)

        if episode:
            self.show_random_result(
                episode,
                "RANDOM TV",
            )

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
                ).pack(pady=6)

        tk.Button(
            self.root,
            text="← BACK",
            command=self.build_main_menu,
            font=("DejaVu Sans", 16),
            bg="#222222",
            fg="white",
            relief="flat",
            cursor="hand2",
        ).pack(side="bottom", pady=30)

    # =========================
    # PLAYER
    # =========================

    def play_episode(self, episode):
        self.root.withdraw()

        play(str(episode))

        self.root.deiconify()

    def play_fireplace(self):
        if self.library["fireplace"]:

            self.root.withdraw()

            play(
                str(self.library["fireplace"])
            )

            self.root.deiconify()

    # =========================
    # RUN
    # =========================

    def run(self):
        self.root.mainloop()
