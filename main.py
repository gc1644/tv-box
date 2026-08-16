from library import scan_library
from player import play


def banner():
    print(r"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   ████████╗██╗   ██╗    ██████╗  ██████╗ ██╗  ██╗      ║
║   ╚══██╔══╝██║   ██║    ██╔══██╗██╔═══██╗╚██╗██╔╝      ║
║      ██║   ██║   ██║    ██████╔╝██║   ██║ ╚███╔╝       ║
║      ██║   ██║   ██║    ██╔══██╗██║   ██║ ██╔██╗       ║
║      ██║   ╚██████╔╝    ██████╔╝╚██████╔╝██╔╝ ██╗      ║
║      ╚═╝    ╚═════╝     ╚═════╝  ╚═════╝ ╚═╝  ╚═╝      ║
║                                                          ║
║                    M E D I A   B O X                   ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")


def status(library):
    series_count = len(library)
    episode_count = sum(
        len(episodes)
        for seasons in library.values()
        for episodes in seasons.values()
    )

    print("┌────────────────────────────────────────────────────────┐")
    print("│ SYSTEM STATUS                                          │")
    print("├────────────────────────────────────────────────────────┤")
    print("│ MEDIA DATABASE............. ONLINE                     │")
    print("│ VIDEO ENGINE............... MPV                        │")
    print(f"│ LIBRARY.................... {series_count} SERIES / {episode_count} EPISODES".ljust(57) + "│")
    print("│ FIREPLACE.................. READY                      │")
    print("│ STATUS..................... ████████████████ 100%      │")
    print("└────────────────────────────────────────────────────────┘")
    print()


def main_menu():
    print("╭────────────────────────────────────────────────────────╮")
    print("│                     SELECT MODE                       │")
    print("├────────────────────────────────────────────────────────┤")
    print("│                                                        │")
    print("│   [1]  BROWSE LIBRARY                                  │")
    print("│   [2]  RANDOM EPISODE                                  │")
    print("│   [3]  RANDOM TV                                       │")
    print("│   [4]  FIREPLACE                                       │")
    print("│                                                        │")
    print("│   [Q]  QUIT                                             │")
    print("│                                                        │")
    print("╰────────────────────────────────────────────────────────╯")
    print()


library = scan_library("media")

banner()
status(library)
main_menu()

choice = input("INPUT > ").strip().lower()

print()

if choice == "q":
    print("Shutting down TV BOX...")
elif choice == "4":
    print("🔥 FIREPLACE MODE")
    play("media/fireplace.mp4")
else:
    print("Feature not implemented yet.")
