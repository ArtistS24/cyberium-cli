"""
Cyberium CLI Command Implementations
"""

import sys
import argparse
from .config import load_config, save_config, interactive_login
from .api import CyberiumClient
from .ui import (
    RED, GREEN, YELLOW, CYAN, WHITE, DIM, BOLD, RESET,
    header, divider, badge_success, badge_pending, badge_failed, badge_empty, progress_bar
)


def cmd_current(client, cfg):
    module_id = cfg.get("current_module_id", 88)
    q_data = client.get_questions(module_id)
    if "error" in q_data:
        print(f"{RED}[!] Error: {q_data['error']}{RESET}")
        return

    mod_name = q_data.get("module_name", f"Module #{module_id}")
    total = q_data.get("total", 0)
    answered = q_data.get("answered_count", 0)
    first_unanswered = q_data.get("first_unanswered")
    questions = q_data.get("questions", [])

    progress_str = f"Lab: {answered}/{total} ({progress_bar(answered, total, width=12)})"
    print(header(mod_name, progress_str))

    if first_unanswered is None or first_unanswered >= len(questions):
        print(f"{GREEN}{BOLD}[✓] All {total} questions in this module are completed!{RESET}\n")
        return

    curr_q = questions[first_unanswered]
    q_text = curr_q.get("text", "")
    q_idx = curr_q.get("index", first_unanswered)

    print(f"{YELLOW}{BOLD}[⏳] CURRENT OBJECTIVE (Index {q_idx}):{RESET}")
    print(f"  {WHITE}{BOLD}{q_text}{RESET}\n")
    print(f"{DIM}To submit your answer:{RESET}")
    print(f"  {CYAN}cyberium submit \"<your_answer>\"{RESET}\n")


def cmd_list(client, cfg):
    module_id = cfg.get("current_module_id", 88)
    q_data = client.get_questions(module_id)
    if "error" in q_data:
        print(f"{RED}[!] Error: {q_data['error']}{RESET}")
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
        print(f"{RED}[!] Error: {q_data['error']}{RESET}")
        return

    first_unanswered = q_data.get("first_unanswered")
    questions = q_data.get("questions", [])

    if first_unanswered is None or first_unanswered >= len(questions):
        print(f"{GREEN}[✓] All questions in this module are already completed!{RESET}")
        return

    curr_q = questions[first_unanswered]
    q_idx = curr_q.get("index", first_unanswered)
    q_text = curr_q.get("text", "")

    print(f"\n{DIM}[*] Question #{q_idx}:{RESET} {WHITE}{q_text}{RESET}")
    print(f"{DIM}[*] Submitting answer:{RESET} {CYAN}{BOLD}{answer_str}{RESET}")

    resp = client.submit_answer(module_id, q_idx, answer_str)

    if resp.get("correct"):
        print(f"{GREEN}{BOLD}[✓] CORRECT! Points awarded.{RESET}")
        next_data = client.get_questions(module_id)
        next_idx = next_data.get("first_unanswered")
        if next_idx is not None and next_idx < len(next_data.get("questions", [])):
            nxt_q = next_data["questions"][next_idx]
            print(f"\n{YELLOW}{BOLD}[⏳] NEXT OBJECTIVE (#{nxt_q.get('index')}):{RESET}")
            print(f"  {WHITE}{BOLD}{nxt_q.get('text')}{RESET}\n")
    elif resp.get("already_answered"):
        print(f"{YELLOW}[!] This question was already answered.{RESET}\n")
    else:
        err_msg = resp.get("message") or resp.get("error") or "Incorrect answer. Try again."
        print(f"{RED}{BOLD}[✗] {err_msg}{RESET}\n")


def cmd_modules(client, cfg):
    prog_id = cfg.get("current_program_id", 10)
    data = client.get_modules(prog_id)
    if "error" in data:
        print(f"{RED}[!] Error: {data['error']}{RESET}")
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
        active_mark = f"{YELLOW}►{RESET}" if mid == curr_mod else " "

        print(f" {active_mark} {BOLD}#{order:<2}{RESET} {WHITE}{name:<30}{RESET} {DIM}ID: {mid:<3}│ Lab: {correct:>2}/{total:<2} ({pct}%){RESET}")

    print(divider())
    print(f"{DIM}To switch module:{RESET} {CYAN}cyberium set-module <ID>{RESET}\n")


def cmd_set_module(cfg, mod_id):
    cfg["current_module_id"] = int(mod_id)
    save_config(cfg)
    print(f"{GREEN}[✓] Active module set to ID {mod_id}.{RESET}")


def cmd_programs(client, cfg):
    programs = client.get_programs()
    if isinstance(programs, dict) and "error" in programs:
        print(f"{RED}[!] Error: {programs['error']}{RESET}")
        return

    curr_prog = cfg.get("current_program_id")
    print(header("ENROLLED PROGRAMS"))

    for p in programs:
        pid = p.get("id")
        code = p.get("code", "")
        name = p.get("name", "")
        done_mods = p.get("completed_modules", 0)
        tot_mods = p.get("total_modules", 0)
        active_mark = f"{YELLOW}►{RESET}" if pid == curr_prog else " "

        print(f" {active_mark} {BOLD}{code:<8}{RESET} {WHITE}{name:<28}{RESET} {DIM}ID: {pid:<2}│ Modules: {done_mods}/{tot_mods}{RESET}")

    print(divider())
    print(f"{DIM}To switch program:{RESET} {CYAN}cyberium set-program <ID>{RESET}\n")


def cmd_set_program(cfg, prog_id):
    cfg["current_program_id"] = int(prog_id)
    save_config(cfg)
    print(f"{GREEN}[✓] Active program set to ID {prog_id}.{RESET}")


def cmd_profile(client):
    data = client.get_profile()
    if "error" in data:
        print(f"{RED}[!] Error: {data['error']}{RESET}")
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
  cyberium profile              # View student stats & points
  cyberium login                # Update session cookies
"""
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("status", help="Show current question & progress (default)")
    subparsers.add_parser("list", help="List all questions in current module")
    subparsers.add_parser("modules", help="List all modules in current program")
    subparsers.add_parser("programs", help="List all enrolled programs")
    subparsers.add_parser("profile", help="Show student profile & score")
    subparsers.add_parser("login", help="Interactive login / cookie setup")

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

    client = CyberiumClient(cfg)

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
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
