"""
ANSI Styling and Terminal Presentation for Cyberium CLI
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


def header(title, subtitle=None):
    out = f"\n{RED}{BOLD}⌖ CYBERIUM ACADEMY{RESET}"
    if title:
        out += f" {DIM}│{RESET} {WHITE}{BOLD}{title}{RESET}"
    if subtitle:
        out += f" {DIM}({subtitle}){RESET}"
    out += f"\n{DIM}{'─' * 72}{RESET}"
    return out


def divider():
    return f"{DIM}{'─' * 72}{RESET}"


def badge_success(text):
    return f"{GREEN}[✓] {text}{RESET}"


def badge_pending(text):
    return f"{YELLOW}{BOLD}[⏳] {text}{RESET}"


def badge_failed(text):
    return f"{RED}{BOLD}[✗] {text}{RESET}"


def badge_empty(text):
    return f"{DIM}[ ] {text}{RESET}"


def progress_bar(current, total, width=20):
    if total <= 0:
        return f"{DIM}[{'.' * width}] 0%{RESET}"
    pct = min(1.0, current / total)
    filled = int(round(width * pct))
    bar = "=" * filled + "-" * (width - filled)
    return f"{CYAN}[{bar}]{RESET} {WHITE}{int(pct * 100)}%{RESET}"
