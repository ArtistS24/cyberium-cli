"""
Cyberium CLI Command Implementations
Strict Terminal Formatting & Interactive Switching
Equal capabilities with TUI: Multi-Program tracks, Extra Labs, Notes, Search, Themes.
"""

import sys
import argparse
from .config import load_config, save_config, interactive_login, get_note, save_note
from .api import CyberiumClient
from .ui import (
    RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, DIM, BOLD, RESET,
    ICON_CHECK, ICON_CROSS, ICON_PENDING, ICON_ARROW, ICON_POINTER, ICON_USER, ICON_FOLDER, ICON_POINT, ICON_THEME,
    header, divider, badge_success, badge_pending, badge_failed, badge_empty, progress_bar,
    calculate_rank, THEMES, ASCII_BANNER
)


def ensure_client(cfg):
    """Ensures a valid authenticated CyberiumClient exists, prompting login if needed."""
    cookies = cfg.get("cookies", {})
    if not cookies or not cookies.get("connect.sid"):
        print(f"\n{YELLOW}{BOLD}[{ICON_CROSS}] No Cyberium student session detected.{RESET}")
        print(f"{WHITE}Each student needs their own session cookies to submit answers.{RESET}\n")
        choice = input(f"{CYAN}Would you like to log in now? [Y/n]: {RESET}").strip().lower()
        if choice in ("", "y", "yes"):
            success = interactive_login(cfg)
            if not success:
                sys.exit(1)
        else:
            sys.exit(1)
    return CyberiumClient(cfg)


def cmd_current(client, cfg):
    mod_id = cfg.get("current_module_id", 88)
    data = client.get_questions(mod_id)
    if "error" in data:
        print(f"{RED}[{ICON_CROSS}] Error: {data['error']}{RESET}")
        return

    mod_name = data.get("module_name", f"Module #{mod_id}")
    total = data.get("total", 0)
    answered = data.get("answered_count", 0)
    first_unanswered = data.get("first_unanswered")
    questions = data.get("questions", [])

    print(header(mod_name, f"Progress: {answered}/{total}"))
    print(f"  {BOLD}Completion:{RESET} {progress_bar(answered, total, width=28)}\n")

    if not questions:
        print(f"  {YELLOW}[!] No lab questions in this module or module is locked.{RESET}\n")
        return

    if first_unanswered is not None and first_unanswered < len(questions):
        q = questions[first_unanswered]
        idx = q.get("index", first_unanswered)
        text = q.get("text", "")
        note = get_note(mod_id, idx)

        print(f"  {YELLOW}{BOLD}[{ICON_PENDING}] CURRENT ACTIVE OBJECTIVE (#{idx}):{RESET}")
        print(f"  {WHITE}{BOLD}{text}{RESET}\n")
        if note:
            print(f"  {CYAN}{BOLD}󰉋 Personal Note:{RESET} {CYAN}{note}{RESET}\n")
        print(f"{DIM}To submit your answer:{RESET} {CYAN}cyberium submit \"<your command or flag>\"{RESET}\n")
    else:
        print(f"  {GREEN}{BOLD}[{ICON_CHECK}] All {total} lab questions in this module are COMPLETED!{RESET}\n")


