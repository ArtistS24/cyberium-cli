"""
Configuration and Session Manager for Cyberium CLI
"""

import os
import json
import sys
from .ui import RED, GREEN, YELLOW, CYAN, WHITE, DIM, BOLD, RESET, header, divider

CONFIG_DIR = os.path.expanduser("~/.config/cyberium")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")


def load_config():
    if not os.path.exists(CONFIG_PATH):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        default_config = {
            "cookies": {},
            "current_program_id": 10,
            "current_module_id": 88
        }
        with open(CONFIG_PATH, "w") as f:
            json.dump(default_config, f, indent=2)
        return default_config
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"{RED}[!] Error loading config from {CONFIG_PATH}: {e}{RESET}")
        sys.exit(1)


def save_config(cfg):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def interactive_login(cfg):
    print(header("STUDENT AUTHENTICATION"))
    print(f"{WHITE}To link your Cyberium account:{RESET}")
    print(f"1. Open {CYAN}https://cyberium.academy{RESET} in your browser and log in.")
    print(f"2. Press {BOLD}F12{RESET} -> {BOLD}Storage / Application{RESET} -> {BOLD}Cookies{RESET}.")
    print(f"3. Copy the values for {BOLD}connect.sid{RESET} and {BOLD}cyb_rt{RESET}.\n")

    connect_sid = input(f"{YELLOW}Enter connect.sid:{RESET} ").strip()
    cyb_rt = input(f"{YELLOW}Enter cyb_rt:{RESET} ").strip()
    cyb_td = input(f"{YELLOW}Enter cyb_td (optional, press Enter to skip):{RESET} ").strip()
    cflb = input(f"{YELLOW}Enter __cflb (optional, press Enter to skip):{RESET} ").strip()

    if not connect_sid or not cyb_rt:
        print(f"\n{RED}[!] connect.sid and cyb_rt are required for authentication.{RESET}")
        return False

    cookies = {
        "connect.sid": connect_sid,
        "cyb_rt": cyb_rt
    }
    if cyb_td:
        cookies["cyb_td"] = cyb_td
    if cflb:
        cookies["__cflb"] = cflb

    cfg["cookies"] = cookies
    save_config(cfg)
    print(f"\n{GREEN}[✓] Credentials saved to {CONFIG_PATH}!{RESET}\n")
    return True
