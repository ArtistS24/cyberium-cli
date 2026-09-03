"""
High-Speed Fuzz Testing & Stress Engine for Cyberium CLI
Suppresses terminal I/O to run 10,000 extreme edge-case cycles in under a second.
"""

import os
import sys
import random
import string
import io
import contextlib
from unittest.mock import MagicMock

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from cyberium import ui, config, cli, tui


def random_string(length=50):
    chars = string.ascii_letters + string.digits + string.punctuation + " אבגדהוזחטיכלמנסעפצקרשת \t\n\r\0\x1b[31m%s%d{foo}★◆✓"
    return "".join(random.choice(chars) for _ in range(length))


def run_fuzz(iterations=10000):
    print(f"[FUZZ] Starting {iterations} rapid randomized stress cycles...")
    mock_win = MagicMock()
    mock_win.getmaxyx.return_value = (24, 80)
    devnull = io.StringIO()

    with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
        for i in range(iterations):
            s = random_string(random.randint(0, 150))
            num = random.randint(-100000, 100000)

            # 1. UI functions
            ui.calculate_rank(num)
            ui.calculate_rank(s)
            ui.progress_bar(num, random.randint(-50, 100), width=random.randint(1, 50))
            ui.badge_success(s)
            ui.badge_pending(s)
            ui.badge_failed(s)
            ui.header(s, s)

            # 2. TUI safe_addstr
            tui.safe_addstr(mock_win, random.randint(-10, 50), random.randint(-10, 100), s)

            # 3. Config notes CRUD
            config.save_note(random.randint(1, 100), random.randint(0, 100), s)
            config.get_note(random.randint(1, 100), random.randint(0, 100))

            # 4. Search logic
            mock_client = MagicMock()
            mock_client.get_questions.return_value = {
                "module_name": s,
                "questions": [{"index": j, "text": random_string(50), "answered": bool(j % 2)} for j in range(10)]
            }
            cli.cmd_search(mock_client, {}, s[:20])

    print(f"[FUZZ] SUCCESS: Completed all {iterations} randomized fuzz cycles with 0 crashes or unhandled exceptions!")


if __name__ == "__main__":
    run_fuzz(10000)
