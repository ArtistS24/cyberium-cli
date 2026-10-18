# Cyberium CLI & TUI Suite

Lightweight terminal client, live submission engine, and interactive TUI dashboard for **Cyberium Academy** (`https://cyberium.academy`).

Work through hands-on labs, track objective progress, take notes, view course books/videos, and submit answers directly from your Linux terminal without switching back and forth to your web browser.

---

## Features

- **Automated Session Discovery:** Auto-detects and syncs active session cookies directly from your local Firefox browser.
- **Interactive TUI Dashboard:** Full-screen ncurses dashboard (`cyberium tui` or `cyberium-tui`) with mouse support, search, scratchpad notes, themes, and instant modal book/video access.
- **Course PDF Books:** Instant viewing (`-o`), downloading (`-d`), or link copying (`-c`) for course textbooks via Cloudflare R2 CDN.
- **HD Video Lectures:** Watch streaming lectures directly in browser (`-o`) or copy links (`-c`).
- **Instant Live Submissions:** Submit answers directly from the shell (`cyberium submit "<answer>"` or `cyberium submit -i 14 "<answer>"`).
- **Multi-Track & Module Navigation:** Effortlessly browse and switch between all 14 training tracks (`ZX310 Cyber Warfare`, `ZX301 Penetration Testing`, `NX201 Network Research`, etc.).
- **Student Scratchpad Notes:** Attach personal notes and memos to any lab question (`cyberium note "memo"`).
- **16 Terminal Themes:** Custom color palettes (Cyberium, Dracula, Tokyo Night, Catppuccin, Nord, Matrix, Gruvbox, etc.).
- **Zero Heavy Dependencies:** Built on pure Python 3 standard libraries—zero external pip dependencies required.
- **Strict Terminal Formatting:** Pure ANSI terminal glyphs with zero emojis, high-contrast badges, and distraction-free layout.

---

## Installation

### Direct Install (Recommended)

```bash
cd ~/Projects/cyberium-cli
./install.sh
```

Installs `cyberium` and `cyberium-tui` to `~/.local/bin/` with bash and zsh tab-completion scripts.

---

## Authentication & Initial Setup

Cyberium CLI auto-detects and syncs your active session cookies from Firefox automatically!

If you ever need to manually refresh or link your session:

```bash
cyberium sync          # Auto-sync live cookies from Firefox
cyberium login         # Interactive login prompt (with auto-detect option)
```

Credentials are saved locally and securely to `~/.config/cyberium/config.json`. The client automatically handles JWT access token refreshing in the background.

---

## Command Reference

| Command | Description |
|---|---|
| `cyberium` | Displays the active lab question and module progress. |
| `cyberium list` | Lists all questions in current module with `[✓]` solved / `[]` active badges. |
| `cyberium submit "<ans>"` | Submits your answer to the active question with instant platform feedback. |
| `cyberium submit -i <num> "<ans>"` | Submits an answer to a specific question number or section (e.g. `2.2`). |
| `cyberium submit-extra <num> "<ans>"` | Submits an answer to a bonus/extra challenge. |
| `cyberium modules` | Lists all modules in your active program with completion stats. |
| `cyberium set-module [ID]` | Switches active module (interactive selector if ID omitted). |
| `cyberium programs` | Lists all 14 enrolled training tracks (e.g., `ZX310`, `ZX301`, `NX201`). |
| `cyberium switch [CODE/ID]` | Switches active training track (e.g., `cyberium switch ZX301`). |
| `cyberium book` | Displays course PDF textbook link and details. |
| `cyberium book -o` | Opens course PDF directly in your default reader or browser. |
| `cyberium book -d` | Downloads course PDF to `~/Downloads/` directly from Cloudflare R2 CDN. |
| `cyberium book -c` | Copies direct PDF URL to clipboard. |
| `cyberium video` | Displays HD video lecture streaming URL. |
| `cyberium video -o` | Opens HD video lecture in browser. |
| `cyberium note "memo"` | Saves a scratchpad note to the current active question. |
| `cyberium note 2.2 "memo"` | Saves a scratchpad note to section `2.2` (Question #14). |
| `cyberium note 2.2` | Displays the scratchpad note for section `2.2`. |
| `cyberium notes` | Lists all saved scratchpad notes across the current module. |
| `cyberium search "<term>"` | Searches question objectives in the active module by keyword. |
| `cyberium extra` | Lists bonus / extra challenges for the active module. |
| `cyberium themes` | Lists all 16 available terminal themes. |
| `cyberium set-theme <name>` | Switches active theme (e.g., `cyberium set-theme matrix`). |
| `cyberium profile` | Displays student dossier, rank, and training points. |
| `cyberium stats` | Displays full operator dashboard with PBR metrics and trophies. |
| `cyberium sync` | Synchronizes live session cookies from Firefox. |
| `cyberium logout` | Logs out of Cyberium Academy and clears saved session cookies. |
| `cyberium tui` | Launches full-screen interactive curses dashboard (`cyberium-tui`). |

---

## Interactive TUI Hotkeys

Launch with `cyberium tui` or `cyberium-tui`:

| Hotkey | Action |
|---|---|
| `↑` / `↓` or `k` / `j` | Navigate question list |
| `Enter` / `i` | Submit answer for selected objective |
| `/` or `s` | Search / filter questions |
| `l` | Attached Lab Resources modal (`[o]` Open, `[d]` Download, `[c]` Copy URL) |
| `n` | Open student scratchpad note popup |
| `m` | Browse and switch modules |
| `P` | Browse and switch training programs/tracks |
| `x` | Toggle between Core Labs and Bonus/Extra Challenges |
| `b` | Course Book modal (`[o]` Open, `[d]` Download, `[c]` Copy link) |
| `v` | HD Video Lecture modal (`[o]` Watch, `[c]` Copy link) |
| `t` | Terminal theme selector (16 palettes) |
| `p` | Student operator dossier popup |
| `c` | Copy selected question text to clipboard |
| `r` | Refresh platform data |
| `L` | Confirmation popup to log out and clear session |
| `q` / `Esc` | Quit TUI / Close popup |

---

## License

Developed by Denis Albin for Cyberium Academy Students & Instructors.

