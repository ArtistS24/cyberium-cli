"""
Cyberium Academy Interactive Terminal User Interface (TUI)
Built on Python Standard Library Curses (Zero External Dependencies)
"""

import sys
import os
import curses
import textwrap
from .config import load_config, save_config
from .api import CyberiumClient


class CyberiumTUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.cfg = load_config()
        self.client = None
        self.module_id = self.cfg.get("current_module_id", 88)
        self.program_id = self.cfg.get("current_program_id", 10)
        self.questions = []
        self.module_name = ""
        self.total = 0
        self.answered = 0
        self.first_unanswered = 0
        self.selected_idx = 0
        self.scroll_offset = 0
        self.status_msg = ""
        self.status_color = 1
        self.input_mode = False
        self.input_text = ""
        self.profile_data = None
        self.modules_list = []

        self.init_colors()
        self.authenticate()
        self.fetch_data()

    def init_colors(self):
        curses.curs_set(0)
        curses.use_default_colors()
        if curses.has_colors():
            curses.init_pair(1, curses.COLOR_WHITE, -1)     # Default
            curses.init_pair(2, curses.COLOR_CYAN, -1)      # Header / Accents
            curses.init_pair(3, curses.COLOR_GREEN, -1)     # Solved / Success
            curses.init_pair(4, curses.COLOR_YELLOW, -1)    # Active / Pending
            curses.init_pair(5, curses.COLOR_RED, -1)       # Errors / Failed
            curses.init_pair(6, curses.COLOR_MAGENTA, -1)   # Highlights
            curses.init_pair(7, 8 if curses.COLORS >= 16 else curses.COLOR_BLACK, -1) # Dim / Borders

    def authenticate(self):
        try:
            self.client = CyberiumClient(self.cfg)
        except Exception as e:
            self.status_msg = f"Auth failed: {e}"
            self.status_color = 5

    def fetch_data(self):
        if not self.client:
            return
        data = self.client.get_questions(self.module_id)
        if "error" in data:
            self.status_msg = f"Error: {data['error']}"
            self.status_color = 5
            return

        self.module_name = data.get("module_name", f"Module #{self.module_id}")
        self.total = data.get("total", 0)
        self.answered = data.get("answered_count", 0)
        self.first_unanswered = data.get("first_unanswered", 0)
        self.questions = data.get("questions", [])

        if self.first_unanswered is not None and self.first_unanswered < len(self.questions):
            self.selected_idx = self.first_unanswered
        else:
            self.selected_idx = 0

    def draw_header(self, max_y, max_x):
        header_text = f" CYBERIUM ACADEMY │ {self.module_name} "
        pct = int(self.answered / self.total * 100) if self.total > 0 else 0
        stats_text = f" Lab: {self.answered}/{self.total} ({pct}%) "

        self.stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
        self.stdscr.addstr(0, 2, header_text)
        self.stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)

        self.stdscr.attron(curses.color_pair(3))
        self.stdscr.addstr(0, max_x - len(stats_text) - 2, stats_text)
        self.stdscr.attroff(curses.color_pair(3))

        self.stdscr.attron(curses.color_pair(7))
        self.stdscr.hline(1, 0, curses.ACS_HLINE, max_x)
        self.stdscr.attroff(curses.color_pair(7))

    def draw_footer(self, max_y, max_x):
        self.stdscr.attron(curses.color_pair(7))
        self.stdscr.hline(max_y - 2, 0, curses.ACS_HLINE, max_x)
        self.stdscr.attroff(curses.color_pair(7))

        if self.input_mode:
            prompt = " Enter Answer: "
            self.stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
            self.stdscr.addstr(max_y - 1, 1, prompt)
            self.stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)

            self.stdscr.attron(curses.color_pair(1))
            self.stdscr.addstr(max_y - 1, len(prompt) + 1, self.input_text[:max_x - len(prompt) - 10])
            self.stdscr.attroff(curses.color_pair(1))
        else:
            help_keys = " [j/k/↑/↓] Navigate │ [i/Enter] Submit Answer │ [m] Modules │ [p] Profile │ [r] Refresh │ [q] Quit"
            self.stdscr.attron(curses.color_pair(1))
            self.stdscr.addstr(max_y - 1, 1, help_keys[:max_x - 2])
            self.stdscr.attroff(curses.color_pair(1))

    def draw_question_list(self, max_y, max_x, split_x):
        list_h = max_y - 3
        start_y = 2

        if self.selected_idx < self.scroll_offset:
            self.scroll_offset = self.selected_idx
        elif self.selected_idx >= self.scroll_offset + list_h:
            self.scroll_offset = self.selected_idx - list_h + 1

        for row in range(list_h):
            q_idx = self.scroll_offset + row
            if q_idx >= len(self.questions):
                break

            q = self.questions[q_idx]
            is_answered = q.get("answered", False)
            idx_num = q.get("index", q_idx)
            text = q.get("text", "").replace("\n", " ")

            is_selected = (q_idx == self.selected_idx)
            is_active = (q_idx == self.first_unanswered)

            if is_answered:
                badge = "[✓]"
                pair = 3
            elif is_active:
                badge = "[]"
                pair = 4
            else:
                badge = "[ ]"
                pair = 7

            line_str = f" {badge} #{idx_num:<2} {text}"
            max_len = split_x - 3
            if len(line_str) > max_len:
                line_str = line_str[:max_len - 1] + "…"
            else:
                line_str = line_str.ljust(max_len)

            if is_selected:
                self.stdscr.attron(curses.color_pair(2) | curses.A_REVERSE | curses.A_BOLD)
                self.stdscr.addstr(start_y + row, 1, line_str)
                self.stdscr.attroff(curses.color_pair(2) | curses.A_REVERSE | curses.A_BOLD)
            else:
                self.stdscr.attron(curses.color_pair(pair))
                self.stdscr.addstr(start_y + row, 1, line_str)
                self.stdscr.attroff(curses.color_pair(pair))

        self.stdscr.attron(curses.color_pair(7))
        self.stdscr.vline(2, split_x, curses.ACS_VLINE, max_y - 4)
        self.stdscr.attroff(curses.color_pair(7))

    def draw_question_detail(self, max_y, max_x, split_x):
        if not self.questions or self.selected_idx >= len(self.questions):
            return

        q = self.questions[self.selected_idx]
        idx_num = q.get("index", self.selected_idx)
        text = q.get("text", "")
        is_answered = q.get("answered", False)
        is_active = (self.selected_idx == self.first_unanswered)

        card_x = split_x + 2
        card_w = max_x - split_x - 4

        # Title Card
        status_label = "SOLVED [✓]" if is_answered else ("ACTIVE OBJECTIVE []" if is_active else "UPCOMING [ ]")
        status_pair = 3 if is_answered else (4 if is_active else 7)

        self.stdscr.attron(curses.color_pair(status_pair) | curses.A_BOLD)
        self.stdscr.addstr(3, card_x, f"◆ QUESTION #{idx_num} — {status_label}")
        self.stdscr.attroff(curses.color_pair(status_pair) | curses.A_BOLD)

        self.stdscr.attron(curses.color_pair(7))
        self.stdscr.hline(4, card_x, curses.ACS_HLINE, card_w)
        self.stdscr.attroff(curses.color_pair(7))

        # Wrapped Question Body
        wrapped_lines = textwrap.wrap(text, width=card_w)
        for i, line in enumerate(wrapped_lines[:max_y - 12]):
            self.stdscr.attron(curses.color_pair(1))
            self.stdscr.addstr(6 + i, card_x, line)
            self.stdscr.attroff(curses.color_pair(1))

        # Status Message Box
        if self.status_msg:
            status_y = max_y - 5
            self.stdscr.attron(curses.color_pair(self.status_color) | curses.A_BOLD)
            self.stdscr.addstr(status_y, card_x, f"STATUS: {self.status_msg}"[:card_w])
            self.stdscr.attroff(curses.color_pair(self.status_color) | curses.A_BOLD)

    def show_profile_popup(self, max_y, max_x):
        if not self.client:
            return
        data = self.client.get_profile()
        ident = data.get("identity", {}) if "identity" in data else {}
        name = f"{ident.get('firstName', '')} {ident.get('lastName', '')}"
        email = ident.get("email", "")
        division = ident.get("divisionName", "")
        unit = ident.get("unitName", "")
        points = ident.get("trainingPoints", 0)
        coins = ident.get("coinBalance", 0)

        pw = min(50, max_x - 4)
        ph = 10
        px = (max_x - pw) // 2
        py = (max_y - ph) // 2

        popup = curses.newwin(ph, pw, py, px)
        popup.box()
        popup.attron(curses.color_pair(2) | curses.A_BOLD)
        popup.addstr(0, 2, " STUDENT PROFILE ")
        popup.attroff(curses.color_pair(2) | curses.A_BOLD)

        popup.addstr(2, 3, f"Name:     {name}")
        popup.addstr(3, 3, f"Email:    {email}")
        popup.addstr(4, 3, f"Division: {division} ({unit})")
        popup.addstr(5, 3, f"Points:   {points} pts", curses.color_pair(3) | curses.A_BOLD)
        popup.addstr(6, 3, f"Coins:    {coins} coins", curses.color_pair(4) | curses.A_BOLD)
        popup.addstr(8, 3, "Press any key to close...", curses.color_pair(7))

        popup.refresh()
        popup.getch()

    def show_modules_popup(self, max_y, max_x):
        if not self.client:
            return
        data = self.client.get_modules(self.program_id)
        modules = data.get("modules", [])
        if not modules:
            return

        pw = min(60, max_x - 4)
        ph = min(len(modules) + 6, max_y - 4)
        px = (max_x - pw) // 2
        py = (max_y - ph) // 2

        sel_m = 0
        while True:
            popup = curses.newwin(ph, pw, py, px)
            popup.box()
            popup.attron(curses.color_pair(2) | curses.A_BOLD)
            popup.addstr(0, 2, " SELECT MODULE ")
            popup.attroff(curses.color_pair(2) | curses.A_BOLD)

            for i, m in enumerate(modules[:ph - 4]):
                mid = m.get("id")
                name = m.get("name", "")[:30]
                correct = m.get("lab_correct", 0)
                tot = m.get("lab_total", 0)
                pct = m.get("lab_correct_pct", 0)
                line_str = f" #{m.get('sort_order', ''):<2} {name:<26} {correct:>2}/{tot:<2} ({pct}%)"
                if i == sel_m:
                    popup.attron(curses.color_pair(2) | curses.A_REVERSE | curses.A_BOLD)
                    popup.addstr(2 + i, 2, line_str[:pw - 4])
                    popup.attroff(curses.color_pair(2) | curses.A_REVERSE | curses.A_BOLD)
                else:
                    popup.addstr(2 + i, 2, line_str[:pw - 4])

            popup.addstr(ph - 2, 2, "[Enter] Select │ [Esc] Cancel", curses.color_pair(7))
            popup.refresh()

            key = popup.getch()
            if key in (curses.KEY_UP, ord('k')):
                sel_m = max(0, sel_m - 1)
            elif key in (curses.KEY_DOWN, ord('j')):
                sel_m = min(len(modules) - 1, sel_m + 1)
            elif key in (10, 13, curses.KEY_ENTER):
                target_mod = modules[sel_m].get("id")
                self.module_id = target_mod
                self.cfg["current_module_id"] = target_mod
                save_config(self.cfg)
                self.fetch_data()
                break
            elif key in (27, ord('q')):
                break

    def handle_submit(self):
        if not self.input_text.strip():
            self.input_mode = False
            return

        if not self.questions or self.selected_idx >= len(self.questions):
            return

        q = self.questions[self.selected_idx]
        q_idx = q.get("index", self.selected_idx)

        self.status_msg = f"Submitting answer to #{q_idx}..."
        self.status_color = 4
        self.render()

        resp = self.client.submit_answer(self.module_id, q_idx, self.input_text.strip())

        if resp.get("correct"):
            self.status_msg = f"[✓] CORRECT! Points awarded for question #{q_idx}."
            self.status_color = 3
            self.fetch_data()
        elif resp.get("already_answered"):
            self.status_msg = f"[!] Question #{q_idx} was already answered."
            self.status_color = 4
        else:
            err = resp.get("message") or resp.get("error") or "Incorrect answer. Try again."
            self.status_msg = f"[✗] {err}"
            self.status_color = 5

        self.input_text = ""
        self.input_mode = False

    def render(self):
        self.stdscr.clear()
        max_y, max_x = self.stdscr.getmaxyx()

        if max_y < 12 or max_x < 50:
            self.stdscr.addstr(0, 0, "Terminal window too small for TUI.")
            self.stdscr.refresh()
            return

        split_x = max(35, int(max_x * 0.42))

        self.draw_header(max_y, max_x)
        self.draw_question_list(max_y, max_x, split_x)
        self.draw_question_detail(max_y, max_x, split_x)
        self.draw_footer(max_y, max_x)

        self.stdscr.refresh()

    def run(self):
        while True:
            self.render()
            key = self.stdscr.getch()

            if self.input_mode:
                if key in (10, 13, curses.KEY_ENTER):
                    self.handle_submit()
                elif key in (27,):  # ESC
                    self.input_mode = False
                    self.input_text = ""
                elif key in (curses.KEY_BACKSPACE, 127, 8):
                    self.input_text = self.input_text[:-1]
                elif 32 <= key <= 126:
                    self.input_text += chr(key)
            else:
                if key in (ord('q'), ord('Q')):
                    break
                elif key in (curses.KEY_UP, ord('k')):
                    self.selected_idx = max(0, self.selected_idx - 1)
                elif key in (curses.KEY_DOWN, ord('j')):
                    self.selected_idx = min(len(self.questions) - 1, self.selected_idx + 1)
                elif key in (ord('i'), ord('I'), 10, 13, curses.KEY_ENTER):
                    self.input_mode = True
                    self.input_text = ""
                    curses.curs_set(1)
                elif key in (ord('m'), ord('M')):
                    max_y, max_x = self.stdscr.getmaxyx()
                    self.show_modules_popup(max_y, max_x)
                elif key in (ord('p'), ord('P')):
                    max_y, max_x = self.stdscr.getmaxyx()
                    self.show_profile_popup(max_y, max_x)
                elif key in (ord('r'), ord('R')):
                    self.status_msg = "Refreshing platform data..."
                    self.status_color = 2
                    self.render()
                    self.fetch_data()
                    self.status_msg = "Platform data refreshed."
                    self.status_color = 3

            if not self.input_mode:
                curses.curs_set(0)


def start_tui():
    curses.wrapper(lambda stdscr: CyberiumTUI(stdscr).run())


if __name__ == "__main__":
    start_tui()
