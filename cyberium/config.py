"""
Configuration and Session Manager for Cyberium CLI
Supports:
1. ~/.config/cyberium/config.json (Per-user default)
2. Local .env file in project/current directory
3. Environment variables (CYBERIUM_CONNECT_SID, CYBERIUM_CYB_RT)
"""

import os
import json
import sys
from .ui import RED, GREEN, YELLOW, CYAN, WHITE, DIM, BOLD, RESET, header, divider

CONFIG_DIR = os.path.expanduser("~/.config/cyberium")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")


def parse_env_file(filepath):
    """Parse a simple key=value .env file without external dependencies."""
    env_vars = {}
    if not os.path.exists(filepath):
        return env_vars
    try:
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("\"'").strip()
                env_vars[k] = v
    except Exception:
        pass
    return env_vars


def load_config():
    """
    Loads configuration in order of priority:
    1. Environment variables
    2. Local .env file (if present)
    3. ~/.config/cyberium/config.json
    """
    config = {
        "cookies": {},
        "current_program_id": 10,
        "current_module_id": 88
    }

    # 1. Base config from ~/.config/cyberium/config.json
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                saved = json.load(f)
                config.update(saved)
        except Exception:
            pass

    # 2. Local .env file in cwd or project root
    local_env = parse_env_file(".env")
    if not local_env:
        # Check project root if invoked via symlink
        script_root = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
        project_env_path = os.path.join(script_root, ".env")
        if os.path.exists(project_env_path):
            local_env = parse_env_file(project_env_path)

    # 3. Environment variables overrides
    connect_sid = os.getenv("CYBERIUM_CONNECT_SID") or local_env.get("CONNECT_SID") or local_env.get("CYBERIUM_CONNECT_SID")
    cyb_rt = os.getenv("CYBERIUM_CYB_RT") or local_env.get("CYB_RT") or local_env.get("CYBERIUM_CYB_RT")
    cyb_td = os.getenv("CYBERIUM_CYB_TD") or local_env.get("CYB_TD") or local_env.get("CYBERIUM_CYB_TD")
    cflb = os.getenv("CYBERIUM_CFLB") or local_env.get("CFLB") or local_env.get("CYBERIUM_CFLB")

    if connect_sid:
        config.setdefault("cookies", {})["connect.sid"] = connect_sid
    if cyb_rt:
        config.setdefault("cookies", {})["cyb_rt"] = cyb_rt
    if cyb_td:
        config.setdefault("cookies", {})["cyb_td"] = cyb_td
    if cflb:
        config.setdefault("cookies", {})["__cflb"] = cflb

    # Override program/module IDs if specified
    prog_id = os.getenv("CYBERIUM_PROGRAM_ID") or local_env.get("CURRENT_PROGRAM_ID")
    if prog_id:
        try:
            config["current_program_id"] = int(prog_id)
        except ValueError:
            pass

    mod_id = os.getenv("CYBERIUM_MODULE_ID") or local_env.get("CURRENT_MODULE_ID")
    if mod_id:
        try:
            config["current_module_id"] = int(mod_id)
        except ValueError:
            pass

    return config


def save_config(cfg):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def interactive_login(cfg=None):
    if cfg is None:
        cfg = load_config()

    print(header("STUDENT AUTHENTICATION"))
    print(f"{WHITE}Each student has their own unique session on Cyberium Academy.{RESET}")
    print(f"{DIM}Follow these steps to link your terminal client:{RESET}\n")
    print(f"  1. Log into {CYAN}https://cyberium.academy{RESET} in your browser.")
    print(f"  2. Press {BOLD}F12{RESET} -> {BOLD}Storage / Application{RESET} -> {BOLD}Cookies{RESET}.")
    print(f"  3. Copy the values for {BOLD}connect.sid{RESET} and {BOLD}cyb_rt{RESET}.\n")

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
    print(f"\n{GREEN}[✓] Credentials saved securely to {CONFIG_PATH}!{RESET}")
    print(f"{DIM}Your session is independent to your local user account.{RESET}\n")
    return True