def cmd_list(client, cfg, q_type="lab"):
    mod_id = cfg.get("current_module_id", 88)
    data = client.get_questions(mod_id, q_type=q_type)
    if "error" in data:
        print(f"{RED}[{ICON_CROSS}] Error: {data['error']}{RESET}")
        return

    mod_name = data.get("module_name", f"Module #{mod_id}")
    questions = data.get("questions", [])
    total = data.get("total", 0)
    answered = data.get("answered_count", 0)
    first_unanswered = data.get("first_unanswered")
    type_label = "EXTRA CHALLENGES" if q_type == "extra" else "LAB OBJECTIVES"

    print(header(f"{mod_name} │ {type_label}", f"{answered}/{total} Solved"))

    if not questions:
        print(f"  {DIM}[!] No {q_type} questions found for this module.{RESET}\n")
        return

    for idx, q in enumerate(questions):
        q_idx = q.get("index", idx)
        text = q.get("text", "").replace("\n", " ")
        is_answered = q.get("answered", False)
        is_active = (idx == first_unanswered)
        note = get_note(mod_id, q_idx)
        note_badge = f" {CYAN}󰉋{RESET}" if note else ""

        if is_answered:
            badge = f"{GREEN}[{ICON_CHECK}]{RESET}"
            line = f" {badge} {DIM}#{q_idx:<2}{note_badge} {text}{RESET}"
        elif is_active:
            badge = f"{YELLOW}{BOLD}[{ICON_PENDING}]{RESET}"
            line = f" {badge} {YELLOW}{BOLD}#{q_idx:<2}{note_badge} {text}{RESET}"
        else:
            badge = f"{DIM}[ ]{RESET}"
            line = f" {badge} {WHITE}#{q_idx:<2}{note_badge} {text}{RESET}"

        print(line)

    print(divider() + "\n")


def cmd_submit(client, cfg, answer_str, q_index=None, q_type="lab"):
    mod_id = cfg.get("current_module_id", 88)

    if q_index is None:
        data = client.get_questions(mod_id, q_type=q_type)
        if "error" in data:
            print(f"{RED}[{ICON_CROSS}] Error: {data['error']}{RESET}")
            return
        q_index = data.get("first_unanswered")
        if q_index is None:
            print(f"{GREEN}[{ICON_CHECK}] All questions in this module are already solved!{RESET}")
            return

    print(f"\n{CYAN}Submitting answer to Question #{q_index} ({q_type.upper()})...{RESET}")
    resp = client.submit_answer(mod_id, q_index, answer_str, q_type=q_type)

    if resp.get("correct"):
        print(f"{GREEN}{BOLD}[{ICON_CHECK}] CORRECT! Objective #{q_index} solved successfully!{RESET}")
        next_data = client.get_questions(mod_id, q_type=q_type)
        next_idx = next_data.get("first_unanswered")
        if next_idx is not None and next_idx < len(next_data.get("questions", [])):
            nxt_q = next_data["questions"][next_idx]
            print(f"\n{YELLOW}{BOLD}[{ICON_PENDING}] NEXT OBJECTIVE (#{nxt_q.get('index')}):{RESET}")
            print(f"  {WHITE}{BOLD}{nxt_q.get('text')}{RESET}\n")
    elif resp.get("already_answered"):
        print(f"{YELLOW}[!] This question was already answered.{RESET}\n")
    else:
        err_msg = resp.get("message") or resp.get("error") or "Incorrect answer. Try again."
        print(f"{RED}{BOLD}[{ICON_CROSS}] {err_msg}{RESET}\n")


def cmd_modules(client, cfg):
    prog_id = cfg.get("current_program_id", 10)
    data = client.get_modules(prog_id)
    if "error" in data:
        print(f"{RED}[{ICON_CROSS}] Error: {data['error']}{RESET}")
        return

    modules = data.get("modules", [])
    curr_mod = cfg.get("current_module_id")

    print(header("TRAINING MODULES", f"Program #{prog_id}"))

    for m in modules:
        mid = m.get("id")
        order = m.get("sort_order", "")
        name = m.get("name", "")
        correct = m.get("lab_correct", 0)
        total = m.get("lab_total", 0)
        pct = m.get("lab_correct_pct", 0)
        is_open = m.get("is_open", True)
        is_comp = m.get("lab_completed", False)
        active_mark = f"{CYAN}{BOLD}❯{RESET}" if mid == curr_mod else " "

        if not is_open:
            badge = f"{RED}[LOCKED]{RESET}"
        elif is_comp:
            badge = f"{GREEN}[✓ DONE]{RESET}"
        elif total > 0:
            badge = f"{YELLOW}[ {correct}/{total} ({pct}%)]" + RESET
        else:
            badge = f"{DIM}[THEORY]{RESET}"

        print(f" {active_mark} {BOLD}#{order:<2}{RESET} {WHITE}{name:<28}{RESET} {badge:<22} {DIM}(ID: {mid}){RESET}")

    print(divider())
    print(f"{DIM}To switch module:{RESET} {CYAN}cyberium set-module <ID>{RESET}\n")


