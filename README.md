# Rumi Desktop alpha 0.6

Rumi Desktop is a **local desktop application for downloading, managing, and playing audio** with a strong focus on UI, theming, and metadata editing.
Built with **Python + Flet**, it combines a downloader, music player, tag editor, and dynamic color system into a single app.

This README explains **how the project works internally**, how files interact, and how to extend or modify the code.

---

## Core Features

* Download audio (YouTube / playlists via yt-dlp)
* Local MP3 library management
* Built-in music player (play, pause, seek, volume)
* Shuffle / repeat modes
* ID3 metadata reading and editing
* Album cover extraction and blur-based dynamic background
* Dynamic UI theming based on album cover colors
* User settings persistence (colors, wallpaper. still in development)
* Keyboard controls
* Designed for PyInstaller builds

---

## Requirements

- [FFmpeg](https://ffmpeg.org/download.html) must be installed.
- After downloading, **add the `ffmpeg\bin` folder to your system `PATH`.**

```bash
pip install -r requirements.txt
```

---

## Project Structure

```
rumi-desktop/
│
├── main.py              # App entry point, routing
├── start.py             # Initial download page
├── player.py            # Music player page (core logic)
├── edit_page.py         # Audio metadata editor
├── settings_page.py     # App settings page
├── config.py            # Global state, settings, helpers
│
├── icons/               # SVG icons
├── color/               # Wallpapers, temporary backgrounds
├── dynamic_color/       # Debug dumps of dynamic UI elements
│
├── user_setting.json    # User preferences (generated)
├── mp3_files.json       # Saved MP3 paths (generated)
├── errors.log           # Runtime error log
└── venv/
```

---

## Global Architecture

The app uses a **central shared state** via `config.py`.

There is **no class-based state management** — everything relies on:

* global variables
* shared references to UI elements
* explicit updates via `page.update()`

This keeps UI behavior predictable and fast, at the cost of tighter coupling.

---

## config.py (Global State & Utilities)

### Purpose

* Store **global runtime state**
* Load and validate user settings
* Manage default UI colors
* Track current playback status
* Provide helper utilities

### Key Variables

```python
main_color_hex      # Primary UI color
not_main_color_hex  # Secondary UI color
wallpaper           # Background image path
current_playing_audio
current_volume
current_mp3_files
all_mp3s
play_mode           # default | shuffle | repeat
```

### Dynamic Color System

```python
dynamic_color = {
    "active_color": [],
    "inactive_color": [],
    "color_main": [],
    "color_not_main": []
}
```

UI elements are **registered once**, then recolored globally when the theme changes.

### Hex Validation

```python
re.fullmatch(r"#([0-9a-fA-F]{6})", s)
```

Ensures strict `#RRGGBB` format.

### Settings Loading

* Reads `user_setting.json` if present
* Validates wallpaper existence and format
* Applies stored colors if valid
* Errors are logged to `errors.log`

---

## main.py (Application Entry)

### Responsibilities

* Initialize Flet app
* Register routes
* Handle navigation between pages

### Routes

```text
/          → start.py (download page)
/music     → player.py
/edit      → edit_page.py
/settings  → settings_page.py
```

---

## start.py (Download Page)

### Responsibilities

* Download audio using `yt-dlp`
* Track download progress

### Output

* MP3 files saved to user-selected directory

---

## player.py (Music Player Core)

This is the **largest and most important module**.

### Responsibilities

* Render MP3 list
* Play audio via `flet_audio`
* Read ID3 metadata (mutagen)
* Extract and display album covers
* Generate blurred backgrounds
* Calculate average album color
* Dynamically recolor UI
* Handle playback logic

### Audio Playback

```python
audio1 = fa.Audio(
    on_loaded=audio_loaded,
    on_position_changed=audio_position_changed,
    on_state_changed=state_handler
)
```

Supports:

* play / pause
* seek
* volume
* track end detection

### Play Modes

* `default` — sequential
* `shuffle` — random next track
* `repeat` — replay current track

### Dynamic Theme Generation

1. Extract album cover (APIC tag)
2. Convert to RGB
3. Compute average color
4. Normalize brightness
5. Generate secondary desaturated color
6. Apply globally to UI

If no cover exists → fallback to default theme.

---

## edit_page.py (Metadata Editor)

### Responsibilities

* Edit ID3 tags:

  * title
  * artist
  * album
  * cover image
* Preview changes
* Save updates back to file

### Workflow

* Audio file selected
* Existing tags extracted
* User edits fields
* Mutagen writes updated ID3 tags

---

## settings_page.py (User Settings)

### Features

* Change background wallpaper
* Set `main_color_hex`
* Set `not_main_color_hex`
* Reset colors using `default`
* Persistent storage in `user_setting.json`

---

## Error Handling

All runtime errors are appended to:

```
errors.log
```

Format:

```
YYYY-MM-DD HH:MM:SS (Context) Error message
```

---

## Keyboard Controls (Player)

| Key   | Action       |
| ----- | ------------ |
| Space | Play / Pause |
| F11   | Fullscreen   |

(Search input disables space behavior.)

---

## Build with PyInstaller

Example command:

```bash
pyinstaller -w \
-i color/icon_sq.ico \
--add-data "color;color" \
--add-data "icons;icons" \
--add-data "cooks;cooks" \
main.py
```

---

## Extending the Project

Ideas:

* Playlist management
* Hotkey rebinding

The architecture intentionally stays simple to allow fast iteration.

---

# Custom Colors Approach

In this project, instead of using a global theme, colors for each UI element are set **manually**.  

The reason is that theme-based approaches **do not provide full control** over every element's color, which is necessary for precise customization in this application.  

This allows for **fine-grained control** of the appearance of sliders, buttons, text, and other components, ensuring the interface matches the intended design.

---

## Known Critical Issues

- **High RAM usage** when a large number of tracks are added.

The application is still in **alpha stage**, so it may **experience crashes, glitches, or other unexpected behavior**.
It is **not yet a full-featured music player**, and long-term continuous use may expose bugs that will be **addressed in future updates**.

Using `dynamic_color` in `config.py` is a temporary solution that will be replaced in the future with a more efficient and optimized option.

---

## License

This project is licensed under the  
**Creative Commons Attribution–NonCommercial 4.0 International (CC BY-NC 4.0)**.

You are free to:
- View and download the source code
- Modify it for personal or non-commercial use

You are NOT allowed to:
- Use this project or any modified version of it for commercial purposes
- Sell or include it in paid products or services

See the LICENSE file for details.
