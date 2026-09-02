# Cyberium CLI (⌖)

Official, lightweight terminal client and live submission engine for **Cyberium Academy** (`https://cyberium.academy`).

Work through hands-on labs, track objective progress, and submit answers directly from your Linux terminal without switching back and forth to your web browser.

---

## Features

- **Live Synchronization:** Real-time question fetching and progress tracking directly from Cyberium's platform.
- **Instant Submissions:** Submit answers directly from the shell (`cyberium submit "<answer>"`).
- **Module & Program Switching:** Navigate through all training tracks (e.g., `ZX310 Cyber Warfare`, `XE103 Linux Fundamentals`).
- **Student Profile HUD:** View your division rank, total points, and coin balances.
- **Zero Heavy Dependencies:** Built on pure Python 3 standard libraries—no external dependencies or bloated packages required.
- **Clean Terminal UI:** Pure ANSI terminal glyphs with high-contrast red/gray/white palettes and zero emojis.

---

## Installation

### Method 1: Direct Install (Recommended)

Clone the repository and run the installer:

```bash
git clone https://github.com/yourusername/cyberium-cli.git ~/projects/cyberium-cli
cd ~/projects/cyberium-cli
./install.sh
```

Ensure `~/.local/bin` is in your `$PATH` (default in most Linux distributions).

### Method 2: Python Package (pip)

```bash
pip install -e ~/projects/cyberium-cli
```

---

## Authentication & Initial Setup

1. Open `https://cyberium.academy` in your web browser and log into your student account.
2. Press `F12` to open Developer Tools $\rightarrow$ navigate to **Storage / Application** $\rightarrow$ **Cookies** $\rightarrow$ `https://cyberium.academy`.
3. Run the login command in your terminal:
   ```bash
   cyberium login
   ```
4. Paste your `connect.sid` and `cyb_rt` cookie values.

Credentials are saved locally and securely to `~/.config/cyberium/config.json`. The client automatically handles JWT access token refreshing in the background.

---

## Command Reference

| Command | Description |
|---|---|
| `cyberium` | Displays the current active lab question and module progress bar. |
| `cyberium list` | Lists all questions in the current module with `[✓]` solved / `[⏳]` active badges. |
| `cyberium submit "<answer>"` | Submits your answer to the active question with instant platform feedback. |
| `cyberium modules` | Lists all modules in your active program and their completion scores. |
| `cyberium set-module <ID>` | Switches your active module (e.g., `cyberium set-module 88` for Post Linux). |
| `cyberium programs` | Lists all enrolled training tracks (e.g., `ZX310`, `XE103`, `NX201`). |
| `cyberium set-program <ID>` | Switches your active program. |
| `cyberium profile` | Displays your student name, division, unit, and total point score. |

---

## Examples

### View Current Objective
```bash
$ cyberium

⌖ CYBERIUM ACADEMY │ Post (Linux) (Lab: 14/83 [16%])
────────────────────────────────────────────────────────────────────────
[⏳] CURRENT OBJECTIVE (Index 14):
  2.2. Exfiltrate the /etc/passwd file from the Metasploitable3 machine to your Kali machine by running wget with the proper file-transfer flag and share the command.

To submit your answer:
  cyberium submit "<your_answer>"
```

### Submit an Answer
```bash
$ cyberium submit "--post-file"

[*] Question #13: 2.1. Review the wget help menu and identify the flag that sends data from a file.
[*] Submitting answer: --post-file
[✓] CORRECT! Points awarded.

[⏳] NEXT OBJECTIVE (#14):
  2.2. Exfiltrate the /etc/passwd file from the Metasploitable3 machine to your Kali machine...
```

---

## License

Developed by Denis Albin for Cyberium Academy Students & Instructors.