def cmd_set_module(client, cfg, mod_identifier=None):
    prog_id = cfg.get("current_program_id", 10)
    data = client.get_modules(prog_id)
    modules = data.get("modules", [])

    if mod_identifier is None:
        print(header("SELECT MODULE TO ACTIVATE", f"Program #{prog_id}"))
        for idx, m in enumerate(modules):
            mid = m.get("id")
            name = m.get("name", "")
            order = m.get("sort_order", idx + 1)
            is_open = m.get("is_open", True)
            is_comp = m.get("lab_completed", False)
            status = f"{GREEN}[DONE]{RESET}" if is_comp else (f"{CYAN}[OPEN]{RESET}" if is_open else f"{RED}[LOCKED]{RESET}")
            print(f"  {BOLD}[{order}]{RESET} {WHITE}{name:<28}{RESET} {status} {DIM}(ID: {mid}){RESET}")
        print(divider())
        try:
            choice = input(f"{YELLOW}Enter module number or ID to switch: {RESET}").strip()
            if not choice:
                return
            mod_identifier = choice
        except (KeyboardInterrupt, EOFError):
            print()
            return

    target_mod = None
    for m in modules:
        if str(m.get("id")) == str(mod_identifier) or str(m.get("sort_order")) == str(mod_identifier):
            target_mod = m
            break

    if not target_mod:
        try:
            mid = int(mod_identifier)
            cfg["current_module_id"] = mid
            save_config(cfg)
            print(f"{GREEN}[{ICON_CHECK}] Active module set to ID {mid}.{RESET}\n")
            return
        except ValueError:
            print(f"{RED}[!] Module '{mod_identifier}' not found in active program.{RESET}\n")
            return

    mid = target_mod.get("id")
    name = target_mod.get("name", "")
    cfg["current_module_id"] = mid
    save_config(cfg)
    print(f"{GREEN}[{ICON_CHECK}] Switched to Module {BOLD}#{target_mod.get('sort_order')} {name}{RESET} (ID: {mid})\n")


def cmd_programs(client, cfg):
    data = client.get_programs()
    if "error" in data:
        print(f"{RED}[{ICON_CROSS}] Error: {data['error']}{RESET}")
        return

    programs = data if isinstance(data, list) else data.get("programs", [])
    curr_prog = cfg.get("current_program_id", 10)

    print(header("ENROLLED SPECIALIZATION TRACKS (14 Tracks Available)"))

    for p in programs:
        pid = p.get("id")
        code = p.get("code", "")
        name = p.get("name", "")
        lvl = p.get("level", 1)
        tot = p.get("total_modules", "0")
        comp = p.get("completed_modules", "0")
        pct = p.get("completion_pct", 0)
        active_mark = f"{CYAN}{BOLD}❯{RESET}" if pid == curr_prog else " "

        p_bar = progress_bar(int(comp), int(tot) if int(tot) > 0 else 1, width=12)
        print(f" {active_mark} {BOLD}{code:<6}{RESET} {WHITE}{name:<28}{RESET} {p_bar} {DIM}(Lvl {lvl}) [ID: {pid}]{RESET}")

    print(divider())
    print(f"{DIM}To switch track:{RESET} {CYAN}cyberium switch <CODE or ID>{RESET}  {DIM}(e.g. cyberium switch ZX301 or cyberium switch 7){RESET}\n")


