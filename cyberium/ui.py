"""
ANSI Styling, Cyberium Official Theme, and Nerd Font Presentation
Matches the official dark obsidian & electric cyan Cyberium Academy dashboard.
"""

# ANSI Color Palette
RED = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[1;34m"
MAGENTA = "\033[1;35m"
CYAN = "\033[1;36m"
WHITE = "\033[1;37m"
DIM = "\033[0;90m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Nerd Font / Terminal Icons
ICON_CHECK = "✓"
ICON_CROSS = "✗"
ICON_PENDING = ""
ICON_ARROW = "❯"
ICON_POINTER = "►"
ICON_USER = ""
ICON_FOLDER = "󰉋"
ICON_POINT = "◆"
ICON_STAR = "★"
ICON_BOOK = "󰂿"
ICON_VIDEO = "󰕧"
ICON_THEME = "󰏘"
ICON_LIVE = "●"

CYBERIUM_LOGO = rf"""{CYAN}{BOLD}
   ██████╗██╗   ██╗██████╗ ███████╗██████╗ ██╗██╗   ██╗███╗   ███╗
  ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗██║██║   ██║████╗ ████║
  ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝██║██║   ██║██╔████╔██║
  ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗██║██║   ██║██║╚██╔╝██║
  ╚██████╗   ██║   ██████╔╝███████╗██║  ██║██║╚██████╔╝██║ ╚═╝ ██║
   ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝     ╚═╝{RESET}
{RED}{BOLD}  [ JOHN BRYCE #1 בטכנולוגיה ]{RESET}  {YELLOW}{BOLD}★ OFFENSIVE WARFARE SUITE v2.0{RESET}
"""

ASCII_BANNER = CYBERIUM_LOGO

THEMES = {
    "cyberium": {
        "name": "Cyberium Official (Default)",
        "desc": "Official Obsidian Black & Electric Cyan Academy Palette",
        "pair1": "white",    # Text
        "pair2": "cyan",     # Accent / Electric Blue Logo
        "pair3": "green",    # Solved Objectives
        "pair4": "yellow",   # Active Objective / Gold Rank Badge
        "pair5": "red",      # John Bryce Red / Locked
        "pair6": "cyan",     # Badges
        "pair7": "dim",      # Subtle Grid Lines
    },
    "cyberpunk": {
        "name": "Cyberpunk Neon",
        "desc": "High-contrast Cyan, Emerald, and Amber hues",
        "pair1": "white",
        "pair2": "cyan",
        "pair3": "green",
        "pair4": "yellow",
        "pair5": "red",
        "pair6": "magenta",
        "pair7": "dim",
    },
    "catppuccin": {
        "name": "Catppuccin Mocha",
        "desc": "Comfortable pastel sapphire, peach, and mauve",
        "pair1": "white",
        "pair2": "cyan",
        "pair3": "green",
        "pair4": "yellow",
        "pair5": "red",
        "pair6": "magenta",
        "pair7": "dim",
    },
    "dracula": {
        "name": "Dracula",
        "desc": "Vampire purple, neon pink, and cyan highlights",
        "pair1": "white",
        "pair2": "magenta",
        "pair3": "green",
        "pair4": "cyan",
        "pair5": "red",
        "pair6": "yellow",
        "pair7": "dim",
    },
    "tokyo-night": {
        "name": "Tokyo Night",
        "desc": "Midnight blue streets with vibrant neon magenta & cyan",
        "pair1": "white",
        "pair2": "blue",
        "pair3": "green",
        "pair4": "cyan",
        "pair5": "red",
        "pair6": "magenta",
        "pair7": "dim",
    },
    "gruvbox": {
        "name": "Gruvbox Dark",
        "desc": "Warm retro groove with earthy orange, yellow & green",
        "pair1": "white",
        "pair2": "yellow",
        "pair3": "green",
        "pair4": "yellow",
        "pair5": "red",
        "pair6": "magenta",
        "pair7": "dim",
    },
    "everforest": {
        "name": "Everforest",
        "desc": "Soft forest pine, serene sage green, and warm earth",
        "pair1": "white",
        "pair2": "green",
        "pair3": "green",
        "pair4": "yellow",
        "pair5": "red",
        "pair6": "cyan",
        "pair7": "dim",
    },
    "rose-pine": {
        "name": "Rosé Pine",
        "desc": "All natural pine, rosé blush, and golden glow",
        "pair1": "white",
        "pair2": "magenta",
        "pair3": "green",
        "pair4": "yellow",
        "pair5": "red",
        "pair6": "cyan",
        "pair7": "dim",
    },
    "kanagawa": {
        "name": "Kanagawa",
        "desc": "Wave blue ocean, autumn leaf orange, and fuji white",
        "pair1": "white",
        "pair2": "cyan",
        "pair3": "green",
        "pair4": "yellow",
        "pair5": "red",
        "pair6": "blue",
        "pair7": "dim",
    },
    "nord": {
        "name": "Nordic Frost",
        "desc": "Arctic blue, cool cyan, and frosty white tones",
        "pair1": "white",
        "pair2": "cyan",
        "pair3": "green",
        "pair4": "blue",
        "pair5": "red",
        "pair6": "cyan",
        "pair7": "white",
    },
    "matrix": {
        "name": "Matrix Hacker",
        "desc": "Monochromatic hacker CRT with glowing digital green",
        "pair1": "green",
        "pair2": "green",
        "pair3": "white",
        "pair4": "yellow",
        "pair5": "red",
        "pair6": "green",
        "pair7": "dim",
    },
    "synthwave84": {
        "name": "Synthwave '84",
        "desc": "80s retrowave sunset magenta, hot pink & neon cyan",
        "pair1": "white",
        "pair2": "magenta",
        "pair3": "cyan",
        "pair4": "yellow",
        "pair5": "red",
        "pair6": "magenta",
        "pair7": "dim",
    },
    "monokai": {
        "name": "Monokai Pro",
        "desc": "Vibrant sunshine yellow, emerald, and hot pink",
        "pair1": "white",
        "pair2": "yellow",
        "pair3": "green",
        "pair4": "cyan",
        "pair5": "red",
        "pair6": "magenta",
        "pair7": "dim",
    },
    "oxocarbon": {
        "name": "Oxocarbon",
        "desc": "Minimalist high-tech carbon with crisp neon accents",
        "pair1": "white",
        "pair2": "cyan",
        "pair3": "green",
        "pair4": "magenta",
        "pair5": "red",
        "pair6": "white",
        "pair7": "dim",
    },
    "retro-fallout": {
        "name": "Fallout Pip-Boy",
        "desc": "Post-apocalyptic phosphor amber & green terminal",
        "pair1": "yellow",
        "pair2": "yellow",
        "pair3": "green",
        "pair4": "white",
        "pair5": "red",
        "pair6": "yellow",
        "pair7": "dim",
    },
    "solarized": {
        "name": "Solarized Dark",
        "desc": "Precision solarized cyan, blue, and golden yellow",
        "pair1": "white",
        "pair2": "blue",
        "pair3": "green",
        "pair4": "yellow",
        "pair5": "red",
        "pair6": "cyan",
        "pair7": "dim",
    },
    "classic": {
        "name": "Standard Linux ANSI",
        "desc": "Pure standard 8-color fallback for standard Linux/TTY terminals",
        "pair1": "white",
        "pair2": "cyan",
        "pair3": "green",
        "pair4": "yellow",
        "pair5": "red",
        "pair6": "white",
        "pair7": "white",
    }
}


def header(title, subtitle=None):
    out = f"\n{CYAN}{BOLD}C Y B E R I U M{RESET} {RED}{BOLD}[JOHN BRYCE]{RESET}"
    if title:
        out += f" {DIM}│{RESET} {WHITE}{BOLD}{title}{RESET}"
    if subtitle:
        out += f" {DIM}({subtitle}){RESET}"
    out += f"\n{DIM}{'─' * 74}{RESET}"
    return out


def divider():
    return f"{DIM}{'─' * 74}{RESET}"


def badge_success(text):
    return f"{GREEN}[{ICON_CHECK}] {text}{RESET}"


def badge_pending(text):
    return f"{YELLOW}{BOLD}[{ICON_PENDING}] {text}{RESET}"


def badge_failed(text):
    return f"{RED}{BOLD}[{ICON_CROSS}] {text}{RESET}"


def badge_empty(text):
    return f"{DIM}[ ] {text}{RESET}"


def progress_bar(current, total, width=20):
    try:
        cur = max(0, int(current))
        tot = max(0, int(total))
        w = max(1, int(width))
    except (ValueError, TypeError):
        return f"{DIM}[{'·' * 10}] 0%{RESET}"
    if tot <= 0:
        return f"{DIM}[{'·' * w}] 0%{RESET}"
    pct = max(0.0, min(1.0, cur / tot))
    filled = max(0, min(w, int(round(w * pct))))
    bar = "■" * filled + "□" * (w - filled)
    return f"{CYAN}[{bar}]{RESET} {WHITE}{int(pct * 100)}%{RESET}"


def calculate_rank(points):
    """Calculates official Cyberium Academy student rank matching web dashboard."""
    try:
        pts = int(points)
    except (ValueError, TypeError):
        pts = 0
    if pts >= 500:
        return "★ MASTER SPECIALIST", MAGENTA
    elif pts >= 250:
        return "★ SENIOR OPERATOR", CYAN
    elif pts >= 100:
        return "★ EXPERT", YELLOW
    elif pts >= 40:
        return "★ PRACTITIONER", GREEN
    elif pts >= 10:
        return "★ APPRENTICE", BLUE
    else:
        return "★ RECRUIT", WHITE
