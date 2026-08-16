# 📺 TV BOX

> A tiny, stupidly overengineered media center for an old laptop.

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Linux](https://img.shields.io/badge/Linux-supported-orange?logo=linux)
![MPV](https://img.shields.io/badge/Player-mpv-green)
![Status](https://img.shields.io/badge/Status-UNDER%20CONSTRUCTION-yellow)

---

    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   ████████╗██╗   ██╗    ██████╗  ██████╗ ██╗  ██╗      ║
    ║   ╚══██╔══╝██║   ██║    ██╔══██╗██╔═══██╗╚██╗██╔╝      ║
    ║      ██║   ██║   ██║    ██████╔╝██║   ██║ ╚███╔╝       ║
    ║      ██║   ██║   ██║    ██╔══██╗██║   ██║ ██╔██╗      ║
    ║      ██║   ╚██████╔╝    ██████╔╝╚██████╔╝██╔╝ ██╗      ║
    ║      ╚═╝    ╚═════╝     ╚═════╝  ╚═════╝ ╚═╝  ╚═╝      ║
    ║                                                          ║
    ║                    M E D I A   B O X                   ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝

## 🧠 What is this?

**TV BOX** is a lightweight, Python-powered media center designed to turn an old laptop into a simple living-room entertainment machine.

The goal is simple:

> Turn the laptop on → turn the TV on → pick something → enjoy.

No bloated media center.  
No complicated interface.  
No giant database.

Just Python, `mpv`, some videos, and questionable engineering decisions.

---

## ✨ Planned Features

### 📺 TV Shows

- Browse series
- Browse seasons
- Browse episodes
- Play individual episodes
- Random episode selection
- Continue watching
- Automatic next-episode playback

### 🎲 Random TV

Turn your collection into a personal TV channel.

    ALF
      ↓
    The Simpsons
      ↓
    South Park
      ↓
    SpongeBob
      ↓
    ALF
      ↓
    ...

The TV never has to stop.

### 🔥 Fireplace Mode

Because apparently a 20 GB fireplace video was necessary.

### 🎬 Movies

Eventually the box will also support a local movie library.

### 🖥️ Minimal GUI

The final interface will be designed specifically for use from a couch:

- Large buttons
- Minimal menus
- Mouse friendly
- Fullscreen
- No unnecessary desktop UI

---

## 🏗️ Architecture

    ┌──────────────┐
    │     GUI      │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │    main.py   │
    └──────┬───────┘
           │
    ┌──────┴───────┐
    ▼              ▼
    ┌───────────┐  ┌───────────┐
    │ library.py│  │ player.py │
    └─────┬─────┘  └─────┬─────┘
          │              │
          ▼              ▼
       Local media      mpv
          │              │
          └──────┬───────┘
                 ▼
                📺

---

## 📁 Media Library

The intended library structure is:

    media/
    ├── Alf/
    │   ├── Season 1/
    │   │   ├── Episode 1.mkv
    │   │   └── Episode 2.mkv
    │   └── Season 2/
    │       └── Episode 1.mkv
    │
    ├── Simpsons/
    │   └── Season 1/
    │       ├── Episode 1.mp4
    │       └── Episode 2.mp4
    │
    └── fireplace.mp4

The actual media collection is **not stored in this repository**.

---

## ⚙️ Requirements

- Linux
- Python 3
- `mpv`
- A collection of media
- A functioning sense of humor

Install `mpv` on Debian/Ubuntu/Mint:

    sudo apt install mpv

---

## 🚀 Running

Clone the repository:

    git clone git@github.com:gc1644/tv-box.git
    cd tv-box

Run:

    python3 main.py

---

## 🧪 Current Development Status

    [██████████████░░░░░░░░░░░░] DEVELOPMENT

    ✓ Project initialized
    ✓ Git repository
    ✓ Library scanner
    ✓ Series detection
    ✓ Season detection
    ✓ Episode detection
    ✓ mpv integration
    ✓ CLI interface
    ✓ Fireplace mode

    □ Browse library
    □ Random episode
    □ Random TV
    □ Automatic next episode
    □ Playback history
    □ Movie library
    □ Fullscreen GUI
    □ TV-box autostart
    □ Couch-friendly interface

---

## 🖥️ The Hardware

The intended target is an old HP laptop connected to a television via HDMI.

The laptop runs headless with the lid closed and acts as a tiny dedicated media computer.

    ┌─────────────────────┐
    │        📺 TV        │
    └──────────┬──────────┘
               │ HDMI
               │
    ┌──────────┴──────────┐
    │      OLD HP LAPTOP  │
    │                     │
    │      Linux Mint     │
    │       Xfce          │
    │                     │
    │        mpv          │
    │         +           │
    │       Python        │
    └─────────────────────┘
               │
               ▼
          HDD / Media

The entire purpose of this project is to make the hardware disappear.

The user should only see the TV.

---

## 🛠️ Philosophy

**Keep it lightweight.**

The target hardware is old. If it needs 16 GB of RAM and a dedicated GPU, something has gone terribly wrong.

**Keep it simple.**

The person using the TV shouldn't need to know what Linux is doing underneath.

**Prefer boring technologies.**

Python.  
Filesystem.  
JSON.  
mpv.

If it works, it works.

**Make it fun.**

This started as an experiment to turn an old laptop into a TV box.

Now it has a fake terminal interface and a dedicated fireplace mode.

There was never any chance this would remain reasonable.

---

## 📜 License

TBD.

---

<p align="center">

### 📺 Built with Python, Linux, mpv and questionable decisions.

**TV BOX — your personal television, minus the television company.**

</p>