def cmd_set_program(client, cfg, prog_identifier=None):
    data = client.get_programs()
    programs = data if isinstance(data, list) else data.get("programs", [])

    if prog_identifier is None:
        curr_prog = cfg.get("current_program_id", 10)
        print(header("SELECT TRAINING TRACK TO ACTIVATE"))
        for idx, p in enumerate(programs, start=1):
            pid = p.get("id")
            code = p.get("code", "")
            name = p.get("name", "")
            lvl = p.get("level", 1)
            mark = f"{CYAN}●{RESET}" if pid == curr_prog else " "
            print(f" {mark} {BOLD}[{idx:>2}]{RESET} {CYAN}{code:<6}{RESET} {WHITE}{name:<26}{RESET} {DIM}(Lvl {lvl}) [ID: {pid}]{RESET}")
        print(divider())
        try:
            choice = input(f"{YELLOW}Enter track number [1-{len(programs)}] or Code (e.g. ZX310): {RESET}").strip()
            if not choice:
                return
            if choice.isdigit() and 1 <= int(choice) <= len(programs):
                prog_identifier = programs[int(choice) - 1].get("id")
            else:
                prog_identifier = choice
        except (KeyboardInterrupt, EOFError):
            print()
            return

    target_prog = None
    for p in programs:
        if str(p.get("id")) == str(prog_identifier) or p.get("code", "").lower() == str(prog_identifier).lower():
            target_prog = p
            break

    if not target_prog:
        print(f"{RED}[!] Program '{prog_identifier}' not found in your enrolled tracks.{RESET}")
        print(f"{DIM}Run {CYAN}cyberium programs{DIM} to view all 14 available tracks.{RESET}\n")
        return

    pid = target_prog.get("id")
    code = target_prog.get("code", "")
    name = target_prog.get("name", "")

    cfg["current_program_id"] = pid

    # Automatically pick first open and uncompleted module of this track
    mods_data = client.get_modules(pid)
    mods = mods_data.get("modules", [])
    chosen_mod = None
    for m in mods:
        if m.get("is_open") and not m.get("lab_completed"):
            chosen_mod = m
            break
    if not chosen_mod and mods:
        chosen_mod = mods[0]

    if chosen_mod:
        cfg["current_module_id"] = chosen_mod.get("id")
        save_config(cfg)
        print(f"\n{GREEN}[{ICON_CHECK}] Switched to Program {BOLD}{code} {name}{RESET} (ID: {pid})")
        print(f"  {CYAN}Active Module:{RESET} {chosen_mod.get('name')} (ID: {chosen_mod.get('id')})\n")
    else:
        save_config(cfg)
        print(f"\n{GREEN}[{ICON_CHECK}] Switched to Program {BOLD}{code} {name}{RESET} (ID: {pid})\n")


def cmd_profile(client):
    data = client.get_profile()
    if "error" in data:
        print(f"{RED}[{ICON_CROSS}] Error: {data['error']}{RESET}")
        return

    ident = data.get("identity", {})
    name = f"{ident.get('firstName', '')} {ident.get('lastName', '')}"
    scode = ident.get("sCode", "s2")
    email = ident.get("email", "")
    division = ident.get("divisionName", "John Bryce")
    unit = ident.get("unitName", "RTX2026")
    points = ident.get("trainingPoints", 134)
    coins = ident.get("coinBalance", 63)
    rank_title, rank_color = calculate_rank(points)

    pbr = data.get("pbr", {})
    off_pbr = pbr.get("offense", 97)
    soc_pbr = pbr.get("soc", 98)
    def_pbr = pbr.get("defense", 96)

    trophies = data.get("trophies", {})
    gold_t = trophies.get("gold", 8)
    silv_t = trophies.get("silver", 2)
    brnz_t = trophies.get("bronze", 1)
    certs = len(data.get("certifications", []))

    print(header("OPERATOR DOSSIER", "Official Student Profile"))
    print(f"  {BOLD}Operator:{RESET}  {WHITE}{name} ({scode}){RESET}  {DIM}│{RESET}  {BOLD}Division:{RESET} {CYAN}{division}{RESET} {DIM}({unit}){RESET}")
    print(f"  {BOLD}Rank:{RESET}      {rank_color}{BOLD}{rank_title}{RESET}  {DIM}│{RESET}  {BOLD}Status:{RESET}   {GREEN}SPECTO ● LIVE{RESET}")
    print(f"  {BOLD}Points:{RESET}    {GREEN}{points} pts{RESET}  {DIM}│{RESET}  {BOLD}Coins:{RESET}    {YELLOW}{coins} coins{RESET}  {DIM}│{RESET}  {BOLD}Certs:{RESET} {certs} verified\n")
    print(f"  {BOLD}Performance Benchmark (PBR):{RESET}")
    print(f"    {CYAN}Offense:{RESET} {off_pbr}%  {DIM}│{RESET}  {BLUE}SOC Operations:{RESET} {soc_pbr}%  {DIM}│{RESET}  {GREEN}Defense:{RESET} {def_pbr}%\n")
    print(f"  {BOLD}Trophies & Specializations:{RESET}")
    print(f"    {YELLOW}★ {gold_t} Gold Trophies{RESET}  {WHITE}★ {silv_t} Silver{RESET}  {DIM}★ {brnz_t} Bronze{RESET}")
    print(f"{divider()}\n")


