import tkinter as tk
from pathlib import Path
from datetime import date
import random
import time
import subprocess

from PIL import Image, ImageTk

from library import scan_all_media
from player import play, play_playlist


class TVBox:
    def __init__(self, library):
        self.library = library

        self.root = tk.Tk()
        self.root.title("TV BOX")
        self.root.geometry("1280x720")
        self.root.configure(bg="#111111")

        # SLEEP TIMER
        self.sleep_timer_job = None
        self.sleep_deadline = None
        self.sleep_button = None

        # MEDIA
        self.media_dir = Path.home() / "Videos"

        # BACKGROUNDS
        self.background_dir = Path(__file__).parent / "data" / "backgrounds"
        self.movie_background_dir = self.background_dir / "movies"

        self.backgrounds = {
            "Simpsons": self.load_background("simpsons.jpeg"),
            "Futurama": self.load_background("futurama.jpeg"),
            "Alf": self.load_background("alf.jpeg"),
            "South Park": self.load_background("south-park.jpeg"),
            "SpongeBob": self.load_background("spongebob.jpeg"),
        }

        self.background_image = None
        self.background_label = None

        # Animated event background
        self.event_background = None
        self.event_frames = []
        self.event_frame_index = 0
        self.event_animation_job = None

        # Birthday confetti
        self.confetti_canvas = None
        self.confetti_particles = []
        self.confetti_animation_job = None

        # PAGE MEMORY
        self.page_memory = {
            "movies": 0,
            "classics": {},
            "shows": {},
            "events": {},
        }

        self.build_main_menu()

    # ==============================================
    # SLEEP TIMER
    # ==============================================

    def toggle_sleep_timer(self):
        if self.sleep_timer_job is not None:
            self.cancel_sleep_timer()
        else:
            self.sleep_deadline = time.time() + 1200
            self.update_sleep_button()

    def update_sleep_button(self):
        if self.sleep_deadline is None:
            return

        remaining = int(self.sleep_deadline - time.time())

        if remaining <= 0:
            self.sleep_timer_job = None
            self.sleep_deadline = None
            self.suspend_system()
            return

        minutes = remaining // 60
        seconds = remaining % 60

        if self.sleep_button is not None:
            try:
                self.sleep_button.config(
                    text=f"SLEEP {minutes:02d}:{seconds:02d}",
                    bg="#8B0000",
                    fg="white",
                )
            except tk.TclError:
                self.sleep_button = None

        self.sleep_timer_job = self.root.after(1000, self.update_sleep_button)

    def cancel_sleep_timer(self):
        if self.sleep_timer_job is not None:
            try:
                self.root.after_cancel(self.sleep_timer_job)
            except tk.TclError:
                pass

        self.sleep_timer_job = None
        self.sleep_deadline = None

        if self.sleep_button is not None:
            try:
                self.sleep_button.config(
                    text="SLEEP",
                    bg="#222222",
                    fg="white",
                )
            except tk.TclError:
                self.sleep_button = None

    def suspend_system(self):
        self.sleep_timer_job = None
        self.sleep_deadline = None
        self.sleep_button = None
        self.root.withdraw()
        subprocess.run(["systemctl", "suspend"])

    # ==============================================
    # BACKGROUNDS
    # ==============================================

    def load_background(self, filename):
        path = self.background_dir / filename
        if not path.exists():
            print(f"Background not found: {path}")
            return None

        try:
            image = Image.open(path)
            image = image.resize((1280, 720), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(image)
        except Exception as error:
            print(f"Could not load background {path}: {error}")
            return None

    def find_artwork(self, name):
        if not self.movie_background_dir.exists():
            return None

        name = Path(name).stem.casefold()
        supported_extensions = {".jpg", ".jpeg", ".png", ".webp"}

        try:
            for artwork in self.movie_background_dir.iterdir():
                if not artwork.is_file():
                    continue
                if artwork.suffix.lower() not in supported_extensions:
                    continue
                if artwork.stem.casefold() == name:
                    return artwork
        except OSError as error:
            print(f"Could not search artwork: {error}")

        return None

    def set_artwork_background(self, name):
        artwork = self.find_artwork(name)
        if artwork is None:
            self.set_background(None)
            return

        try:
            image = Image.open(artwork)
            image = image.resize((1280, 720), Image.Resampling.LANCZOS)
            self.background_image = ImageTk.PhotoImage(image)
            self.background_label = tk.Label(
                self.root,
                image=self.background_image,
                borderwidth=0,
            )
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.background_label.lower()
        except Exception as error:
            print(f"Could not load artwork background {artwork}: {error}")
            self.set_background(None)

    def find_movie_background(self, movie):
        return self.find_artwork(movie)

    def set_movie_background(self, movie):
        self.set_artwork_background(movie)

    def set_classics_folder_background(self, folder):
        self.set_artwork_background(folder.name)

    def get_show_for_episode(self, episode):
        for show_name, seasons in self.library["shows"].items():
            for season_episodes in seasons.values():
                if episode in season_episodes:
                    return show_name
        return None

    def set_random_background(self, media_file):
        show_name = self.get_show_for_episode(media_file)
        if show_name is not None:
            self.set_background(show_name)
            return

        if media_file in self.library["movies"]:
            self.set_movie_background(media_file)
            return

        self.set_background(None)

    def stop_event_animation(self):
        if self.event_animation_job is not None:
            try:
                self.root.after_cancel(self.event_animation_job)
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

            if getattr(image, "n_frames", 1) > 1:
                self.event_frames = []
                for frame_number in range(image.n_frames):
                    image.seek(frame_number)
                    frame = image.convert("RGB")
                    frame = frame.resize((1280, 720), Image.Resampling.LANCZOS)
                    self.event_frames.append(ImageTk.PhotoImage(frame))

                if not self.event_frames:
                    return False

                self.event_frame_index = 0
                self.background_image = self.event_frames[0]
                self.background_label = tk.Label(
                    self.root,
                    image=self.background_image,
                    borderwidth=0,
                )
                self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
                self.background_label.lower()
                self.animate_event_background()
                return True

            image = image.resize((1280, 720), Image.Resampling.LANCZOS)
            self.event_background = ImageTk.PhotoImage(image)
            self.background_image = self.event_background
            self.background_label = tk.Label(
                self.root,
                image=self.background_image,
                borderwidth=0,
            )
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.background_label.lower()
            return True
        except Exception as error:
            print(f"Could not load event background: {error}")
            return False

    def animate_event_background(self):
        if not self.event_frames or not self.background_label:
            return

        self.event_frame_index += 1
        if self.event_frame_index >= len(self.event_frames):
            self.event_frame_index = 0

        self.background_image = self.event_frames[self.event_frame_index]
        self.background_label.configure(image=self.background_image)
        self.event_animation_job = self.root.after(100, self.animate_event_background)

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
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.background_label.lower()

    # ==============================================
    # GENERAL UI
    # ==============================================

    def stop_confetti_animation(self):
        if self.confetti_animation_job is not None:
            try:
                self.root.after_cancel(self.confetti_animation_job)
            except tk.TclError:
                pass
            self.confetti_animation_job = None

        self.confetti_particles = []

        if self.confetti_canvas is not None:
            try:
                self.confetti_canvas.destroy()
            except tk.TclError:
                pass
            self.confetti_canvas = None

    def start_confetti_animation(self):
        self.stop_confetti_animation()

        self.confetti_canvas = tk.Canvas(
            self.root,
            width=1280,
            height=720,
            bg="#111111",
            highlightthickness=0,
            bd=0,
        )

        self.confetti_canvas.place(
            x=0,
            y=0,
            relwidth=1,
            relheight=1,
        )

        # Keep the confetti behind the rest of the UI.
        self.root.tk.call(
            "lower",
            self.confetti_canvas._w,
        )

        confetti_colors = [
            "#FF5252",
            "#FFD740",
            "#40C4FF",
            "#69F0AE",
            "#E040FB",
            "#FFFFFF",
            "#FF6E40",
        ]

        for _ in range(100):
            x = random.randint(0, 1280)
            y = random.randint(-720, 0)
            size = random.randint(5, 12)
            vx = random.uniform(-1.2, 1.2)
            vy = random.uniform(1.5, 4.5)

            item = self.confetti_canvas.create_rectangle(
                x,
                y,
                x + size,
                y + size,
                fill=random.choice(confetti_colors),
                outline="",
            )

            self.confetti_particles.append({
                "item": item,
                "x": x,
                "y": y,
                "vx": vx,
                "vy": vy,
                "size": size,
            })

        self.animate_confetti()

    def animate_confetti(self):
        if self.confetti_canvas is None:
            return

        for particle in self.confetti_particles:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["vy"] += 0.04

            if particle["y"] > 720:
                particle["x"] = random.randint(0, 1280)
                particle["y"] = random.randint(-60, -5)
                particle["vx"] = random.uniform(-1.2, 1.2)
                particle["vy"] = random.uniform(1.5, 4.5)

            size = particle["size"]

            self.confetti_canvas.coords(
                particle["item"],
                particle["x"],
                particle["y"],
                particle["x"] + size,
                particle["y"] + size,
            )

        self.confetti_animation_job = self.root.after(
            30,
            self.animate_confetti,
        )

    def clear(self):
        self.stop_event_animation()

        # Birthday confetti may follow us between screens, but only on
        # the two birthday dates. On every other day it is always removed.
        if self.get_birthday_text() is None:
            self.stop_confetti_animation()

        for widget in self.root.winfo_children():
            if widget is self.confetti_canvas:
                continue
            widget.destroy()
        self.background_label = None
        self.background_image = None
        self.sleep_button = None

    def lighten_color(self, color):
        """Return a slightly brighter version of a hex color for hover effects."""
        color = color.lstrip("#")
        if len(color) != 6:
            return "#666666"

        rgb = [int(color[index:index + 2], 16) for index in (0, 2, 4)]
        rgb = [min(255, value + 28) for value in rgb]
        return "#" + "".join(f"{value:02X}" for value in rgb)

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

    def make_small_button(self, parent, text, bg, fg, command):
        return tk.Button(
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

    def make_nav_button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("DejaVu Sans", 11, "bold"),
            bg="#222222",
            fg="white",
            relief="flat",
            cursor="hand2",
            width=10,
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
        ).place(relx=0.98, rely=0.02, anchor="ne")

    # ==============================================
    # SLEEP BUTTON
    # ==============================================

    def make_sleep_button(self):
        if self.sleep_deadline is not None:
            remaining = int(self.sleep_deadline - time.time())
            if remaining > 0:
                minutes = remaining // 60
                seconds = remaining % 60
                text = f"SLEEP {minutes:02d}:{seconds:02d}"
                bg = "#8B0000"
            else:
                text = "SLEEP"
                bg = "#222222"
        else:
            text = "SLEEP"
            bg = "#222222"

        self.sleep_button = tk.Button(
            self.root,
            text=text,
            command=self.toggle_sleep_timer,
            font=("DejaVu Sans", 11, "bold"),
            bg=bg,
            fg="white",
            activebackground="#444444",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            width=11,
        )
        self.sleep_button.place(relx=0.02, rely=0.02, anchor="nw")

    # ==============================================
    # BIRTHDAYS
    # ==============================================

    def get_birthday_text(self):
        today = date.today()

        birthdays = {
            (4, 24): date(1996, 4, 24),
            (5, 25): date(1998, 5, 25),
        }

        birth_date = birthdays.get(
            (today.month, today.day)
        )

        if birth_date is None:
            return None

        age = today.year - birth_date.year

        if (today.month, today.day) < (
            birth_date.month,
            birth_date.day,
        ):
            age -= 1

        return f"HAPPY {age}"

    # ==============================================
    # EVENTS
    # ==============================================

    def get_current_event(self):
        today = date.today()

        if today.month == 10 and today.day >= 30:
            return "halloween"
        if today.month == 11 and today.day == 1:
            return "halloween"
        if today.month == 12:
            return "christmas"
        if today.month == 1 and today.day <= 10:
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
            return "white"
        return "#666666"

    def handle_event_button(self):
        event = self.get_current_event()
        if event:
            self.show_event_screen(event)
        else:
            self.show_random_normal()

    # ==============================================
    # MAIN MENU
    # ==============================================

    def build_main_menu(self):
        self.clear()
        self.root.configure(bg="#111111")
        self.make_sleep_button()

        title = tk.Label(
            self.root,
            text="📺 TV BOX",
            font=("DejaVu Sans", 30, "bold"),
            bg="#111111",
            fg="white",
        )
        title.pack(pady=(28, 2))

        birthday_text = self.get_birthday_text()

        if birthday_text:
            self.start_confetti_animation()
        else:
            self.stop_confetti_animation()

        subtitle = tk.Label(
            self.root,
            text=birthday_text or "v1.0",
            font=("DejaVu Sans", 11, "bold"),
            bg="#111111",
            fg="#777777",
        )
        subtitle.pack(pady=(0, 18))

        show_frame = tk.Frame(self.root, bg="#111111")
        show_frame.pack()

        def show_card(text, color, command, row, column, fg="white", dark=None):
            dark = dark or "#181818"
            card = tk.Frame(
                show_frame,
                bg=dark,
                padx=3,
                pady=3,
            )
            card.grid(row=row, column=column, padx=9, pady=9)

            button = tk.Button(
                card,
                text=text,
                command=command,
                font=("DejaVu Sans", 17, "bold"),
                bg=color,
                fg=fg,
                activebackground=color,
                activeforeground=fg,
                relief="flat",
                bd=0,
                width=16,
                height=2,
                cursor="hand2",
            )
            button.pack()

            accent = tk.Frame(card, bg=color, height=4)
            accent.pack(fill="x", pady=(3, 0))

            hover_color = self.lighten_color(color)
            button.bind("<Enter>", lambda event, c=hover_color: button.config(bg=c))
            button.bind("<Leave>", lambda event, c=color: button.config(bg=c))

        show_card("SIMPSONS", "#F6C945", lambda: self.show_show("Simpsons"), 0, 0, "white", "#3A2F08")
        show_card("FUTURAMA", "#4A148C", lambda: self.show_show("Futurama"), 0, 1, "white", "#0B3045")
        show_card("ALF", "#B8663C", lambda: self.show_show("Alf"), 1, 0, "white", "#3E1F13")
        show_card("SOUTH PARK", "#2E5D34", lambda: self.show_show("South Park"), 1, 1, "white", "#183A20")
        show_card("SPONGEBOB", "#42A5F5", lambda: self.show_show("SpongeBob"), 2, 0, "white", "#4A2020")

        mystery_color = self.get_event_button_color()
        mystery_text = self.get_event_button_text()
        mystery = tk.Frame(
            show_frame,
            bg="#251B32" if self.get_current_event() == "halloween" else "#2A1C1C" if self.get_current_event() == "christmas" else "#202020",
            padx=3,
            pady=3,
        )
        mystery.grid(row=2, column=1, padx=9, pady=9)

        mystery_fg = "#B71C1C" if self.get_current_event() == "christmas" else "white"
        mystery_button = tk.Button(
            mystery,
            text=mystery_text,
            command=self.handle_event_button,
            font=("DejaVu Sans", 17, "bold"),
            bg=mystery_color,
            fg=mystery_fg,
            activebackground=mystery_color,
            activeforeground=mystery_fg,
            relief="flat",
            bd=0,
            width=16,
            height=2,
            cursor="hand2",
        )
        mystery_button.pack()
        mystery_accent = tk.Frame(mystery, bg=mystery_color, height=4)
        mystery_accent.pack(fill="x", pady=(3, 0))
        if mystery_color != "white":
            mystery_hover = self.lighten_color(mystery_color)
            mystery_button.bind("<Enter>", lambda event, c=mystery_hover: mystery_button.config(bg=c))
            mystery_button.bind("<Leave>", lambda event, c=mystery_color: mystery_button.config(bg=c))

        tk.Frame(self.root, bg="#333333", height=2, width=650).pack(pady=(14, 12))
        utility_frame = tk.Frame(self.root, bg="#111111")
        utility_frame.pack()

        movies_button = tk.Button(
            utility_frame,
            text="🎬  CLASSICS",
            command=self.show_movies,
            font=("DejaVu Sans", 15, "bold"),
            bg="#292929",
            fg="white",
            activebackground="#444444",
            activeforeground="white",
            relief="flat",
            bd=0,
            width=18,
            height=2,
            cursor="hand2",
        )
        movies_button.grid(row=0, column=0, padx=7)

        fireplace_button = tk.Button(
            utility_frame,
            text="🔥  FIREPLACE",
            command=self.play_fireplace,
            font=("DejaVu Sans", 15, "bold"),
            bg="#C62828",
            fg="white",
            activebackground="#E53935",
            activeforeground="white",
            relief="flat",
            bd=0,
            width=18,
            height=2,
            cursor="hand2",
        )
        fireplace_button.grid(row=0, column=1, padx=7)

        tk.Label(
            self.root,
            text="© 2026",
            font=("DejaVu Sans", 9),
            bg="#111111",
            fg="#555555",
        ).pack(pady=(12, 0))

    # ==============================================
    # UNIVERSAL RANDOM
    # ==============================================

    def get_all_media(self):
        return scan_all_media(self.media_dir)

    def show_random_normal(self):
        media = self.get_all_media()
        if not media:
            return

        selected = random.choice(media)
        self.clear()
        self.set_random_background(selected)

        tk.Label(
            self.root,
            text="❔ RANDOM",
            font=("DejaVu Sans", 30, "bold"),
            bg="#151515",
            fg="white",
        ).pack(pady=(70, 25))

        tk.Label(
            self.root,
            text=selected.stem,
            font=("DejaVu Sans", 22, "bold"),
            bg="#333333",
            fg="white",
            padx=35,
            pady=20,
        ).pack(pady=20)

        self.make_small_button(self.root, "🎲 REROLL", "#555555", "white", self.show_random_normal).pack(pady=5)
        self.make_small_button(
            self.root,
            "▶ PLAY",
            "#356B3D",
            "white",
            lambda: self.play_random_media(selected),
        ).pack(pady=5)
        self.make_back_button(self.build_main_menu)

    def play_random_media(self, selected):
        self.root.withdraw()
        play(str(selected))
        self.root.deiconify()

    # ==============================================
    # SHOWS
    # ==============================================

    def show_show(self, show_name):
        self.clear()
        self.set_background(show_name)

        tk.Label(
            self.root,
            text=show_name,
            font=("DejaVu Sans", 28, "bold"),
            bg="#111111",
            fg="white",
        ).pack(pady=(15, 10))

        if show_name not in self.library["shows"]:
            tk.Label(
                self.root,
                text="This show isn't in the library yet.",
                font=("DejaVu Sans", 18),
                bg="#111111",
                fg="white",
            ).pack(pady=20)
        else:
            season_frame = tk.Frame(self.root, bg="#111111")
            season_frame.pack(expand=True, pady=3)

            seasons = list(self.library["shows"][show_name].keys())
            seasons.sort(key=lambda s: int(''.join(filter(str.isdigit, s))))

            for index, season in enumerate(seasons):
                row = index // 4
                column = index % 4
                button = self.make_button(
                    season_frame,
                    season,
                    "#333333",
                    "white",
                    lambda s=season: self.show_season(show_name, s),
                )
                button.config(width=12, height=2, font=("DejaVu Sans", 16, "bold"))
                button.grid(row=row, column=column, padx=8, pady=4)

            self.make_button(
                self.root,
                "🎲 RANDOM EPISODE",
                "#555555",
                "white",
                lambda: self.random_show_episode(show_name),
            ).pack(pady=6)

        self.make_back_button(self.build_main_menu)

    # ==============================================
    # EPISODES
    # ==============================================

    def show_season(self, show_name, season):
        key = (show_name, season)
        page = self.page_memory["shows"].get(key, 0)
        self.show_episode_page(show_name, season, page)

    def show_episode_page(self, show_name, season, page=0):
        self.clear()
        self.set_background(show_name)
        episodes = self.library["shows"][show_name][season]
        EPISODES_PER_PAGE = 10

        total_pages = (len(episodes) + EPISODES_PER_PAGE - 1) // EPISODES_PER_PAGE
        if total_pages == 0:
            total_pages = 1

        page = min(page, total_pages - 1)
        self.page_memory["shows"][(show_name, season)] = page
        start = page * EPISODES_PER_PAGE
        end = start + EPISODES_PER_PAGE
        page_episodes = episodes[start:end]

        tk.Label(
            self.root,
            text=f"{show_name} — {season}",
            font=("DejaVu Sans", 24, "bold"),
            bg="#111111",
            fg="white",
        ).pack(pady=(10, 2))

        tk.Label(
            self.root,
            text=f"Page {page + 1} / {total_pages}",
            font=("DejaVu Sans", 10),
            bg="#111111",
            fg="#AAAAAA",
        ).pack(pady=(0, 2))

        navigation = tk.Frame(self.root, bg="#111111")
        navigation.pack(pady=(2, 5))

        if page > 0:
            self.make_nav_button(
                navigation,
                "← PREV",
                lambda: self.show_episode_page(show_name, season, page - 1),
            ).grid(row=0, column=0, padx=5)

        if page < total_pages - 1:
            self.make_nav_button(
                navigation,
                "NEXT →",
                lambda: self.show_episode_page(show_name, season, page + 1),
            ).grid(row=0, column=1, padx=5)

        episode_frame = tk.Frame(self.root, bg="#111111")
        episode_frame.pack(pady=2)

        for episode in page_episodes:
            button = self.make_button(
                episode_frame,
                episode.stem,
                "#333333",
                "white",
                lambda e=episode: self.play_episode(e),
            )
            button.config(width=42, height=1, font=("DejaVu Sans", 12, "bold"))
            button.pack(pady=2)

        self.make_back_button(lambda: self.show_show(show_name))

    # ==============================================
    # RANDOM EPISODE
    # ==============================================

    def random_show_episode(self, show_name):
        episodes = []
        for season_episodes in self.library["shows"][show_name].values():
            episodes.extend(season_episodes)
        if not episodes:
            return
        self.show_random_episode(show_name, episodes)

    def show_random_episode(self, show_name, episodes):
        self.clear()
        self.set_background(show_name)
        episode = random.choice(episodes)

        tk.Label(
            self.root,
            text="🎲 RANDOM EPISODE",
            font=("DejaVu Sans", 28, "bold"),
            bg="#111111",
            fg="white",
        ).pack(pady=(80, 20))

        tk.Label(
            self.root,
            text=episode.stem,
            font=("DejaVu Sans", 22, "bold"),
            bg="#333333",
            fg="white",
            padx=30,
            pady=20,
        ).pack(pady=20)

        self.make_small_button(
            self.root,
            "🎲 REROLL",
            "#555555",
            "white",
            lambda: self.show_random_episode(show_name, episodes),
        ).pack(pady=5)

        self.make_small_button(
            self.root,
            "▶ PLAY",
            "#356B3D",
            "white",
            lambda: self.play_random_selected(episode, show_name),
        ).pack(pady=5)

        self.make_back_button(lambda: self.show_show(show_name))

    def play_random_selected(self, episode, show_name):
        all_episodes = []
        for season_episodes in self.library["shows"][show_name].values():
            all_episodes.extend(season_episodes)
        if not all_episodes:
            return

        start_index = all_episodes.index(episode)
        audio_track = 2 if show_name == "Alf" else None

        self.root.withdraw()
        play_playlist(all_episodes, start_index=start_index, audio_track=audio_track)
        self.root.deiconify()

    # ==============================================
    # PLAY EPISODE / MOVIE
    # ==============================================

    def play_episode(self, episode):
        show_name = self.get_show_for_episode(episode)

        if show_name is None:
            self.root.withdraw()
            play(str(episode))
            self.root.deiconify()
            return

        all_episodes = []
        for season_episodes in self.library["shows"][show_name].values():
            all_episodes.extend(season_episodes)
        if not all_episodes:
            return

        start_index = all_episodes.index(episode)
        audio_track = 2 if show_name == "Alf" else None

        self.root.withdraw()
        play_playlist(all_episodes, start_index=start_index, audio_track=audio_track)
        self.root.deiconify()

    # ==============================================
    # MOVIES / CLASSICS WITH FOLDER SUPPORT
    # ==============================================

    def get_classics_entries(self, folder):
        """Return immediate files and folders inside a Classics folder."""
        if not folder.exists() or not folder.is_dir():
            return []

        try:
            entries = [entry for entry in folder.iterdir() if not entry.name.startswith(".")]
        except OSError as error:
            print(f"Could not read Classics folder {folder}: {error}")
            return []

        folders = sorted(
            [entry for entry in entries if entry.is_dir()],
            key=lambda path: path.name.casefold(),
        )
        files = sorted(
            [entry for entry in entries if entry.is_file()],
            key=lambda path: path.name.casefold(),
        )

        return folders + files

    def is_classics_root_folder(self, path):
        """Hide folders already managed as TV shows or seasonal media."""
        if path.name.casefold() in {"halloween", "christmas"}:
            return True

        show_names = {
            name.casefold()
            for name in self.library["shows"].keys()
        }

        return path.name.casefold() in show_names

    def get_classics_root_entries(self):
        """Return root-level Classics files and user-created folders."""
        entries = self.get_classics_entries(self.media_dir)

        filtered = []
        fireplace = self.library.get("fireplace")

        for entry in entries:
            if entry.is_dir() and self.is_classics_root_folder(entry):
                continue

            if fireplace and entry == fireplace:
                continue

            filtered.append(entry)

        return filtered

    def show_movies(self):
        """Compatibility entry point: the old Movies button opens Classics."""
        self.show_classics()

    def show_classics(self, folder=None, page=None):
        if folder is None:
            folder = self.media_dir

        folder = Path(folder)

        if page is None:
            page = self.page_memory["classics"].get(str(folder), 0)

        self.show_classics_page(folder, page)

    def show_classics_page(self, folder, page=0):
        self.clear()
        self.root.configure(bg="#111111")

        if folder == self.media_dir:
            entries = self.get_classics_root_entries()
            title = "🎬 MOVIES"
        else:
            entries = self.get_classics_entries(folder)
            title = f"🎬 {folder.name.upper()}"
            self.set_classics_folder_background(folder)

        FILES_PER_PAGE = 10
        total_pages = (len(entries) + FILES_PER_PAGE - 1) // FILES_PER_PAGE
        if total_pages == 0:
            total_pages = 1

        page = min(page, total_pages - 1)
        self.page_memory["classics"][str(folder)] = page

        start = page * FILES_PER_PAGE
        end = start + FILES_PER_PAGE
        page_entries = entries[start:end]

        tk.Label(
            self.root,
            text=title,
            font=("DejaVu Sans", 28, "bold"),
            bg="#111111",
            fg="white",
        ).pack(pady=(15, 5))

        tk.Label(
            self.root,
            text=f"Page {page + 1} / {total_pages}",
            font=("DejaVu Sans", 10),
            bg="#111111",
            fg="#AAAAAA",
        ).pack(pady=(0, 3))

        navigation = tk.Frame(self.root, bg="#111111")
        navigation.pack(pady=(2, 4))

        if page > 0:
            self.make_nav_button(
                navigation,
                "← PREV",
                lambda: self.show_classics_page(folder, page - 1),
            ).grid(row=0, column=0, padx=5)

        if page < total_pages - 1:
            self.make_nav_button(
                navigation,
                "NEXT →",
                lambda: self.show_classics_page(folder, page + 1),
            ).grid(row=0, column=1, padx=5)

        # Random button: files only, from this folder only.
        files = [entry for entry in entries if entry.is_file()]

        if files:
            random_button = self.make_small_button(
                self.root,
                "🎲 RANDOM",
                "#555555",
                "white",
                lambda folder=folder: self.random_classics_file(folder),
            )
            random_button.config(
                font=("DejaVu Sans", 13, "bold"),
                width=16,
                height=2,
            )
            random_button.pack(pady=(2, 5))

        entry_frame = tk.Frame(self.root, bg="#111111")
        entry_frame.pack(pady=2)

        for entry in page_entries:
            if entry.is_dir():
                text = f"📁 {entry.name}"
                command = lambda folder=entry: self.show_classics(folder)
            else:
                text = f"🎬 {entry.stem}"
                command = lambda media_file=entry: self.play_classics_file(media_file)

            button = self.make_button(
                entry_frame,
                text,
                "#333333",
                "white",
                command,
            )
            button.config(
                width=42,
                height=1,
                font=("DejaVu Sans", 12, "bold"),
            )
            button.pack(pady=2)

        if folder != self.media_dir:
            self.make_back_button(lambda: self.show_classics(folder.parent))
        else:
            self.make_back_button(self.build_main_menu)

    def play_classics_file(self, media_file):
        self.root.withdraw()
        play(str(media_file))
        self.root.deiconify()

    def random_classics_file(self, folder):
        """Choose a random file from this folder only.

        Folders are never included and subfolders are not searched.
        """
        if folder == self.media_dir:
            files = [
                entry
                for entry in self.get_classics_root_entries()
                if entry.is_file()
            ]
        else:
            files = [
                entry
                for entry in self.get_classics_entries(folder)
                if entry.is_file()
            ]

        if not files:
            return

        selected = random.choice(files)

        self.clear()
        self.set_movie_background(selected)
        self.root.configure(bg="#111111")

        tk.Label(
            self.root,
            text="🎲 RANDOM",
            font=("DejaVu Sans", 28, "bold"),
            bg="#111111",
            fg="white",
        ).pack(pady=(80, 20))

        tk.Label(
            self.root,
            text=selected.stem,
            font=("DejaVu Sans", 22, "bold"),
            bg="#333333",
            fg="white",
            padx=30,
            pady=20,
        ).pack(pady=20)

        self.make_small_button(
            self.root,
            "🎲 REROLL",
            "#555555",
            "white",
            lambda: self.random_classics_file(folder),
        ).pack(pady=5)

        self.make_small_button(
            self.root,
            "▶ PLAY",
            "#356B3D",
            "white",
            lambda: self.play_classics_file(selected),
        ).pack(pady=5)

        if folder == self.media_dir:
            self.make_back_button(self.show_classics)
        else:
            self.make_back_button(lambda: self.show_classics(folder))

    # ==============================================
    # EVENT FILES
    # ==============================================

    def get_event_files(self, event):
        folder_name = "Halloween" if event == "halloween" else "Christmas"
        event_dir = self.media_dir / folder_name
        if not event_dir.exists():
            return []

        extensions = {".mp4", ".mkv", ".avi", ".webm", ".mov"}
        return sorted(
            [
                path
                for path in event_dir.rglob("*")
                if path.is_file() and path.suffix.lower() in extensions
            ],
            key=lambda path: path.name.lower(),
        )

    # ==============================================
    # EVENT RANDOM SCREEN
    # ==============================================

    def show_event_screen(self, event, selected=None):
        self.clear()

        if event == "halloween":
            background_file = "halloween.gif"
            title = "🎃 HAPPY HALLOWEEN 🎃"
            reroll_text = "🎃 REROLL"
            play_text = "👻 PLAY"
            fallback_bg = "#180B20"
            title_color = "#FF8C00"
            reroll_color = "#6A1B9A"
            play_color = "#8B4513"
        else:
            background_file = "christmas.gif"
            title = "🎄 HAPPY HOLIDAYS 🎄"
            reroll_text = "🎁 REROLL"
            play_text = "🎄 PLAY"
            fallback_bg = "#102018"
            title_color = "#E53935"
            reroll_color = "#B71C1C"
            play_color = "#2E7D32"

        self.root.configure(bg=fallback_bg)
        self.load_event_background(background_file)
        files = self.get_event_files(event)

        if not files:
            tk.Label(
                self.root,
                text=title,
                font=("DejaVu Sans", 32, "bold"),
                bg=fallback_bg,
                fg=title_color,
            ).pack(pady=(80, 25))
            tk.Label(
                self.root,
                text="No files found.",
                font=("DejaVu Sans", 16),
                bg=fallback_bg,
                fg="white",
            ).pack(pady=20)
            self.make_back_button(self.build_main_menu)
            return

        if selected is None:
            selected = random.choice(files)

        info_frame = tk.Frame(self.root, bg="#111111")
        info_frame.pack(pady=(55, 15))

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

        self.make_small_button(
            self.root,
            reroll_text,
            reroll_color,
            "white",
            lambda: self.show_event_screen(event),
        ).pack(pady=4)

        self.make_small_button(
            self.root,
            play_text,
            play_color,
            "white",
            lambda: self.play_event_file(selected),
        ).pack(pady=4)

        self.make_small_button(
            self.root,
            "📂 BROWSE",
            "#333333",
            "white",
            lambda: self.show_event_browse(event),
        ).pack(pady=4)

        self.make_back_button(self.build_main_menu)

    def play_event_file(self, selected):
        self.root.withdraw()
        play(str(selected))
        self.root.deiconify()

    # ==============================================
    # EVENT BROWSE
    # ==============================================

    def show_event_browse(self, event, page=None):
        if page is None:
            page = self.page_memory["events"].get(event, 0)

        self.clear()

        if event == "halloween":
            background_file = "halloween.gif"
            title = "🎃 HALLOWEEN"
            fallback_bg = "#180B20"
            title_color = "#FF8C00"
        else:
            background_file = "christmas.gif"
            title = "🎄 CHRISTMAS"
            fallback_bg = "#102018"
            title_color = "#E53935"

        self.root.configure(bg=fallback_bg)
        self.load_event_background(background_file)
        files = self.get_event_files(event)
        FILES_PER_PAGE = 10

        total_pages = (len(files) + FILES_PER_PAGE - 1) // FILES_PER_PAGE
        if total_pages == 0:
            total_pages = 1

        page = min(page, total_pages - 1)
        self.page_memory["events"][event] = page
        start = page * FILES_PER_PAGE
        end = start + FILES_PER_PAGE
        page_files = files[start:end]

        tk.Label(
            self.root,
            text=title,
            font=("DejaVu Sans", 26, "bold"),
            bg="#111111",
            fg=title_color,
        ).pack(pady=(12, 3))

        tk.Label(
            self.root,
            text=f"Page {page + 1} / {total_pages}",
            font=("DejaVu Sans", 10),
            bg="#111111",
            fg="#AAAAAA",
        ).pack(pady=(0, 3))

        navigation = tk.Frame(self.root, bg="#111111")
        navigation.pack(pady=2)

        if page > 0:
            self.make_nav_button(
                navigation,
                "← PREV",
                lambda: self.show_event_browse(event, page - 1),
            ).grid(row=0, column=0, padx=5)

        if page < total_pages - 1:
            self.make_nav_button(
                navigation,
                "NEXT →",
                lambda: self.show_event_browse(event, page + 1),
            ).grid(row=0, column=1, padx=5)

        file_frame = tk.Frame(self.root, bg="#111111")
        file_frame.pack(pady=2)

        for media_file in page_files:
            button = self.make_small_button(
                file_frame,
                media_file.stem,
                "#333333",
                "white",
                lambda f=media_file: self.play_event_file(f),
            )
            button.config(width=42, height=1, font=("DejaVu Sans", 12, "bold"))
            button.pack(pady=2)

        self.make_back_button(lambda: self.show_event_screen(event))

    # ==============================================
    # FIREPLACE
    # ==============================================

    def play_fireplace(self):
        if self.library["fireplace"]:
            self.root.withdraw()
            play(str(self.library["fireplace"]), loop=True)
            self.root.deiconify()

    # ==============================================
    # RUN
    # ==============================================

    def run(self):
        self.root.mainloop()
