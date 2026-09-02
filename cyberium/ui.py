"""
ANSI Styling, ASCII Art Branding, and Nerd Font Terminal Presentation
Strictly clean terminal glyphs and high-contrast color formatting.
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


ASCII_BANNER = rf"""{CYAN}{BOLD}
  ██████╗██╗   ██╗██████╗ ███████╗██████╗ ██╗██╗   ██╗███╗   ███╗
 ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗██║██║   ██║████╗ ████║
 ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝██║██║   ██║██╔████╔██║
 ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗██║██║   ██║██║╚██╔╝██║
 ╚██████╗   ██║   ██████╔╝███████╗██║  ██║██║╚██████╔╝██║ ╚═╝ ██║
  ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝     ╚═╝{RESET}
{DIM}                 ACADEMY OFFENSIVE LAB CLIENT v2.0{RESET}
"""


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