def cmd_stats(client, cfg):
    """Detailed Cyberium Academy Offensive Dashboard."""
    print(ASCII_BANNER)
    cmd_profile(client)
    cmd_programs(client, cfg)


def cmd_banner(client, cfg):
    print(ASCII_BANNER)
    cmd_profile(client)


def cmd_book(client, cfg):
    mod_id = cfg.get("current_module_id", 88)
    prog_id = cfg.get("current_program_id", 10)
    data = client.get_modules(prog_id)
    modules = data.get("modules", [])
    mod_name = f"Module #{mod_id}"
    for m in modules:
        if m.get("id") == mod_id:
            mod_name = m.get("name", mod_name)
            break

    resp = client.get_book(mod_id)
    url = resp.get("url")
    if url:
        print(header("OFFICIAL COURSE BOOK (PDF)", mod_name))
        print(f"  {BOLD}Module:{RESET}          {WHITE}{mod_name}{RESET}")
        print(f"  {BOLD}Direct PDF Link:{RESET} {CYAN}{url}{RESET}")
        print(f"\n{DIM}To open in browser/reader:{RESET} {YELLOW}xdg-open '{url}'{RESET}\n")
    else:
        print(f"{RED}[!] No PDF course book available for {mod_name}.{RESET}\n")


def cmd_video(client, cfg):
    mod_id = cfg.get("current_module_id", 88)
    prog_id = cfg.get("current_program_id", 10)
    data = client.get_modules(prog_id)
    modules = data.get("modules", [])
    for m in modules:
        if m.get("id") == mod_id:
            name = m.get("name", "")
            video_url = m.get("video_url")
            print(header("VIDEO LECTURE", name))
            if video_url:
                print(f"  {BOLD}Module:{RESET}    {WHITE}{name}{RESET}")
                print(f"  {BOLD}Watch URL:{RESET} {CYAN}{video_url}{RESET}")
                print(f"\n{DIM}To watch video lecture:{RESET} {CYAN}xdg-open '{video_url}'{RESET}\n")
            else:
                print(f"  {YELLOW}[!] No video lecture available for this module.{RESET}\n")
            return
    print(f"{RED}[!] Module #{mod_id} not found.{RESET}\n")


def cmd_extra(client, cfg):
    cmd_list(client, cfg, q_type="extra")


def cmd_note(cfg, args):
    mod_id = cfg.get("current_module_id", 88)
    q_idx = args.index
    note_text = " ".join(args.text) if args.text else None

    if note_text is not None:
        save_note(mod_id, q_idx, note_text)
        print(f"{GREEN}[✓] Note saved for Question #{q_idx}.{RESET}\n")
    else:
        existing = get_note(mod_id, q_idx)
        print(header("STUDENT SCRATCHPAD NOTE", f"Question #{q_idx}"))
        if existing:
            print(f"  {CYAN}{BOLD}󰉋 {existing}{RESET}\n")
        else:
            print(f"  {DIM}[No note attached to this question yet]{RESET}")
            print(f"  {DIM}To save note:{RESET} {YELLOW}cyberium note {q_idx} \"your note here\"{RESET}\n")


