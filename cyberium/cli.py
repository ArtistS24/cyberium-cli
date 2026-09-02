"""
Cyberium CLI Command Implementations
Strict Nerd Font / Terminal Formatting
"""

import sys
import argparse
from .config import load_config, save_config, interactive_login
from .api import CyberiumClient
from .ui import (
    RED, GREEN, YELLOW, CYAN, WHITE, DIM, BOLD, RESET,
    ICON_CHECK, ICON_CROSS, ICON_PENDING, ICON_ARROW, ICON_POINTER, ICON_USER, ICON_FOLDER, ICON_POINT,
    header, divider, badge_success, badge_pending, badge_failed, badge_empty, progress_bar
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
            cfg = load_config()
        else:
            print(f"\n{DIM}You can set up your session anytime with:{RESET} {CYAN}cyberium login{RESET}")
            print(f"{DIM}Or by creating a {BOLD}.env{RESET}{DIM} file (see .env.example).{RESET}\n")
            sys.exit(0)

    return CyberiumClient(cfg)


def cmd_current(client, cfg):
    module_id = cfg.get("current_module_id", 88)
    q_data = client.get_questions(module_id)
    if "error" in q_data:
        print(f"{RED}[{ICON_CROSS}] Error: {q_data['error']}{RESET}")
        return

    mod_name = q_data.get("module_name", f"Module #{module_id}")
    total = q_data.get("total", 0)
    answered = q_data.get("answered_count", 0)
    first_unanswered = q_data.get("first_unanswered")
    questions = q_data.get("questions", [])

    progress_str = f"Lab: {answered}/{total} ({progress_bar(answered, total, width=12)})"
    print(header(mod_name, progress_str))

    if first_unanswered is None or first_unanswered >= len(questions):
        print(f"{GREEN}{BOLD}[{ICON_CHECK}] All {total} questions in this module are completed!{RESET}\n")
        return

    curr_q = questions[first_unanswered]
    q_text = curr_q.get("text", "")
    q_idx = curr_q.get("index", first_unanswered)

    print(f"{YELLOW}{BOLD}[{ICON_PENDING}] CURRENT OBJECTIVE (Index {q_idx}):{RESET}")
    print(f"  {WHITE}{BOLD}{q_text}{RESET}\n")
    print(f"{DIM}To submit your answer:{RESET}")
    print(f"  {CYAN}cyberium submit \"<your_answer>\"{RESET}\n")


def cmd_list(client, cfg):
    module_id = cfg.get("current_module_id", 88)
    q_data = client.get_questions(module_id)
    if "error" in q_data:
        print(f"{RED}[{ICON_CROSS}] Error: {q_data['error']}{RESET}")
        return

    mod_name = q_data.get("module_name", f"Module #{module_id}")
    total = q_data.get("total", 0)
    answered = q_data.get("answered_count", 0)
    first_unanswered = q_data.get("first_unanswered")
    questions = q_data.get("questions", [])

    print(header(mod_name, f"{answered}/{total} Solved"))

    for q in questions:
        idx = q.get("index", 0)
        is_ans = q.get("answered", False)
        text = q.get("text", "")
        if len(text) > 75:
            text = text[:72] + "..."

        if is_ans:
            print(f"  {badge_success(f'#{idx:<2}')} {DIM}{text}{RESET}")
        elif idx == first_unanswered:
            print(f"  {badge_pending(f'#{idx:<2}')} {WHITE}{text}{RESET}")
        else:
            print(f"  {badge_empty(f'#{idx:<2}')} {DIM}{text}{RESET}")

    print(f"{divider()}\n")


def cmd_submit(client, cfg, answer_str):
    module_id = cfg.get("current_module_id", 88)
    q_data = client.get_questions(module_id)
    if "error" in q_data:
        print(f"{RED}[{ICON_CROSS}] Error: {q_data['error']}{RESET}")
        return

    first_unanswered = q_data.get("first_unanswered")
    questions = q_data.get("questions", [])

    if first_unanswered is None or first_unanswered >= len(questions):
        print(f"{GREEN}[{ICON_CHECK}] All questions in this module are already completed!{RESET}")
        return

    curr_q = questions[first_unanswered]
    q_idx = curr_q.get("index", first_unanswered)
    q_text = curr_q.get("text", "")

    print(f"\n{DIM}[*] Question #{q_idx}:{RESET} {WHITE}{q_text}{RESET}")
    print(f"{DIM}[*] Submitting answer:{RESET} {CYAN}{BOLD}{answer_str}{RESET}")

    resp = client.submit_answer(module_id, q_idx, answer_str)

    if resp.get("correct"):
        print(f"{GREEN}{BOLD}[{ICON_CHECK}] CORRECT! Points awarded.{RESET}")
        next_data = client.get_questions(module_id)
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


def cmd_set_module(cfg, mod_id):
    cfg["current_module_id"] = int(mod_id)
    save_config(cfg)
    print(f"{GREEN}[{ICON_CHECK}] Active module set to ID {mod_id}.{RESET}")


def cmd_programs(client, cfg):
    programs = client.get_programs()
    if isinstance(programs, dict) and "error" in programs:
        print(f"{RED}[{ICON_CROSS}] Error: {programs['error']}{RESET}")
        return

    curr_prog = cfg.get("current_program_id")
    print(header("ENROLLED PROGRAMS"))

    for p in programs:
        pid = p.get("id")
        code = p.get("code", "")
        name = p.get("name", "")
        done_mods = p.get("completed_modules", 0)
        tot_mods = p.get("total_modules", 0)
        active_mark = f"{YELLOW}{ICON_POINTER}{RESET}" if pid == curr_prog else " "

        print(f" {active_mark} {BOLD}{code:<8}{RESET} {WHITE}{name:<28}{RESET} {DIM}ID: {pid:<2}│ Modules: {done_mods}/{tot_mods}{RESET}")

    print(divider())
    print(f"{DIM}To switch program:{RESET} {CYAN}cyberium set-program <ID>{RESET}\n")


def cmd_set_program(cfg, prog_id):
    cfg["current_program_id"] = int(prog_id)
    save_config(cfg)
    print(f"{GREEN}[{ICON_CHECK}] Active program set to ID {prog_id}.{RESET}")


def cmd_profile(client):
    data = client.get_profile()
    if "error" in data:
        print(f"{RED}[{ICON_CROSS}] Error: {data['error']}{RESET}")
        return

    ident = data.get("identity", {})
    name = f"{ident.get('firstName', '')} {ident.get('lastName', '')}"
    email = ident.get("email", "")
    division = ident.get("divisionName", "")
    unit = ident.get("unitName", "")
    points = ident.get("trainingPoints", 0)
    coins = ident.get("coinBalance", 0)

    print(header("STUDENT PROFILE"))
    print(f"  {BOLD}Name:{RESET}     {WHITE}{name}{RESET}")
    print(f"  {BOLD}Email:{RESET}    {DIM}{email}{RESET}")
    print(f"  {BOLD}Division:{RESET} {CYAN}{division}{RESET} {DIM}({unit}){RESET}")
    print(f"  {BOLD}Points:{RESET}   {GREEN}{points} pts{RESET}")
    print(f"  {BOLD}Coins:{RESET}    {YELLOW}{coins} coins{RESET}")
    print(f"{divider()}\n")


def cmd_banner(client, cfg):
    from .ui import ASCII_BANNER
    print(ASCII_BANNER)
    cmd_profile(client)


def cmd_book(client, cfg):
    mod_id = cfg.get("current_module_id", 88)
    prog_id = cfg.get("current_program_id", 10)
    data = client.get_modules(prog_id)
    modules = data.get("modules", [])
    for m in modules:
        if m.get("id") == mod_id:
            name = m.get("name", "")
            book_url = m.get("book_url")
            print(header("COURSE BOOK", name))
            if book_url:
                full_url = f"https://cyberium.academy/{book_url}"
                print(f"  {BOLD}Module:{RESET}     {WHITE}{name}{RESET}")
                print(f"  {BOLD}PDF Path:{RESET}   {CYAN}{book_url}{RESET}")
                print(f"  {BOLD}Direct URL:{RESET} {YELLOW}{full_url}{RESET}")
                print(f"\n{DIM}To open in browser/reader:{RESET} {CYAN}xdg-open '{full_url}'{RESET}\n")
            else:
                print(f"  {YELLOW}[!] No PDF book available for this module.{RESET}\n")
            return
    print(f"{RED}[!] Module #{mod_id} not found.{RESET}\n")


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
    mod_id = cfg.get("current_module_id", 88)
    data = client.get_questions(mod_id, q_type="extra")
    if "error" in data:
        print(f"{RED}[{ICON_CROSS}] Error: {data['error']}{RESET}")
        return

    mod_name = data.get("module_name", f"Module #{mod_id}")
    questions = data.get("questions", [])
    answered = data.get("answered_count", 0)
    total = data.get("total", 0)

    print(header("BONUS / EXTRA CHALLENGES", f"{mod_name} │ Extra: {answered}/{total}"))
    if not questions:
        print(f"  {DIM}[!] No extra challenges for this module yet.{RESET}\n")
        return

    for q in questions:
        idx = q.get("index")
        text = q.get("text", "").replace("\n", " ")
        is_ans = q.get("answered", False)
        badge = f"{GREEN}[{ICON_CHECK}]{RESET}" if is_ans else f"{DIM}[ ]{RESET}"
        print(f" {badge} {BOLD}#{idx:<2}{RESET} {WHITE}{text}{RESET}")

    print(divider())
    print(f"{DIM}To submit extra answer:{RESET} {CYAN}cyberium submit-extra <idx> '<answer>'{RESET}\n")


def cmd_stats(client, cfg):
    """Detailed Cyberium Academy Offensive Dashboard."""
    from .ui import ASCII_BANNER, calculate_rank
    print(ASCII_BANNER)

    prof = client.get_profile()
    ident = prof.get("identity", {}) if "identity" in prof else {}
    name = f"{ident.get('firstName', '')} {ident.get('lastName', '')}"
    division = ident.get("divisionName", "")
    unit = ident.get("unitName", "")
    points = ident.get("trainingPoints", 0)
    coins = ident.get("coinBalance", 0)
    rank_title, rank_color = calculate_rank(points)

    print(f"  {BOLD}OPERATOR:{RESET}  {WHITE}{name}{RESET}  {DIM}│{RESET}  {BOLD}DIVISION:{RESET} {CYAN}{division}{RESET} {DIM}({unit}){RESET}")
    print(f"  {BOLD}RANK:{RESET}      {rank_color}{BOLD}{rank_title}{RESET}")
    print(f"  {BOLD}POINTS:{RESET}    {GREEN}{points} pts{RESET}  {DIM}│{RESET}  {BOLD}COINS:{RESET}    {YELLOW}{coins} coins{RESET}\n")

    # Program Breakdown
    progs = client.get_programs()
    prog_list = progs if isinstance(progs, list) else progs.get("programs", [])
    print(header("ENROLLED SPECIALIZATION TRACKS"))
    for p in prog_list:
        code = p.get("code", "")
        pname = p.get("name", "")
        lvl = p.get("level", 1)
        tot = p.get("total_modules", "0")
        comp = p.get("completed_modules", "0")
        pct = p.get("completion_pct", 0)
        p_bar = progress_bar(int(comp), int(tot) if int(tot) > 0 else 1, width=14)
        print(f"  {BOLD}{code:<6}{RESET} {WHITE}{pname:<26}{RESET} {p_bar} {DIM}(Lvl {lvl}) [{comp}/{tot} Mods]{RESET}")
    print(divider() + "\n")


def cmd_exam(client, cfg):
    """View module lab test / timed exam details."""
    mod_id = cfg.get("current_module_id", 88)
    prog_id = cfg.get("current_program_id", 10)
    data = client.get_modules(prog_id)
    modules = data.get("modules", [])
    for m in modules:
        if m.get("id") == mod_id:
            name = m.get("name", "")
            is_unlocked = m.get("lab_test_unlocked", False)
            is_comp = m.get("lab_test_completed", False)
            sps = m.get("lab_test_sps")
            dur = m.get("lab_test_duration_sec", 0)

            print(header("TIMED LAB EXAM / SPS PERFORMANCE", name))
            status = f"{GREEN}[✓ COMPLETED]{RESET}" if is_comp else (f"{YELLOW}[UNLOCKED]{RESET}" if is_unlocked else f"{RED}[LOCKED]{RESET}")
            print(f"  {BOLD}Module:{RESET}       {WHITE}{name}{RESET}")
            print(f"  {BOLD}Exam Status:{RESET}  {status}")
            if sps is not None:
                score_col = GREEN if sps >= 80 else (YELLOW if sps >= 60 else RED)
                print(f"  {BOLD}SPS Score:{RESET}    {score_col}{sps}% SPS Rating{RESET}")
            if dur:
                mins = dur // 60
                secs = dur % 60
                print(f"  {BOLD}Duration:{RESET}     {CYAN}{mins}m {secs}s{RESET}")
            print(divider() + "\n")
            return
    print(f"{RED}[!] Module #{mod_id} not found.{RESET}\n")


def cmd_note(cfg, args):
    """Add or read personal scratchpad note for a question."""
    from .config import get_note, save_note
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
    """Search questions in current module by keyword."""
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


def main():
    parser = argparse.ArgumentParser(
        description="Cyberium Academy Official Terminal Client & Submission Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  cyberium                      # Show current active question
  cyberium list                 # List all questions and statuses
  cyberium submit "grep -rl"    # Submit answer to current question
  cyberium modules              # List modules in active program
  cyberium set-module 88        # Switch to Module 88
  cyberium programs             # List enrolled programs
  cyberium set-program 10       # Switch to Program 10 (ZX310)
  cyberium stats                # Full operator rank, progress & coin stats
  cyberium exam                 # View timed lab exam / SPS performance
  cyberium note 14 "memo"       # Save personal note for question #14
  cyberium search "wget"        # Search questions by keyword
  cyberium book                 # View course PDF book link
  cyberium video                # View HD video lecture link
  cyberium extra                # View bonus / extra challenges
  cyberium banner               # View stylized ASCII banner & stats
  cyberium profile              # View student stats & points
  cyberium tui                  # Launch full-screen interactive TUI
  cyberium login                # Update session cookies
"""
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("status", help="Show current question & progress (default)")
    subparsers.add_parser("list", help="List all questions in current module")
    subparsers.add_parser("modules", help="List all modules in current program")
    subparsers.add_parser("programs", help="List all enrolled programs")
    subparsers.add_parser("profile", help="Show student profile & score")
    subparsers.add_parser("stats", help="Full student operator dashboard & rank")
    subparsers.add_parser("banner", help="Display Cyberium ASCII banner & stats")
    subparsers.add_parser("book", help="Get official course PDF book link")
    subparsers.add_parser("video", help="Get HD video lecture streaming link")
    subparsers.add_parser("extra", help="List bonus/extra challenges")
    subparsers.add_parser("exam", help="View module timed lab exam & SPS score")

    search_parser = subparsers.add_parser("search", help="Search questions by keyword")
    search_parser.add_argument("term", help="Search term/keyword")

    note_parser = subparsers.add_parser("note", help="Add or read question notes")
    note_parser.add_argument("index", type=int, help="Question index")
    note_parser.add_argument("text", nargs="*", help="Note text to save")

    subparsers.add_parser("login", help="Interactive login / cookie setup")
    subparsers.add_parser("tui", help="Launch interactive full-screen TUI dashboard")

    submit_parser = subparsers.add_parser("submit", help="Submit answer to current question")
    submit_parser.add_argument("answer", nargs="+", help="The answer string to submit")

    set_mod_parser = subparsers.add_parser("set-module", help="Set active module ID")
    set_mod_parser.add_argument("id", type=int, help="Module ID")

    set_prog_parser = subparsers.add_parser("set-program", help="Set active program ID")
    set_prog_parser.add_argument("id", type=int, help="Program ID")

    args = parser.parse_args()

    cfg = load_config()

    if args.command == "login":
        interactive_login(cfg)
        return

    if args.command == "tui":
        from .tui import start_tui
        start_tui()
        return

    client = ensure_client(cfg)

    if args.command in (None, "status", "current", "show"):
        cmd_current(client, cfg)
    elif args.command in ("list", "all", "questions"):
        cmd_list(client, cfg)
    elif args.command == "submit":
        answer_str = " ".join(args.answer)
        cmd_submit(client, cfg, answer_str)
    elif args.command == "modules":
        cmd_modules(client, cfg)
    elif args.command == "set-module":
        cmd_set_module(cfg, args.id)
    elif args.command == "programs":
        cmd_programs(client, cfg)
    elif args.command == "set-program":
        cmd_set_program(cfg, args.id)
    elif args.command == "profile":
        cmd_profile(client)
    elif args.command == "stats":
        cmd_stats(client, cfg)
    elif args.command == "exam":
        cmd_exam(client, cfg)
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
