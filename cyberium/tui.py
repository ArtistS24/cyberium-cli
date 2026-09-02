"""
Cyberium Academy Interactive Terminal User Interface (TUI)
Built with Python Standard Library Curses (Zero External Dependencies)
Optimized for ADHD/Dyslexia readability, mouse navigation, and smooth ergonomics.
"""

import sys
import os
import curses
import textwrap
import subprocess

# Eliminate ESC key delay in ncurses
os.environ.setdefault("ESCDELAY", "25")

from .config import load_config, save_config
from .api import CyberiumClient


def safe_addstr(win, y, x, text, attr=0):
    """Safely write string to window, ignoring boundary errors."""
    try:
        max_y, max_x = win.getmaxyx()
        if y < 0 or y >= max_y or x < 0 or x >= max_x:
            return
        available = max_x - x
        if available <= 0:
            return
        # Clip string safely
        clipped = str(text)[:available]
        if y == max_y - 1 and len(clipped) == available:
            clipped = clipped[:-1]
        win.addstr(y, x, clipped, attr)
    except Exception:
        pass


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
        self.list_scroll = 0
        self.detail_scroll = 0
        self.status_msg = ""
        self.status_color = 1
        self.input_mode = False
        self.input_text = ""
        self.cursor_pos = 0
        self.active_pane = "list"  # 'list' or 'detail'

        self.init_curses()
        self.init_colors()
        self.authenticate()
        self.fetch_data()

    def init_curses(self):
        curses.curs_set(0)
        curses.use_default_colors()
        self.stdscr.keypad(True)
        self.stdscr.nodelay(False)
        try:
            curses.set_escdelay(25)
        except Exception:
            pass
        # Enable mouse events (Clicks, Scrolls)
        try:
            curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        except Exception:
            pass

    def init_colors(self):
        if curses.has_colors():
            curses.init_pair(1, curses.COLOR_WHITE, -1)     # Plain text
            curses.init_pair(2, curses.COLOR_CYAN, -1)      # Cyan titles / accents
            curses.init_pair(3, curses.COLOR_GREEN, -1)     # Green / Solved
            curses.init_pair(4, curses.COLOR_YELLOW, -1)    # Yellow / Active Pending
            curses.init_pair(5, curses.COLOR_RED, -1)       # Red / Error
            curses.init_pair(6, curses.COLOR_MAGENTA, -1)   # Magenta badges
            curses.init_pair(7, 8 if curses.COLORS >= 16 else curses.COLOR_BLACK, -1) # Dim / Borders
            curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_CYAN) # Inverted Cyan Header

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
        self.detail_scroll = 0

    def copy_to_clipboard(self, text):
        """Copy text to local system clipboard via OSC 52 or clipboard tools."""
        # Try local xclip / wl-copy if available
        try:
            p = subprocess.Popen(["wl-copy"], stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
            p.communicate(text.encode("utf-8"))
            if p.returncode == 0:
                return True
        except Exception:
            pass
        try:
            p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
            p.communicate(text.encode("utf-8"))
            if p.returncode == 0:
                return True
        except Exception:
            pass
        return False

    def draw_header(self, max_y, max_x):
        header_text = f" CYBERIUM ACADEMY │ {self.module_name} "
        pct = int(self.answered / self.total * 100) if self.total > 0 else 0
        stats_text = f" Lab: {self.answered}/{self.total} ({pct}%) "

        safe_addstr(self.stdscr, 0, 1, header_text, curses.color_pair(2) | curses.A_BOLD)
        safe_addstr(self.stdscr, 0, max_x - len(stats_text) - 1, stats_text, curses.color_pair(3) | curses.A_BOLD)

        try:
            self.stdscr.attron(curses.color_pair(7))
            self.stdscr.hline(1, 0, curses.ACS_HLINE, max_x)
            self.stdscr.attroff(curses.color_pair(7))
        except Exception:
            pass

    def draw_footer(self, max_y, max_x):
        try:
            self.stdscr.attron(curses.color_pair(7))
            self.stdscr.hline(max_y - 2, 0, curses.ACS_HLINE, max_x)
            self.stdscr.attroff(curses.color_pair(7))
        except Exception:
            pass

        if self.input_mode:
            prompt = " ❯ Submit Answer: "
            safe_addstr(self.stdscr, max_y - 1, 1, prompt, curses.color_pair(4) | curses.A_BOLD)
            ans_x = len(prompt) + 1
            safe_addstr(self.stdscr, max_y - 1, ans_x, self.input_text, curses.color_pair(1) | curses.A_BOLD)
            # Position cursor
            curses.curs_set(1)
            try:
                self.stdscr.move(max_y - 1, ans_x + self.cursor_pos)
            except Exception:
                pass
        else:
            curses.curs_set(0)
            help_items = [
                ("[↑/↓/j/k]", "Select"),
                ("[Enter/i]", "Answer"),
                ("[Tab]", "Scroll Detail"),
                ("[c]", "Copy"),
                ("[m]", "Modules"),
                ("[p]", "Profile"),
                ("[r]", "Refresh"),
                ("[q]", "Quit"),
            ]
            x_pos = 1
            for key, desc in help_items:
                safe_addstr(self.stdscr, max_y - 1, x_pos, key, curses.color_pair(2) | curses.A_BOLD)
                x_pos += len(key) + 1
                safe_addstr(self.stdscr, max_y - 1, x_pos, desc, curses.color_pair(1))
                x_pos += len(desc) + 2
                if x_pos >= max_x - 10:
                    break

    def draw_question_list(self, max_y, max_x, split_x):
        list_h = max_y - 4
        start_y = 2

        # Auto-scroll logic
        if self.selected_idx < self.list_scroll:
            self.list_scroll = self.selected_idx
        elif self.selected_idx >= self.list_scroll + list_h:
            self.list_scroll = self.selected_idx - list_h + 1

        for row in range(list_h):
            q_idx = self.list_scroll + row
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

            max_len = split_x - 3
            item_text = f" {badge} #{idx_num:<2} {text}"
            if len(item_text) > max_len:
                item_text = item_text[:max_len - 1] + "…"
            else:
                item_text = item_text.ljust(max_len)

            if is_selected:
                attr = curses.color_pair(2) | curses.A_REVERSE | curses.A_BOLD if self.active_pane == "list" else curses.color_pair(2) | curses.A_BOLD
                safe_addstr(self.stdscr, start_y + row, 1, item_text, attr)
            else:
                safe_addstr(self.stdscr, start_y + row, 1, item_text, curses.color_pair(pair))

        # Vertical Divider
        try:
            self.stdscr.attron(curses.color_pair(7))
            self.stdscr.vline(2, split_x, curses.ACS_VLINE, max_y - 4)
            self.stdscr.attroff(curses.color_pair(7))
        except Exception:
            pass

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

        # Status Title
        if is_answered:
            status_label = "SOLVED [✓]"
            status_pair = 3
        elif is_active:
            status_label = "ACTIVE OBJECTIVE []"
            status_pair = 4
        else:
            status_label = "UPCOMING [ ]"
            status_pair = 7

        title_line = f"◆ QUESTION #{idx_num}  │  {status_label}"
        safe_addstr(self.stdscr, 2, card_x, title_line, curses.color_pair(status_pair) | curses.A_BOLD)

        try:
            self.stdscr.attron(curses.color_pair(7))
            self.stdscr.hline(3, card_x, curses.ACS_HLINE, card_w)
            self.stdscr.attroff(curses.color_pair(7))
        except Exception:
            pass

        # Text Wrapping & Scrolling
        wrapped_lines = []
        for paragraph in text.split("\n"):
            if not paragraph.strip():
                wrapped_lines.append("")
            else:
                wrapped_lines.extend(textwrap.wrap(paragraph, width=card_w))

        visible_h = max_y - 10
        total_lines = len(wrapped_lines)

        # Clamp detail scroll
        max_scroll = max(0, total_lines - visible_h)
        self.detail_scroll = min(self.detail_scroll, max_scroll)

        for i in range(visible_h):
            line_idx = self.detail_scroll + i
            if line_idx >= total_lines:
                break
            safe_addstr(self.stdscr, 5 + i, card_x, wrapped_lines[line_idx], curses.color_pair(1))

        # Scroll indicator if text is long
        if total_lines > visible_h:
            pct_down = int((self.detail_scroll / max_scroll) * 100) if max_scroll > 0 else 100
            scroll_indicator = f" [Scroll: {self.detail_scroll+1}/{total_lines} ({pct_down}%)] "
            safe_addstr(self.stdscr, max_y - 5, card_x + card_w - len(scroll_indicator), scroll_indicator, curses.color_pair(6) | curses.A_BOLD)

        # Status Notification Banner
        if self.status_msg:
            status_y = max_y - 4
            safe_addstr(self.stdscr, status_y, card_x, f" 󰉋 {self.status_msg}", curses.color_pair(self.status_color) | curses.A_BOLD)

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

        pw = min(54, max_x - 4)
        ph = 11
        px = (max_x - pw) // 2
        py = (max_y - ph) // 2

        popup = curses.newwin(ph, pw, py, px)
        popup.box()
        safe_addstr(popup, 0, 2, " STUDENT PROFILE ", curses.color_pair(2) | curses.A_BOLD)
        safe_addstr(popup, 2, 3, f"Name:     {name}", curses.color_pair(1) | curses.A_BOLD)
        safe_addstr(popup, 3, 3, f"Email:    {email}", curses.color_pair(7))
        safe_addstr(popup, 4, 3, f"Division: {division} ({unit})", curses.color_pair(1))
        safe_addstr(popup, 6, 3, f"Points:   {points} pts", curses.color_pair(3) | curses.A_BOLD)
        safe_addstr(popup, 7, 3, f"Coins:    {coins} coins", curses.color_pair(4) | curses.A_BOLD)
        safe_addstr(popup, 9, 3, "Press [Esc] or [Enter] to close", curses.color_pair(7))

        popup.refresh()
        while True:
            k = popup.getch()
            if k in (27, 10, 13, ord('q'), ord('p'), ord('P')):
                break

    def show_modules_popup(self, max_y, max_x):
        if not self.client:
            return
        data = self.client.get_modules(self.program_id)
        modules = data.get("modules", [])
        if not modules:
            self.status_msg = "No modules found."
            self.status_color = 5
            return

        pw = min(70, max_x - 4)
        ph = min(16, max_y - 4)
        px = (max_x - pw) // 2
        py = (max_y - ph) // 2

        sel_m = 0
        mod_scroll = 0

        # Find current module index
        for idx, m in enumerate(modules):
            if m.get("id") == self.module_id:
                sel_m = idx
                break

        while True:
            popup = curses.newwin(ph, pw, py, px)
            popup.box()
            safe_addstr(popup, 0, 2, " SELECT TRAINING MODULE ", curses.color_pair(2) | curses.A_BOLD)

            visible_count = ph - 4
            if sel_m < mod_scroll:
                mod_scroll = sel_m
            elif sel_m >= mod_scroll + visible_count:
                mod_scroll = sel_m - visible_count + 1

            for row in range(visible_count):
                m_idx = mod_scroll + row
                if m_idx >= len(modules):
                    break
                m = modules[m_idx]
                mid = m.get("id")
                name = m.get("name", "")[:32]
                correct = m.get("lab_correct", 0)
                tot = m.get("lab_total", 0)
                pct = m.get("lab_correct_pct", 0)
                order = m.get("sort_order", m_idx + 1)

                line_str = f" #{order:<2} {name:<32} {correct:>2}/{tot:<2} ({pct:>3}%)"
                if m_idx == sel_m:
                    safe_addstr(popup, 2 + row, 2, line_str[:pw - 4], curses.color_pair(2) | curses.A_REVERSE | curses.A_BOLD)
                else:
                    safe_addstr(popup, 2 + row, 2, line_str[:pw - 4], curses.color_pair(1))

            safe_addstr(popup, ph - 2, 2, "[↑/↓/j/k] Navigate │ [Enter] Select │ [Esc] Cancel", curses.color_pair(7))
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
                self.status_msg = f"Switched to {modules[sel_m].get('name')}"
                self.status_color = 3
                break
            elif key in (27, ord('q'), ord('Q'), ord('m'), ord('M')):
                break

    def handle_submit(self):
        answer = self.input_text.strip()
        if not answer:
            self.input_mode = False
            return

        if not self.questions or self.selected_idx >= len(self.questions):
            return

        q = self.questions[self.selected_idx]
        q_idx = q.get("index", self.selected_idx)

        self.status_msg = f"Submitting answer to #{q_idx}..."
        self.status_color = 4
        self.render()

        resp = self.client.submit_answer(self.module_id, q_idx, answer)

        if resp.get("correct"):
            self.status_msg = f"[✓] CORRECT! Points awarded for question #{q_idx}."
            self.status_color = 3
            self.fetch_data()
        elif resp.get("already_answered"):
            self.status_msg = f"[!] Question #{q_idx} was already completed."
            self.status_color = 4
        else:
            err = resp.get("message") or resp.get("error") or "Incorrect answer. Try again."
            self.status_msg = f"[✗] {err}"
            self.status_color = 5

        self.input_text = ""
        self.cursor_pos = 0
        self.input_mode = False

    def render(self):
        self.stdscr.erase()
        max_y, max_x = self.stdscr.getmaxyx()

        if max_y < 12 or max_x < 50:
            safe_addstr(self.stdscr, 0, 0, "Window too small for Cyberium TUI.", curses.color_pair(5))
            self.stdscr.refresh()
            return

        split_x = max(34, int(max_x * 0.40))

        self.draw_header(max_y, max_x)
        self.draw_question_list(max_y, max_x, split_x)
        self.draw_question_detail(max_y, max_x, split_x)
        self.draw_footer(max_y, max_x)

        self.stdscr.refresh()

    def run(self):
        while True:
            self.render()
            key = self.stdscr.getch()

            if key == curses.KEY_RESIZE:
                continue

            # Mouse interaction
            if key == curses.KEY_MOUSE:
                try:
                    _, mx, my, _, bstate = curses.getmouse()
                    max_y, max_x = self.stdscr.getmaxyx()
                    split_x = max(34, int(max_x * 0.40))

                    if bstate & (curses.BUTTON1_CLICKED | curses.BUTTON1_PRESSED):
                        if 2 <= my < max_y - 2 and mx < split_x:
                            clicked_idx = self.list_scroll + (my - 2)
                            if clicked_idx < len(self.questions):
                                self.selected_idx = clicked_idx
                                self.detail_scroll = 0
                    # Scroll wheel up / down
                    elif bstate & curses.BUTTON4_PRESSED or key == 65536:
                        self.selected_idx = max(0, self.selected_idx - 1)
                    elif bstate & curses.BUTTON5_PRESSED or key == 65537:
                        self.selected_idx = min(len(self.questions) - 1, self.selected_idx + 1)
                except Exception:
                    pass
                continue

            if self.input_mode:
                if key in (10, 13, curses.KEY_ENTER):
                    self.handle_submit()
                elif key == 27:  # ESC cancels input
                    self.input_mode = False
                    self.input_text = ""
                    self.cursor_pos = 0
                elif key in (curses.KEY_BACKSPACE, 127, 8):
                    if self.cursor_pos > 0:
                        self.input_text = self.input_text[:self.cursor_pos - 1] + self.input_text[self.cursor_pos:]
                        self.cursor_pos -= 1
                elif key == curses.KEY_DC:  # Delete key
                    if self.cursor_pos < len(self.input_text):
                        self.input_text = self.input_text[:self.cursor_pos] + self.input_text[self.cursor_pos + 1:]
                elif key == curses.KEY_LEFT:
                    self.cursor_pos = max(0, self.cursor_pos - 1)
                elif key == curses.KEY_RIGHT:
                    self.cursor_pos = min(len(self.input_text), self.cursor_pos + 1)
                elif key in (curses.KEY_HOME, 1):  # Ctrl+A / Home
                    self.cursor_pos = 0
                elif key in (curses.KEY_END, 5):   # Ctrl+E / End
                    self.cursor_pos = len(self.input_text)
                elif key == 21:  # Ctrl+U (Clear line)
                    self.input_text = ""
                    self.cursor_pos = 0
                elif 32 <= key <= 126:
                    self.input_text = self.input_text[:self.cursor_pos] + chr(key) + self.input_text[self.cursor_pos:]
                    self.cursor_pos += 1
            else:
                if key in (ord('q'), ord('Q')):
                    break
                elif key in (curses.KEY_UP, ord('k')):
                    self.selected_idx = max(0, self.selected_idx - 1)
                    self.detail_scroll = 0
                elif key in (curses.KEY_DOWN, ord('j')):
                    self.selected_idx = min(len(self.questions) - 1, self.selected_idx + 1)
                    self.detail_scroll = 0
                elif key in (curses.KEY_PPAGE, ord('u')):  # Page Up / Scroll detail up
                    self.detail_scroll = max(0, self.detail_scroll - 4)
                elif key in (curses.KEY_NPAGE, ord('d')):  # Page Down / Scroll detail down
                    self.detail_scroll += 4
                elif key == 9:  # Tab key toggles detail scrolling
                    self.detail_scroll += 4
                elif key in (ord('i'), ord('I'), 10, 13, curses.KEY_ENTER):
                    self.input_mode = True
                    self.input_text = ""
                    self.cursor_pos = 0
                elif key in (ord('c'), ord('C')):
                    if self.questions and self.selected_idx < len(self.questions):
                        q_text = self.questions[self.selected_idx].get("text", "")
                        if self.copy_to_clipboard(q_text):
                            self.status_msg = "Copied question text to clipboard."
                            self.status_color = 3
                        else:
                            self.status_msg = "Question text ready."
                            self.status_color = 2
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


def start_tui():
    curses.wrapper(lambda stdscr: CyberiumTUI(stdscr).run())


if __name__ == "__main__":
    start_tui()