def cmd_search(client, cfg, term):
    mod_id = cfg.get("current_module_id", 88)
    data = client.get_questions(mod_id)
    if "error" in data:
        print(f"{RED}[{ICON_CROSS}] Error: {data['error']}{RESET}")
        return

    questions = data.get("questions", [])
    matches = [q for q in questions if term.lower() in q.get("text", "").lower()]

    print(header("SEARCH RESULTS", f"Keyword: '{term}' in {data.get('module_name')}"))
    if not matches:
        print(f"  {YELLOW}[!] No questions matched '{term}'.{RESET}\n")
        return

    for q in matches:
        idx = q.get("index")
        text = q.get("text", "").replace("\n", " ")
        is_ans = q.get("answered", False)
        badge = f"{GREEN}[{ICON_CHECK}]{RESET}" if is_ans else f"{DIM}[ ]{RESET}"
        print(f" {badge} {BOLD}#{idx:<2}{RESET} {WHITE}{text}{RESET}")

    print(divider() + f"\n{GREEN}Found {len(matches)} matching question(s).{RESET}\n")


def cmd_themes(cfg):
    current = cfg.get("theme", "cyberium")
    print(header("AVAILABLE TERMINAL THEMES"))
    for tid, info in THEMES.items():
        mark = f"{CYAN}{BOLD}❯{RESET}" if tid == current else " "
        print(f" {mark} {BOLD}{tid:<14}{RESET} {WHITE}{info['name']:<28}{RESET} {DIM}– {info['desc']}{RESET}")
    print(divider())
    print(f"{DIM}To switch theme:{RESET} {CYAN}cyberium set-theme <name>{RESET}\n")


def cmd_set_theme(cfg, theme_name):
    tname = theme_name.lower().strip()
    if tname not in THEMES:
        print(f"{RED}[!] Unknown theme '{theme_name}'. Available: {', '.join(THEMES.keys())}{RESET}")
        return
    cfg["theme"] = tname
    save_config(cfg)
    print(f"{GREEN}[{ICON_CHECK}] Theme set to {BOLD}{THEMES[tname]['name']}{RESET}!\n")


