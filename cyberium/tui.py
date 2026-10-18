"""
Cyberium Academy Interactive Terminal User Interface (TUI)
Built with Python Standard Library Curses (Zero External Dependencies)
Faithful to the Cyberium Academy student dashboard & dark obsidian aesthetic.
"""

import sys
import os
import curses
import textwrap
import subprocess

# Eliminate ESC key lag in ncurses
os.environ.setdefault("ESCDELAY", "25")

from .config import load_config, save_config, get_note, save_note, clear_session, BOOKS_DIR
from .api import CyberiumClient, get_book_info, download_file
from .ui import calculate_rank, THEMES, ICON_LIVE, copy_to_clipboard, format_question_text, extract_urls


def safe_addstr(win, y, x, text, attr=0):
    """Safely write string to window, ignoring boundary errors."""
    try:
        max_y, max_x = win.getmaxyx()
        if y < 0 or y >= max_y or x < 0 or x >= max_x:
            return
        available = max_x - x
        if available <= 0:
            return
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
        self.theme_name = self.cfg.get("theme", "cyberium")
        if self.theme_name not in THEMES:
            self.theme_name = "cyberium"

        self.module_id = self.cfg.get("current_module_id")
        self.program_id = self.cfg.get("current_program_id")
        self.program_name = ""
        self.unit_name = ""
        self.questions = []
        self.filtered_questions = []
        self.module_name = ""
        self.module_open = True
        self.module_completed = False
        self.total = 0
        self.answered = 0
        self.first_unanswered = 0
        self.selected_idx = 0
        self.list_scroll = 0
        self.detail_scroll = 0
        self.status_msg = ""
        self.status_color = 1
        self.input_mode = False       # True when answering question
        self.search_mode = False      # True when filtering questions
        self.input_text = ""
        self.search_text = ""
        self.cursor_pos = 0
        self.q_type = "lab"           # "lab" or "extra"
        self.profile_pts = 0
        self.profile_coins = 0
        self.profile_data = {}

        self.init_curses()
        self.init_colors()
        self.authenticate()
        self.fetch_profile_stats()
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
        try:
            curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        except Exception:
            pass

    def init_colors(self):
        if not curses.has_colors():
            return

        color_map = {
            "white": curses.COLOR_WHITE,
            "cyan": curses.COLOR_CYAN,
            "green": curses.COLOR_GREEN,
            "yellow": curses.COLOR_YELLOW,
            "red": curses.COLOR_RED,
            "magenta": curses.COLOR_MAGENTA,
            "blue": curses.COLOR_BLUE,
            "dim": 8 if curses.COLORS >= 16 else curses.COLOR_BLACK,
            "black": curses.COLOR_BLACK,
        }

        t_data = THEMES.get(self.theme_name, THEMES["cyberium"])
        for pair_idx in range(1, 8):
            col_name = t_data.get(f"pair{pair_idx}", "white")
            fg_col = color_map.get(col_name, curses.COLOR_WHITE)
            curses.init_pair(pair_idx, fg_col, -1)

    def authenticate(self):
        try:
            self.client = CyberiumClient(self.cfg)
        except Exception as e:
            self.status_msg = f"Auth failed: {e}"
            self.status_color = 5

    def fetch_profile_stats(self):
        if not self.client:
            return
        try:
            data = self.client.get_profile()
            self.profile_data = data
            ident = data.get("identity", {}) if isinstance(data, dict) and "identity" in data else {}
            self.profile_pts = ident.get("trainingPoints", 0)
            self.profile_coins = ident.get("coinBalance", 0)
            self.unit_name = ident.get("unitName", "Cyberium")
        except Exception:
            pass

    def fetch_data(self):
        if not self.client:
            return

        needs_save = False

        # 1. Fetch Programs to resolve active program and program name
        progs_data = self.client.get_programs()
        progs = progs_data if isinstance(progs_data, list) else (progs_data.get("programs", []) if isinstance(progs_data, dict) else [])
        
        if not self.program_id and progs:
            active_p = next((p for p in progs if p.get("completion_pct", 0) > 0), progs[0])
            self.program_id = active_p.get("id")
            self.cfg["current_program_id"] = self.program_id
            needs_save = True

        for p in progs:
            if p.get("id") == self.program_id:
                self.program_name = f"{p.get('code', '')} {p.get('name', '')}".strip()
                break

        if not self.program_name:
            self.program_name = f"Track #{self.program_id}" if self.program_id else "Cyberium Training"

        # 2. Check module metadata (is_open, lab_completed)
        if self.program_id:
            mods_data = self.client.get_modules(self.program_id)
            mods = mods_data.get("modules", []) if isinstance(mods_data, dict) else []

            if not self.module_id and mods:
                active_m = next((m for m in mods if m.get("is_open") and not m.get("lab_completed")), None)
                if not active_m:
                    active_m = next((m for m in mods if m.get("is_open")), mods[0])
                self.module_id = active_m.get("id")
                self.cfg["current_module_id"] = self.module_id
                needs_save = True

            for m in mods:
                if m.get("id") == self.module_id:
                    self.module_open = m.get("is_open", True)
                    self.module_completed = m.get("lab_completed", False)
                    break

        if needs_save:
            save_config(self.cfg)

        # 3. Fetch Questions for Current Module
        if not self.module_id:
            self.status_msg = "No active module selected. Press [m] to choose a module."
            self.status_color = 4
            self.questions = []
            self.filtered_questions = []
            return

        data = self.client.get_questions(self.module_id, q_type=self.q_type)
        if "error" in data:
            self.status_msg = f"{data['error']}"
            self.status_color = 5
            self.questions = []
            self.filtered_questions = []
            return

        self.module_name = data.get("module_name", f"Module #{self.module_id}")
        self.total = data.get("total", 0)
        self.answered = data.get("answered_count", 0)
        self.first_unanswered = data.get("first_unanswered", 0)
        self.questions = data.get("questions", [])

        self.apply_filter()

        if self.first_unanswered is not None and self.first_unanswered < len(self.filtered_questions):
            self.selected_idx = self.first_unanswered
        else:
            self.selected_idx = 0
        self.detail_scroll = 0

    def apply_filter(self):
        if not self.search_text.strip():
            self.filtered_questions = self.questions
        else:
            term = self.search_text.lower().strip()
            self.filtered_questions = [q for q in self.questions if term in q.get("text", "").lower()]
        self.selected_idx = min(self.selected_idx, max(0, len(self.filtered_questions) - 1))

    def copy_to_clipboard(self, text):
        return copy_to_clipboard(text)

    def draw_header(self, max_y, max_x):
        rank_title, _ = calculate_rank(self.profile_pts)
        type_badge = " [EXTRA]" if self.q_type == "extra" else ""
        header_text = f" C Y B E R I U M │ {self.unit_name} │ {self.program_name} › {self.module_name}{type_badge} "
        pct = int(self.answered / self.total * 100) if self.total > 0 else (100 if self.module_completed else 0)
        stats_text = f" {self.answered}/{self.total} Solved ({pct}%) │ {rank_title} • {self.profile_pts} pts ◆ {self.profile_coins} coins "

        safe_addstr(self.stdscr, 0, 1, header_text, curses.color_pair(2) | curses.A_BOLD)
        safe_addstr(self.stdscr, 0, max_x - len(stats_text) - 1, stats_text, curses.color_pair(4) | curses.A_BOLD)

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
            prompt = f" ❯ Submit Answer ({self.q_type.upper()}): "
            safe_addstr(self.stdscr, max_y - 1, 1, prompt, curses.color_pair(4) | curses.A_BOLD)
            ans_x = len(prompt) + 1
            safe_addstr(self.stdscr, max_y - 1, ans_x, self.input_text, curses.color_pair(1) | curses.A_BOLD)
            curses.curs_set(1)
            try:
                self.stdscr.move(max_y - 1, ans_x + self.cursor_pos)
            except Exception:
                pass
        elif self.search_mode:
            prompt = "  Search Questions: "
            safe_addstr(self.stdscr, max_y - 1, 1, prompt, curses.color_pair(2) | curses.A_BOLD)
            ans_x = len(prompt) + 1
            safe_addstr(self.stdscr, max_y - 1, ans_x, self.search_text, curses.color_pair(1) | curses.A_BOLD)
            curses.curs_set(1)
            try:
                self.stdscr.move(max_y - 1, ans_x + self.cursor_pos)
            except Exception:
                pass
        else:
            curses.curs_set(0)
            help_items = [
                ("[↑/↓]", "Nav"),
                ("[Enter]", "Answer"),
                ("[/]", "Search"),
                ("[l]", "Links"),
                ("[n]", "Note"),
                ("[m]", "Modules"),
                ("[P]", "Tracks"),
                ("[x]", "Extra" if self.q_type == "lab" else "Labs"),
                ("[t]", "Theme"),
                ("[b]", "Book"),
                ("[v]", "Video"),
                ("[p]", "Profile"),
                ("[L]", "Logout"),
                ("[q]", "Quit"),
            ]
            x_pos = 1
            for key, desc in help_items:
                safe_addstr(self.stdscr, max_y - 1, x_pos, key, curses.color_pair(2) | curses.A_BOLD)
                x_pos += len(key) + 1
                safe_addstr(self.stdscr, max_y - 1, x_pos, desc, curses.color_pair(1))
                x_pos += len(desc) + 2
                if x_pos >= max_x - 6:
                    break

    def draw_question_list(self, max_y, max_x, split_x):
        list_h = max_y - 4
        start_y = 2

        if not self.filtered_questions:
            if self.search_text:
                status_text = f" [NO MATCHES FOR '{self.search_text[:14]}'] "
                safe_addstr(self.stdscr, start_y + 2, 2, status_text, curses.color_pair(5) | curses.A_BOLD)
                safe_addstr(self.stdscr, start_y + 4, 2, " Press [Esc] to clear search filter", curses.color_pair(7))
            elif not self.module_open:
                status_text = " [LOCKED BY LECTURER] "
                safe_addstr(self.stdscr, start_y + 2, 2, status_text, curses.color_pair(5) | curses.A_BOLD)
                safe_addstr(self.stdscr, start_y + 4, 2, " Press [m] to pick an open module", curses.color_pair(7))
            elif self.q_type == "extra":
                status_text = " [EXTRA LABS LOCKED] "
                safe_addstr(self.stdscr, start_y + 2, 2, status_text, curses.color_pair(5) | curses.A_BOLD)
                safe_addstr(self.stdscr, start_y + 4, 2, " Requires >= 80% score on Core Labs", curses.color_pair(4))
                safe_addstr(self.stdscr, start_y + 6, 2, " Press [x] to return to Core Labs", curses.color_pair(2))
            else:
                status_text = " [NO LABS IN THIS MODULE] "
                safe_addstr(self.stdscr, start_y + 2, 2, status_text, curses.color_pair(5) | curses.A_BOLD)
                safe_addstr(self.stdscr, start_y + 4, 2, " Press [m] to pick an active module", curses.color_pair(7))
        else:
            if self.selected_idx < self.list_scroll:
                self.list_scroll = self.selected_idx
            elif self.selected_idx >= self.list_scroll + list_h:
                self.list_scroll = self.selected_idx - list_h + 1

            for row in range(list_h):
                q_idx = self.list_scroll + row
                if q_idx >= len(self.filtered_questions):
                    break

                q = self.filtered_questions[q_idx]
                is_answered = q.get("answered", False)
                idx_num = q.get("index", q_idx)
                raw_text = q.get("text", "")
                cleaned_text, urls = format_question_text(raw_text, ansi=False)
                text = cleaned_text.replace("\n", " ")

                is_selected = (q_idx == self.selected_idx)
                is_active = (q_idx == self.first_unanswered)

                # Check if question has a student note attached or attached resources
                has_note = bool(get_note(self.module_id, idx_num))
                note_glyph = " 󰉋" if has_note else ""
                res_glyph = " 󰌹" if urls else ""

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
                item_text = f" {badge} #{idx_num:<2}{note_glyph}{res_glyph} {text}"
                if len(item_text) > max_len:
                    item_text = item_text[:max_len - 1] + "…"
                else:
                    item_text = item_text.ljust(max_len)

                if is_selected:
                    safe_addstr(self.stdscr, start_y + row, 1, item_text, curses.color_pair(2) | curses.A_REVERSE | curses.A_BOLD)
                else:
                    safe_addstr(self.stdscr, start_y + row, 1, item_text, curses.color_pair(pair))

        try:
            self.stdscr.attron(curses.color_pair(7))
            self.stdscr.vline(2, split_x, curses.ACS_VLINE, max_y - 4)
            self.stdscr.attroff(curses.color_pair(7))
        except Exception:
            pass

    def draw_question_detail(self, max_y, max_x, split_x):
        card_x = split_x + 2
        card_w = max_x - split_x - 4

        if not self.filtered_questions:
            if not self.module_open:
                safe_addstr(self.stdscr, 3, card_x, "◆ MODULE ACCESS: LOCKED []", curses.color_pair(5) | curses.A_BOLD)
                safe_addstr(self.stdscr, 5, card_x, "The lecturer has not unlocked this module yet.", curses.color_pair(1))
                safe_addstr(self.stdscr, 7, card_x, "• Check back after your next class lesson.", curses.color_pair(7))
                safe_addstr(self.stdscr, 8, card_x, "• Press [m] to select an open module with active labs.", curses.color_pair(4) | curses.A_BOLD)
                safe_addstr(self.stdscr, 9, card_x, "• Press [P] to switch to another training track.", curses.color_pair(2) | curses.A_BOLD)
            elif self.q_type == "extra":
                safe_addstr(self.stdscr, 3, card_x, "◆ BONUS / EXTRA CHALLENGES LOCKED", curses.color_pair(5) | curses.A_BOLD)
                safe_addstr(self.stdscr, 5, card_x, "Cyberium requires completing >=80% of Core Labs to unlock bonus tasks.", curses.color_pair(1))
                safe_addstr(self.stdscr, 7, card_x, "• Complete remaining Core Labs first to earn bonus access.", curses.color_pair(4))
                safe_addstr(self.stdscr, 8, card_x, "• Press [x] to return to Core Lab Objectives.", curses.color_pair(2) | curses.A_BOLD)
            else:
                safe_addstr(self.stdscr, 3, card_x, "◆ MODULE STATUS: NO LAB EXERCISES", curses.color_pair(4) | curses.A_BOLD)
                safe_addstr(self.stdscr, 5, card_x, "This module contains lecture/book material only (0 labs).", curses.color_pair(1))
                safe_addstr(self.stdscr, 7, card_x, "Press [m] to select a module with hands-on labs.", curses.color_pair(2))
            return

        if self.selected_idx >= len(self.filtered_questions):
            return

        q = self.filtered_questions[self.selected_idx]
        idx_num = q.get("index", self.selected_idx)
        raw_text = q.get("text", "")
        formatted_text, urls = format_question_text(raw_text, ansi=False)
        is_answered = q.get("answered", False)
        is_active = (self.selected_idx == self.first_unanswered)

        if is_answered:
            status_label = "SOLVED [✓]"
            status_pair = 3
        elif is_active:
            status_label = "ACTIVE OBJECTIVE []"
            status_pair = 4
        else:
            status_label = "UPCOMING [ ]"
            status_pair = 7

        mode_prefix = "EXTRA #" if self.q_type == "extra" else "QUESTION #"
        title_line = f"◆ {mode_prefix}{idx_num}  │  {status_label}"
        safe_addstr(self.stdscr, 2, card_x, title_line, curses.color_pair(status_pair) | curses.A_BOLD)

        try:
            self.stdscr.attron(curses.color_pair(7))
            self.stdscr.hline(3, card_x, curses.ACS_HLINE, card_w)
            self.stdscr.attroff(curses.color_pair(7))
        except Exception:
            pass

        # Check for personal student note
        note_text = get_note(self.module_id, idx_num)

        wrapped_lines = []
        for paragraph in formatted_text.split("\n"):
            if not paragraph.strip():
                wrapped_lines.append("")
            else:
                wrapped_lines.extend(textwrap.wrap(paragraph, width=card_w))

        if urls:
            wrapped_lines.append("")
            wrapped_lines.append("󰌹 ATTACHED LAB RESOURCES:")
            for u in urls:
                fname = u.split("/")[-1] if "/" in u else u
                wrapped_lines.append(f"  • {fname}")
            wrapped_lines.append("    [Press 'l' to open / download / copy link]")

        if note_text:
            wrapped_lines.append("")
            wrapped_lines.append(f"󰉋 PERSONAL NOTE: {note_text}")

        visible_h = max_y - 10
        total_lines = len(wrapped_lines)

        max_scroll = max(0, total_lines - visible_h)
        self.detail_scroll = min(self.detail_scroll, max_scroll)

        for i in range(visible_h):
            line_idx = self.detail_scroll + i
            if line_idx >= total_lines:
                break
            line_content = wrapped_lines[line_idx]
            if "󰉋 PERSONAL NOTE:" in line_content:
                safe_addstr(self.stdscr, 5 + i, card_x, line_content, curses.color_pair(2) | curses.A_BOLD)
            elif "󰌹 ATTACHED LAB RESOURCES:" in line_content:
                safe_addstr(self.stdscr, 5 + i, card_x, line_content, curses.color_pair(4) | curses.A_BOLD)
            elif line_content.strip().startswith("• ") or "Press 'l'" in line_content:
                safe_addstr(self.stdscr, 5 + i, card_x, line_content, curses.color_pair(2))
            else:
                safe_addstr(self.stdscr, 5 + i, card_x, line_content, curses.color_pair(1))

        if total_lines > visible_h:
            pct_down = int((self.detail_scroll / max_scroll) * 100) if max_scroll > 0 else 100
            scroll_indicator = f" [Scroll: {self.detail_scroll+1}/{total_lines} ({pct_down}%)] "
            safe_addstr(self.stdscr, max_y - 5, card_x + card_w - len(scroll_indicator), scroll_indicator, curses.color_pair(6) | curses.A_BOLD)

        if self.status_msg:
            status_y = max_y - 4
            safe_addstr(self.stdscr, status_y, card_x, f" 󰉋 {self.status_msg}", curses.color_pair(self.status_color) | curses.A_BOLD)

    def show_note_popup(self, max_y, max_x):
        """Add or edit personal scratchpad note for current question."""
        if not self.filtered_questions or self.selected_idx >= len(self.filtered_questions):
            return
        q = self.filtered_questions[self.selected_idx]
        q_idx = q.get("index", self.selected_idx)
        current_note = get_note(self.module_id, q_idx)

        pw = min(70, max_x - 4)
        ph = 8
        px = (max_x - pw) // 2
        py = (max_y - ph) // 2

        popup = curses.newwin(ph, pw, py, px)
        popup.keypad(True)
        popup.box()

        note_buffer = current_note
        cursor_pos = len(note_buffer)

        while True:
            popup.erase()
            popup.box()
            safe_addstr(popup, 0, 2, f" SCRATCHPAD NOTE: QUESTION #{q_idx} ", curses.color_pair(2) | curses.A_BOLD)
            safe_addstr(popup, 2, 2, "Note: ", curses.color_pair(4) | curses.A_BOLD)
            safe_addstr(popup, 2, 8, note_buffer[:pw - 12], curses.color_pair(1))
            safe_addstr(popup, ph - 2, 2, "[Enter] Save Note │ [Ctrl+U] Clear │ [Esc] Cancel", curses.color_pair(7))

            curses.curs_set(1)
            try:
                popup.move(2, 8 + cursor_pos)
            except Exception:
                pass
            popup.refresh()

            k = popup.getch()
            if k in (10, 13, curses.KEY_ENTER):
                save_note(self.module_id, q_idx, note_buffer)
                self.status_msg = f"Saved note for Question #{q_idx}."
                self.status_color = 3
                curses.curs_set(0)
                break
            elif k == 27:  # ESC
                curses.curs_set(0)
                break
            elif k in (curses.KEY_BACKSPACE, 127, 8):
                if cursor_pos > 0:
                    note_buffer = note_buffer[:cursor_pos - 1] + note_buffer[cursor_pos:]
                    cursor_pos -= 1
            elif k == 21:  # Ctrl+U
                note_buffer = ""
                cursor_pos = 0
            elif k == curses.KEY_LEFT:
                cursor_pos = max(0, cursor_pos - 1)
            elif k == curses.KEY_RIGHT:
                cursor_pos = min(len(note_buffer), cursor_pos + 1)
            elif 32 <= k <= 126 and len(note_buffer) < pw - 14:
                note_buffer = note_buffer[:cursor_pos] + chr(k) + note_buffer[cursor_pos:]
                cursor_pos += 1

    def show_themes_popup(self, max_y, max_x):
        """Scrollable Theme Selector Modal."""
        theme_keys = list(THEMES.keys())
        pw = min(74, max_x - 4)
        ph = min(16, max_y - 4)
        px = (max_x - pw) // 2
        py = (max_y - ph) // 2

        sel_t = 0
        theme_scroll = 0
        for idx, k in enumerate(theme_keys):
            if k == self.theme_name:
                sel_t = idx
                break

        while True:
            popup = curses.newwin(ph, pw, py, px)
            popup.keypad(True)
            popup.box()
            safe_addstr(popup, 0, 2, " TERMINAL THEMES & DESKTOP RICE PALETTES ", curses.color_pair(2) | curses.A_BOLD)

            visible_count = ph - 4
            if sel_t < theme_scroll:
                theme_scroll = sel_t
            elif sel_t >= theme_scroll + visible_count:
                theme_scroll = sel_t - visible_count + 1

            for row in range(visible_count):
                t_idx = theme_scroll + row
                if t_idx >= len(theme_keys):
                    break
                tid = theme_keys[t_idx]
                info = THEMES[tid]
                t_name = info.get("name", tid)
                t_desc = info.get("desc", "")[:28]
                mark = "●" if tid == self.theme_name else "○"

                line_str = f" {mark} {t_name:<24} │ {t_desc}"
                if t_idx == sel_t:
                    safe_addstr(popup, 2 + row, 2, line_str[:pw - 4], curses.color_pair(2) | curses.A_REVERSE | curses.A_BOLD)
                else:
                    safe_addstr(popup, 2 + row, 2, line_str[:pw - 4], curses.color_pair(1))

            safe_addstr(popup, ph - 2, 2, "[↑/↓/j/k] Select │ [Enter] Apply Theme │ [Esc] Cancel", curses.color_pair(7))
            popup.refresh()

            key = popup.getch()
            if key in (curses.KEY_UP, ord('k')):
                sel_t = max(0, sel_t - 1)
            elif key in (curses.KEY_DOWN, ord('j')):
                sel_t = min(len(theme_keys) - 1, sel_t + 1)
            elif key in (10, 13, curses.KEY_ENTER):
                new_theme = theme_keys[sel_t]
                self.theme_name = new_theme
                self.cfg["theme"] = new_theme
                save_config(self.cfg)
                self.init_colors()
                self.status_msg = f"Theme applied: {THEMES[new_theme]['name']}"
                self.status_color = 3
                break
            elif key in (27, ord('q'), ord('Q'), ord('t'), ord('T')):
                break

    def show_profile_popup(self, max_y, max_x):
        """Dossier Popup matching Cyberium Dashboard."""
        if not self.client:
            return
        data = self.client.get_profile()
        ident = data.get("identity", {}) if isinstance(data, dict) and "identity" in data else {}
        name = f"{ident.get('firstName', '')} {ident.get('lastName', '')}".strip() or "Student Operator"
        scode = ident.get("studentCode") or ident.get("sCode", "")
        division = ident.get("divisionName", "Cyberium Academy")
        unit = ident.get("unitName", "Unit")
        points = ident.get("trainingPoints", 0)
        coins = ident.get("coinBalance", 0)
        rank_title, _ = calculate_rank(points)

        pbr = data.get("pbr", {}) if isinstance(data, dict) else {}
        off_pbr = pbr.get("offense", 0)
        soc_pbr = pbr.get("soc", 0)
        def_pbr = pbr.get("defense", 0)

        trophies = data.get("trophies", {}) if isinstance(data, dict) else {}
        gold_t = trophies.get("gold", 0)
        silv_t = trophies.get("silver", 0)
        brnz_t = trophies.get("bronze", 0)
        certs = len(data.get("certifications", [])) if isinstance(data, dict) else 0

        pw = min(68, max_x - 4)
        ph = 15
        px = (max_x - pw) // 2
        py = (max_y - ph) // 2

        popup = curses.newwin(ph, pw, py, px)
        popup.keypad(True)
        popup.box()
        safe_addstr(popup, 0, 2, " CYBERIUM ACADEMY │ OPERATOR DOSSIER ", curses.color_pair(2) | curses.A_BOLD)
        
        scode_str = f" ({scode})" if scode else ""
        safe_addstr(popup, 2, 3, f"Operator: {name}{scode_str}", curses.color_pair(1) | curses.A_BOLD)
        safe_addstr(popup, 2, 36, f"Division: {division} ({unit})", curses.color_pair(2))
        
        safe_addstr(popup, 3, 3, f"Rank:     {rank_title}", curses.color_pair(4) | curses.A_BOLD)
        safe_addstr(popup, 3, 36, f"Status:   SPECTO ● LIVE", curses.color_pair(3) | curses.A_BOLD)

        safe_addstr(popup, 5, 3, f"Points:   {points} pts", curses.color_pair(3) | curses.A_BOLD)
        safe_addstr(popup, 5, 24, f"Coins: {coins} coins", curses.color_pair(4) | curses.A_BOLD)
        safe_addstr(popup, 5, 44, f"Certs: {certs} verified", curses.color_pair(2))

        try:
            popup.attron(curses.color_pair(7))
            popup.hline(7, 3, curses.ACS_HLINE, pw - 6)
            popup.attroff(curses.color_pair(7))
        except Exception:
            pass

        safe_addstr(popup, 8, 3, "PERFORMANCE BENCHMARK (PBR):", curses.color_pair(2) | curses.A_BOLD)
        safe_addstr(popup, 9, 3, f"  Offense: {off_pbr}%   SOC Operations: {soc_pbr}%   Defense: {def_pbr}%", curses.color_pair(1))

        safe_addstr(popup, 11, 3, "TROPHIES & SPECIALIZATIONS:", curses.color_pair(4) | curses.A_BOLD)
        safe_addstr(popup, 12, 3, f"  ★ {gold_t} Gold Trophies   ★ {silv_t} Silver   ★ {brnz_t} Bronze", curses.color_pair(1))

        safe_addstr(popup, ph - 2, 3, "Press [Esc] or [Enter] to close dossier", curses.color_pair(7))

        popup.refresh()
        while True:
            k = popup.getch()
            if k in (27, 10, 13, ord('q'), ord('p'), ord('P'), curses.KEY_ENTER):
                break

    def show_programs_popup(self, max_y, max_x):
        """Browse and switch between all enrolled Programs (ZX310, NX201, etc.)."""
        if not self.client:
            return
        progs_data = self.client.get_programs()
        programs = progs_data if isinstance(progs_data, list) else progs_data.get("programs", [])
        if not programs:
            self.status_msg = "No enrolled programs found."
            self.status_color = 5
            return

        pw = min(74, max_x - 4)
        ph = min(16, max_y - 4)
        px = (max_x - pw) // 2
        py = (max_y - ph) // 2

        sel_p = 0
        prog_scroll = 0

        for idx, p in enumerate(programs):
            if p.get("id") == self.program_id:
                sel_p = idx
                break

        while True:
            popup = curses.newwin(ph, pw, py, px)
            popup.keypad(True)
            popup.box()
            safe_addstr(popup, 0, 2, " ENROLLED TRAINING PROGRAMS ", curses.color_pair(2) | curses.A_BOLD)

            visible_count = ph - 4
            if sel_p < prog_scroll:
                prog_scroll = sel_p
            elif sel_p >= prog_scroll + visible_count:
                prog_scroll = sel_p - visible_count + 1

            for row in range(visible_count):
                p_idx = prog_scroll + row
                if p_idx >= len(programs):
                    break
                p = programs[p_idx]
                code = p.get("code", "")
                name = p.get("name", "")[:28]
                tot_m = p.get("total_modules", "0")
                comp_m = p.get("completed_modules", "0")
                pct = p.get("completion_pct", 0)

                line_str = f" {code:<6} {name:<28} {comp_m:>2}/{tot_m:<2} Mods ({pct:>3}%)"
                if p_idx == sel_p:
                    safe_addstr(popup, 2 + row, 2, line_str[:pw - 4], curses.color_pair(2) | curses.A_REVERSE | curses.A_BOLD)
                else:
                    safe_addstr(popup, 2 + row, 2, line_str[:pw - 4], curses.color_pair(1))

            safe_addstr(popup, ph - 2, 2, "[↑/↓/j/k] Select │ [Enter] Open Track │ [Esc] Cancel", curses.color_pair(7))
            popup.refresh()

            key = popup.getch()
            if key in (curses.KEY_UP, ord('k')):
                sel_p = max(0, sel_p - 1)
            elif key in (curses.KEY_DOWN, ord('j')):
                sel_p = min(len(programs) - 1, sel_p + 1)
            elif key in (10, 13, curses.KEY_ENTER):
                target_prog = programs[sel_p]
                self.program_id = target_prog.get("id")
                self.program_name = f"{target_prog.get('code', '')} {target_prog.get('name', '')}".strip()
                self.cfg["current_program_id"] = self.program_id
                
                # Automatically pick first open module of this new program
                mods_data = self.client.get_modules(self.program_id)
                mods = mods_data.get("modules", [])
                chosen_mod = None
                for m in mods:
                    if m.get("is_open") and not m.get("lab_completed"):
                        chosen_mod = m.get("id")
                        break
                if not chosen_mod and mods:
                    chosen_mod = mods[0].get("id")

                if chosen_mod:
                    self.module_id = chosen_mod
                    self.cfg["current_module_id"] = chosen_mod

                save_config(self.cfg)
                self.fetch_data()
                self.status_msg = f"Switched to program: {self.program_name}"
                self.status_color = 3
                break
            elif key in (27, ord('q'), ord('Q'), ord('P')):
                break

    def show_modules_popup(self, max_y, max_x):
        """Browse and switch between Modules for current program with Unlock Awareness."""
        if not self.client:
            return
        data = self.client.get_modules(self.program_id)
        modules = data.get("modules", [])
        if not modules:
            self.status_msg = "No modules found for this program."
            self.status_color = 5
            return

        pw = min(76, max_x - 4)
        ph = min(16, max_y - 4)
        px = (max_x - pw) // 2
        py = (max_y - ph) // 2

        sel_m = 0
        mod_scroll = 0

        for idx, m in enumerate(modules):
            if m.get("id") == self.module_id:
                sel_m = idx
                break

        while True:
            popup = curses.newwin(ph, pw, py, px)
            popup.keypad(True)
            popup.box()
            safe_addstr(popup, 0, 2, f" {self.program_name} │ MODULES ", curses.color_pair(2) | curses.A_BOLD)

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
                name = m.get("name", "")[:30]
                correct = m.get("lab_correct", 0)
                tot = m.get("lab_total", 0)
                pct = m.get("lab_correct_pct", 0)
                order = m.get("sort_order", m_idx + 1)
                is_open = m.get("is_open", True)
                is_comp = m.get("lab_completed", False)

                if not is_open:
                    status_badge = "[LOCKED]"
                    color_p = 5
                elif is_comp:
                    status_badge = "[✓ DONE]"
                    color_p = 3
                elif tot > 0:
                    status_badge = f"{correct:>2}/{tot:<2} ({pct:>2}%)"
                    color_p = 4
                else:
                    status_badge = "[THEORY]"
                    color_p = 7

                line_str = f" #{order:<2} {name:<30} {status_badge:>14}"
                if m_idx == sel_m:
                    safe_addstr(popup, 2 + row, 2, line_str[:pw - 4], curses.color_pair(2) | curses.A_REVERSE | curses.A_BOLD)
                else:
                    safe_addstr(popup, 2 + row, 2, line_str[:pw - 4], curses.color_pair(color_p))

            safe_addstr(popup, ph - 2, 2, "[↑/↓/j/k] Select │ [Enter] Open Module │ [P] Change Track │ [Esc] Cancel", curses.color_pair(7))
            popup.refresh()

            key = popup.getch()
            if key in (curses.KEY_UP, ord('k')):
                sel_m = max(0, sel_m - 1)
            elif key in (curses.KEY_DOWN, ord('j')):
                sel_m = min(len(modules) - 1, sel_m + 1)
            elif key in (10, 13, curses.KEY_ENTER):
                target_mod = modules[sel_m]
                self.module_id = target_mod.get("id")
                self.cfg["current_module_id"] = self.module_id
                save_config(self.cfg)
                self.fetch_data()
                if not target_mod.get("is_open", True):
                    self.status_msg = f"[!] '{target_mod.get('name')}' is currently locked by lecturer."
                    self.status_color = 5
                else:
                    self.status_msg = f"Loaded module: {target_mod.get('name')}"
                    self.status_color = 3
                break
            elif key in (ord('P'),):
                self.show_programs_popup(max_y, max_x)
                data = self.client.get_modules(self.program_id)
                modules = data.get("modules", [])
                sel_m = 0
                mod_scroll = 0
            elif key in (27, ord('q'), ord('Q'), ord('m'), ord('M')):
                break

    def show_media_popup(self, max_y, max_x, media_type):
        """Show and open Course Book or Video Lecture link with clean metadata."""
        if not self.client:
            return
        data = self.client.get_modules(self.program_id)
        modules = data.get("modules", [])
        curr_m = None
        for m in modules:
            if m.get("id") == self.module_id:
                curr_m = m
                break
        if not curr_m:
            return

        name = curr_m.get("name", f"Module #{self.module_id}")
        pw = min(74, max_x - 4)
        ph = 11
        px = (max_x - pw) // 2
        py = (max_y - ph) // 2

        popup = curses.newwin(ph, pw, py, px)
        popup.keypad(True)
        popup.box()

        if media_type == "book":
            binfo = self.client.get_book_info(self.module_id, name)
            url = binfo.get("url") if binfo else None
            fname = binfo.get("filename", "Course-Book.pdf") if binfo else "N/A"

            safe_addstr(popup, 0, 2, " COURSE BOOK (PDF) ", curses.color_pair(2) | curses.A_BOLD)
            safe_addstr(popup, 2, 3, f"Module:   {name[:pw-14]}", curses.color_pair(1) | curses.A_BOLD)
            if url:
                safe_addstr(popup, 3, 3, f"Document: {fname[:pw-14]}", curses.color_pair(4) | curses.A_BOLD)
                safe_addstr(popup, 4, 3, "Storage:  Cloudflare R2 High-Speed Secure CDN", curses.color_pair(3))
                safe_addstr(popup, 6, 3, "[o] Open in Reader  │  [d] Download to Disk", curses.color_pair(2) | curses.A_BOLD)
                safe_addstr(popup, 7, 3, "[c] Copy Direct Link  │  [Esc] Close", curses.color_pair(7))
            else:
                safe_addstr(popup, 4, 3, "No PDF book available for this module.", curses.color_pair(5))
                safe_addstr(popup, 6, 3, "Press [Esc] to close", curses.color_pair(7))
        else:
            url = curr_m.get("video_url")
            safe_addstr(popup, 0, 2, " HD VIDEO LECTURE ", curses.color_pair(2) | curses.A_BOLD)
            safe_addstr(popup, 2, 3, f"Module:   {name[:pw-14]}", curses.color_pair(1) | curses.A_BOLD)
            if url:
                safe_addstr(popup, 3, 3, "Stream:   Cyberium Academy HD Video Stream", curses.color_pair(3))
                safe_addstr(popup, 5, 3, "[o] Watch in Browser  │  [c] Copy Stream Link", curses.color_pair(2) | curses.A_BOLD)
                safe_addstr(popup, 6, 3, "[Esc] Close", curses.color_pair(7))
            else:
                safe_addstr(popup, 4, 3, "No video lecture available for this module.", curses.color_pair(5))
                safe_addstr(popup, 6, 3, "Press [Esc] to close", curses.color_pair(7))

        popup.refresh()
        while True:
            k = popup.getch()
            if k in (ord('o'), ord('O')) and url:
                try:
                    subprocess.Popen(["xdg-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    self.status_msg = f"[✓] Launched {media_type} in browser/reader."
                    self.status_color = 3
                except Exception as e:
                    self.status_msg = f"[!] Failed to launch browser: {e}"
                    self.status_color = 5
                break
            elif k in (ord('d'), ord('D')) and media_type == "book" and url:
                try:
                    downloads_dir = os.path.expanduser("~/Downloads")
                    if not os.path.exists(downloads_dir):
                        downloads_dir = BOOKS_DIR
                    dest_file = os.path.join(downloads_dir, fname)
                    download_file(url, dest_file)
                    self.status_msg = f"[✓] Saved book to {dest_file}"
                    self.status_color = 3
                except Exception as e:
                    self.status_msg = f"[!] Download error: {e}"
                    self.status_color = 5
                break
            elif k in (ord('c'), ord('C')) and url:
                if self.copy_to_clipboard(url):
                    self.status_msg = f"[✓] Copied full {media_type} URL to clipboard."
                    self.status_color = 3
                else:
                    self.status_msg = f"[!] Could not access system clipboard."
                    self.status_color = 5
                break
            elif k in (27, 10, 13, ord('q'), ord('Q'), curses.KEY_ENTER):
                break

    def show_links_popup(self, max_y, max_x):
        """Interactive Modal to view, open in browser, download, or copy question attachment URLs."""
        if not self.filtered_questions or self.selected_idx >= len(self.filtered_questions):
            return
        q = self.filtered_questions[self.selected_idx]
        q_idx = q.get("index", self.selected_idx)
        raw_text = q.get("text", "")
        urls = extract_urls(raw_text)

        if not urls:
            self.status_msg = f"No attached resources for Question #{q_idx}."
            self.status_color = 4
            return

        pw = min(76, max_x - 4)
        ph = min(15, max_y - 4)
        px = (max_x - pw) // 2
        py = (max_y - ph) // 2

        sel_link = 0
        link_scroll = 0

        while True:
            popup = curses.newwin(ph, pw, py, px)
            popup.keypad(True)
            popup.box()
            safe_addstr(popup, 0, 2, f" QUESTION #{q_idx} │ LAB RESOURCES ({len(urls)}) ", curses.color_pair(2) | curses.A_BOLD)

            visible_count = ph - 5
            if sel_link < link_scroll:
                link_scroll = sel_link
            elif sel_link >= link_scroll + visible_count:
                link_scroll = sel_link - visible_count + 1

            for row in range(visible_count):
                l_idx = link_scroll + row
                if l_idx >= len(urls):
                    break
                u = urls[l_idx]
                fname = u.split("/")[-1] if "/" in u else u
                mark = "●" if l_idx == sel_link else "○"
                line_str = f" {mark} {fname:<32} │ {u[:30]}"
                if l_idx == sel_link:
                    safe_addstr(popup, 2 + row, 2, line_str[:pw - 4], curses.color_pair(2) | curses.A_REVERSE | curses.A_BOLD)
                else:
                    safe_addstr(popup, 2 + row, 2, line_str[:pw - 4], curses.color_pair(1))

            curr_u = urls[sel_link]
            safe_addstr(popup, ph - 3, 2, "[o] Open / Launch  │  [d] Download  │  [c] Copy URL", curses.color_pair(4) | curses.A_BOLD)
            safe_addstr(popup, ph - 2, 2, "[↑/↓/j/k] Select  │  [Esc] Close", curses.color_pair(7))
            popup.refresh()

            k = popup.getch()
            if k in (curses.KEY_UP, ord('k')):
                sel_link = max(0, sel_link - 1)
            elif k in (curses.KEY_DOWN, ord('j')):
                sel_link = min(len(urls) - 1, sel_link + 1)
            elif k in (ord('o'), ord('O'), 10, 13, curses.KEY_ENTER):
                try:
                    subprocess.Popen(["xdg-open", curr_u], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    self.status_msg = f"[✓] Launched {curr_u.split('/')[-1]} in default app."
                    self.status_color = 3
                except Exception as e:
                    self.status_msg = f"[!] Failed to launch browser: {e}"
                    self.status_color = 5
                break
            elif k in (ord('d'), ord('D')):
                fname = curr_u.split("/")[-1] if "/" in curr_u else "attachment.bin"
                downloads_dir = os.path.expanduser("~/Downloads")
                if not os.path.exists(downloads_dir):
                    downloads_dir = BOOKS_DIR
                dest_file = os.path.join(downloads_dir, fname)
                try:
                    download_file(curr_u, dest_file)
                    self.status_msg = f"[✓] Saved resource to {dest_file}"
                    self.status_color = 3
                except Exception as e:
                    self.status_msg = f"[!] Download error: {e}"
                    self.status_color = 5
                break
            elif k in (ord('c'), ord('C')):
                if self.copy_to_clipboard(curr_u):
                    self.status_msg = f"[✓] Copied resource URL to clipboard."
                    self.status_color = 3
                else:
                    self.status_msg = f"[!] Could not access system clipboard."
                    self.status_color = 5
                break
            elif k in (27, ord('q'), ord('Q'), ord('l'), ord('L')):
                break

    def show_logout_popup(self, max_y, max_x):
        """Interactive Logout Confirmation Modal."""
        pw = min(66, max_x - 4)
        ph = 9
        px = (max_x - pw) // 2
        py = (max_y - ph) // 2

        popup = curses.newwin(ph, pw, py, px)
        popup.keypad(True)
        popup.box()

        safe_addstr(popup, 0, 2, " CYBERIUM ACADEMY │ LOGOUT CONFIRMATION ", curses.color_pair(5) | curses.A_BOLD)
        safe_addstr(popup, 2, 3, "Are you sure you want to log out of Cyberium Academy?", curses.color_pair(1) | curses.A_BOLD)
        safe_addstr(popup, 3, 3, "This will clear your local stored session cookies.", curses.color_pair(7))
        safe_addstr(popup, 5, 3, "[y] Confirm Logout  │  [n / Esc] Cancel", curses.color_pair(4) | curses.A_BOLD)
        popup.refresh()

        while True:
            k = popup.getch()
            if k in (ord('y'), ord('Y'), 10, 13, curses.KEY_ENTER):
                if self.client:
                    try:
                        self.client.logout()
                    except Exception:
                        pass
                clear_session(self.cfg)
                return True
            elif k in (27, ord('n'), ord('N'), ord('q'), ord('Q')):
                return False

    def handle_submit(self):
        answer = self.input_text.strip()
        if not answer:
            self.input_mode = False
            return

        if not self.filtered_questions or self.selected_idx >= len(self.filtered_questions):
            return

        q = self.filtered_questions[self.selected_idx]
        q_idx = q.get("index", self.selected_idx)

        self.status_msg = f"Submitting answer to #{q_idx} ({self.q_type.upper()})..."
        self.status_color = 4
        self.render()

        resp = self.client.submit_answer(self.module_id, q_idx, answer, q_type=self.q_type)

        if resp.get("correct"):
            self.status_msg = f"[✓] CORRECT! +Points awarded for #{q_idx}."
            self.status_color = 3
            self.fetch_profile_stats()
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

            if key == curses.KEY_MOUSE:
                try:
                    _, mx, my, _, bstate = curses.getmouse()
                    max_y, max_x = self.stdscr.getmaxyx()
                    split_x = max(34, int(max_x * 0.40))

                    if bstate & (curses.BUTTON1_CLICKED | curses.BUTTON1_PRESSED):
                        if 2 <= my < max_y - 2 and mx < split_x:
                            clicked_idx = self.list_scroll + (my - 2)
                            if clicked_idx < len(self.filtered_questions):
                                self.selected_idx = clicked_idx
                                self.detail_scroll = 0
                    elif bstate & curses.BUTTON4_PRESSED or key == 65536:
                        self.selected_idx = max(0, self.selected_idx - 1)
                    elif bstate & curses.BUTTON5_PRESSED or key == 65537:
                        self.selected_idx = min(len(self.filtered_questions) - 1, self.selected_idx + 1)
                except Exception:
                    pass
                continue

            if self.input_mode:
                if key in (10, 13, curses.KEY_ENTER):
                    self.handle_submit()
                elif key == 27:  # ESC
                    self.input_mode = False
                    self.input_text = ""
                    self.cursor_pos = 0
                elif key in (curses.KEY_BACKSPACE, 127, 8):
                    if self.cursor_pos > 0:
                        self.input_text = self.input_text[:self.cursor_pos - 1] + self.input_text[self.cursor_pos:]
                        self.cursor_pos -= 1
                elif key == curses.KEY_DC:
                    if self.cursor_pos < len(self.input_text):
                        self.input_text = self.input_text[:self.cursor_pos] + self.input_text[self.cursor_pos + 1:]
                elif key == curses.KEY_LEFT:
                    self.cursor_pos = max(0, self.cursor_pos - 1)
                elif key == curses.KEY_RIGHT:
                    self.cursor_pos = min(len(self.input_text), self.cursor_pos + 1)
                elif key in (curses.KEY_HOME, 1):
                    self.cursor_pos = 0
                elif key in (curses.KEY_END, 5):
                    self.cursor_pos = len(self.input_text)
                elif key == 21:  # Ctrl+U
                    self.input_text = ""
                    self.cursor_pos = 0
                elif 32 <= key <= 126:
                    self.input_text = self.input_text[:self.cursor_pos] + chr(key) + self.input_text[self.cursor_pos:]
                    self.cursor_pos += 1
            elif self.search_mode:
                if key in (10, 13, curses.KEY_ENTER, 27):  # Enter or ESC completes search
                    self.search_mode = False
                    self.cursor_pos = 0
                elif key in (curses.KEY_BACKSPACE, 127, 8):
                    if self.cursor_pos > 0:
                        self.search_text = self.search_text[:self.cursor_pos - 1] + self.search_text[self.cursor_pos:]
                        self.cursor_pos -= 1
                        self.apply_filter()
                elif key == 21:  # Ctrl+U
                    self.search_text = ""
                    self.cursor_pos = 0
                    self.apply_filter()
                elif 32 <= key <= 126:
                    self.search_text = self.search_text[:self.cursor_pos] + chr(key) + self.search_text[self.cursor_pos:]
                    self.cursor_pos += 1
                    self.apply_filter()
            else:
                if key in (ord('q'), ord('Q')):
                    break
                elif key in (curses.KEY_UP, ord('k')):
                    if self.filtered_questions:
                        self.selected_idx = max(0, self.selected_idx - 1)
                        self.detail_scroll = 0
                elif key in (curses.KEY_DOWN, ord('j')):
                    if self.filtered_questions:
                        self.selected_idx = min(len(self.filtered_questions) - 1, self.selected_idx + 1)
                        self.detail_scroll = 0
                elif key in (curses.KEY_PPAGE, ord('u')):
                    self.detail_scroll = max(0, self.detail_scroll - 4)
                elif key in (curses.KEY_NPAGE, ord('d')):
                    self.detail_scroll += 4
                elif key == 9:  # Tab
                    self.detail_scroll += 4
                elif key in (ord('/'), ord('s')):
                    self.search_mode = True
                    self.search_text = ""
                    self.cursor_pos = 0
                elif key in (ord('i'), ord('I'), 10, 13, curses.KEY_ENTER):
                    if self.filtered_questions and self.module_open:
                        self.input_mode = True
                        self.input_text = ""
                        self.cursor_pos = 0
                elif key in (ord('n'), ord('N')):
                    max_y, max_x = self.stdscr.getmaxyx()
                    self.show_note_popup(max_y, max_x)
                elif key in (ord('t'), ord('T')):
                    max_y, max_x = self.stdscr.getmaxyx()
                    self.show_themes_popup(max_y, max_x)
                elif key in (ord('c'), ord('C')):
                    if self.filtered_questions and self.selected_idx < len(self.filtered_questions):
                        q_text = self.filtered_questions[self.selected_idx].get("text", "")
                        if self.copy_to_clipboard(q_text):
                            self.status_msg = "Copied question text to clipboard."
                            self.status_color = 3
                        else:
                            self.status_msg = "Question text ready."
                            self.status_color = 2
                elif key in (ord('b'), ord('B')):
                    max_y, max_x = self.stdscr.getmaxyx()
                    self.show_media_popup(max_y, max_x, "book")
                elif key in (ord('v'), ord('V')):
                    max_y, max_x = self.stdscr.getmaxyx()
                    self.show_media_popup(max_y, max_x, "video")
                elif key in (ord('x'), ord('X')):
                    self.q_type = "extra" if self.q_type == "lab" else "lab"
                    self.status_msg = f"Mode: {'BONUS / EXTRA' if self.q_type == 'extra' else 'CORE LABS'}."
                    self.status_color = 4
                    self.fetch_data()
                elif key in (ord('l'),):
                    max_y, max_x = self.stdscr.getmaxyx()
                    self.show_links_popup(max_y, max_x)
                elif key in (ord('L'),):
                    max_y, max_x = self.stdscr.getmaxyx()
                    logged_out = self.show_logout_popup(max_y, max_x)
                    if logged_out:
                        self.status_msg = "[✓] Logged out of Cyberium Academy."
                        break
                elif key in (ord('m'), ord('M')):
                    max_y, max_x = self.stdscr.getmaxyx()
                    self.show_modules_popup(max_y, max_x)
                elif key in (ord('P'),):
                    max_y, max_x = self.stdscr.getmaxyx()
                    self.show_programs_popup(max_y, max_x)
                elif key in (ord('p'),):
                    max_y, max_x = self.stdscr.getmaxyx()
                    self.show_profile_popup(max_y, max_x)
                elif key in (ord('r'), ord('R')):
                    self.status_msg = "Refreshing platform data..."
                    self.status_color = 2
                    self.render()
                    self.fetch_profile_stats()
                    self.fetch_data()
                    self.status_msg = "Platform data refreshed."
                    self.status_color = 3


def start_tui():
    curses.wrapper(lambda stdscr: CyberiumTUI(stdscr).run())


if __name__ == "__main__":
    start_tui()
