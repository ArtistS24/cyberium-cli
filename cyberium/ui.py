"""
ANSI Styling, ASCII Art Branding, and Nerd Font Terminal Presentation
Strictly clean terminal glyphs, expanded theme palettes, and high-contrast color formatting.
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
ICON_BOOK = "󰂿"
ICON_VIDEO = "󰕧"
ICON_STAR = "★"
ICON_THEME = "󰏘"

ASCII_BANNER = rf"""{CYAN}{BOLD}
  ██████╗██╗   ██╗██████╗ ███████╗██████╗ ██╗██╗   ██╗███╗   ███╗
 ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗██║██║   ██║████╗ ████║
 ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝██║██║   ██║██╔████╔██║
 ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗██║██║   ██║██║╚██╔╝██║
 ╚██████╗   ██║   ██████╔╝███████╗██║  ██║██║╚██████╔╝██║ ╚═╝ ██║
  ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝     ╚═╝{RESET}
{DIM}                 ACADEMY OFFENSIVE LAB CLIENT v2.0{RESET}
"""

THEMES = {
    "cyberpunk": {
        "name": "Cyberpunk Neon (Default)",
        "desc": "High-contrast Cyan, Emerald, and Amber hues",
        "pair1": "white",    # Text
        "pair2": "cyan",     # Accent / Header
        "pair3": "green",    # Solved
        "pair4": "yellow",   # Active Objective
        "pair5": "red",      # Locked / Error
        "pair6": "magenta",  # Badges
        "pair7": "dim",      # Borders
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
    out = f"\n{RED}{BOLD}CYBERIUM ACADEMY{RESET}"
    if title:
        out += f" {DIM}│{RESET} {WHITE}{BOLD}{title}{RESET}"
    if subtitle:
        out += f" {DIM}({subtitle}){RESET}"
    out += f"\n{DIM}{'─' * 72}{RESET}"
    return out


def divider():
    return f"{DIM}{'─' * 72}{RESET}"


def badge_success(text):
    return f"{GREEN}[{ICON_CHECK}] {text}{RESET}"


def badge_pending(text):
    return f"{YELLOW}{BOLD}[{ICON_PENDING}] {text}{RESET}"


def badge_failed(text):
    return f"{RED}{BOLD}[{ICON_CROSS}] {text}{RESET}"


def badge_empty(text):
    return f"{DIM}[ ] {text}{RESET}"


def progress_bar(current, total, width=20):
    if total <= 0:
        return f"{DIM}[{'.' * width}] 0%{RESET}"
    pct = min(1.0, current / total)
    filled = int(round(width * pct))
    bar = "=" * filled + "-" * (width - filled)
    return f"{CYAN}[{bar}]{RESET} {WHITE}{int(pct * 100)}%{RESET}"


def calculate_rank(points):
    """Calculates student offensive title based on training points."""
    if points >= 500:
        return "LVL 6 ◆ CYBER WARFARE OPERATOR", MAGENTA
    elif points >= 300:
        return "LVL 5 ◆ SENIOR THREAT SPECIALIST", CYAN
    elif points >= 150:
        return "LVL 4 ◆ EXPLOITATION PRACTITIONER", GREEN
    elif points >= 50:
        return "LVL 3 ◆ OFFENSIVE APPRENTICE", YELLOW
    elif points >= 10:
        return "LVL 2 ◆ SECURITY ANALYST", BLUE
    else:
        return "LVL 1 ◆ CYBER RECRUIT", WHITE