def main():
    parser = argparse.ArgumentParser(
        description="Cyberium Academy Official Terminal Client & Submission Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  cyberium                      # Show current active question
  cyberium list                 # List all questions and statuses
  cyberium submit "grep -rl"    # Submit answer to current question
  cyberium submit-extra 1 "ans" # Submit answer to bonus/extra challenge #1
  cyberium switch ZX301         # Switch to Penetration Testing track
  cyberium switch               # Interactive track selector
  cyberium set-module           # Interactive module selector
  cyberium modules              # List modules in active program
  cyberium programs             # List all 14 enrolled programs
  cyberium extra                # View bonus / extra challenges
  cyberium themes               # List 16 color palettes
  cyberium set-theme matrix     # Switch to matrix / classic theme
  cyberium stats                # Full operator rank, progress & stats
  cyberium note 14 "memo"       # Save personal note for question #14
  cyberium search "wget"        # Search questions by keyword
  cyberium book                 # View course PDF book link
  cyberium video                # View HD video lecture link
  cyberium profile              # View student dossier & points
  cyberium tui                  # Launch full-screen interactive TUI
  cyberium login                # Update session cookies
"""
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("status", aliases=["current", "show"], help="Show current question & progress (default)")
    subparsers.add_parser("list", help="List all questions in current module")
    
    # Modules
    subparsers.add_parser("modules", help="List all modules in current program")
    set_mod_parser = subparsers.add_parser("set-module", aliases=["module"], help="Set or choose active module")
    set_mod_parser.add_argument("id", nargs="?", default=None, help="Module ID or Order number (interactive if empty)")

    # Programs / Tracks
    subparsers.add_parser("programs", aliases=["tracks"], help="List all enrolled programs")
    set_prog_parser = subparsers.add_parser("set-program", aliases=["program", "switch", "track"], help="Switch active track/program (interactive if empty)")
    set_prog_parser.add_argument("id", nargs="?", default=None, help="Program ID or Code (e.g. 10 or ZX310)")

    # Profile & Stats
    subparsers.add_parser("profile", help="Show student profile & score")
    subparsers.add_parser("stats", help="Full student operator dashboard & rank")
    subparsers.add_parser("banner", help="Display Cyberium ASCII banner & stats")
    
    # Media & Addons
    subparsers.add_parser("book", help="Get official course PDF book link")
    subparsers.add_parser("video", help="Get HD video lecture streaming link")
    subparsers.add_parser("extra", help="List bonus/extra challenges")

    # Themes
    subparsers.add_parser("themes", help="List all available terminal themes")
    set_theme_parser = subparsers.add_parser("set-theme", aliases=["theme"], help="Set active terminal theme")
    set_theme_parser.add_argument("name", help="Theme name (cyberium, catppuccin, matrix, nord, dracula, classic, etc.)")

    # Search & Notes
    search_parser = subparsers.add_parser("search", help="Search questions by keyword")
    search_parser.add_argument("term", help="Search term/keyword")

    note_parser = subparsers.add_parser("note", help="Add or read question notes")
    note_parser.add_argument("index", type=int, help="Question index")
    note_parser.add_argument("text", nargs="*", help="Note text to save")

    # Core
    subparsers.add_parser("login", help="Interactive login / cookie setup")
    subparsers.add_parser("tui", help="Launch interactive full-screen TUI dashboard")

    # Submission
    submit_parser = subparsers.add_parser("submit", help="Submit answer to current question")
    submit_parser.add_argument("answer", nargs="+", help="The answer string to submit")
    submit_parser.add_argument("-x", "--extra", action="store_true", help="Submit to extra challenge instead of core lab")
    submit_parser.add_argument("-i", "--index", type=int, default=None, help="Question index to submit to")

    submit_extra_parser = subparsers.add_parser("submit-extra", help="Submit answer to extra/bonus challenge")
    submit_extra_parser.add_argument("index", type=int, help="Extra challenge index")
    submit_extra_parser.add_argument("answer", nargs="+", help="The answer string to submit")

    args = parser.parse_args()

    cfg = load_config()

    if args.command == "login":
        interactive_login(cfg)
        return

    if args.command == "tui":
        from .tui import start_tui
        start_tui()
        return

    if args.command == "themes":
        cmd_themes(cfg)
        return

    if args.command in ("set-theme", "theme"):
        cmd_set_theme(cfg, args.name)
        return

    client = ensure_client(cfg)

    if args.command in (None, "status", "current", "show"):
        cmd_current(client, cfg)
    elif args.command in ("list", "all", "questions"):
        cmd_list(client, cfg)
    elif args.command == "submit":
        answer_str = " ".join(args.answer)
        q_type = "extra" if args.extra else "lab"
        cmd_submit(client, cfg, answer_str, q_index=args.index, q_type=q_type)
    elif args.command == "submit-extra":
        answer_str = " ".join(args.answer)
        cmd_submit(client, cfg, answer_str, q_index=args.index, q_type="extra")
    elif args.command == "modules":
        cmd_modules(client, cfg)
    elif args.command in ("set-module", "module"):
        cmd_set_module(client, cfg, args.id)
    elif args.command in ("programs", "tracks"):
        cmd_programs(client, cfg)
    elif args.command in ("set-program", "program", "switch", "track"):
        cmd_set_program(client, cfg, args.id)
    elif args.command == "profile":
        cmd_profile(client)
    elif args.command == "stats":
        cmd_stats(client, cfg)
    elif args.command == "note":
        cmd_note(cfg, args)
    elif args.command == "search":
        cmd_search(client, cfg, args.term)
    elif args.command == "banner":
        cmd_banner(client, cfg)
    elif args.command == "book":
        cmd_book(client, cfg)
    elif args.command == "video":
        cmd_video(client, cfg)
    elif args.command == "extra":
        cmd_extra(client, cfg)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
