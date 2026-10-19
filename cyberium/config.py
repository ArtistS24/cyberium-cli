"""
Configuration and Session Manager for Cyberium CLI
Supports:
1. ~/.config/cyberium/config.json (Per-user default)
2. Local .env file in project/current directory
3. Environment variables (CYBERIUM_CONNECT_SID, CYBERIUM_CYB_RT)
"""

import os
import glob
import json
import sqlite3
import shutil
import tempfile
from .ui import RED, GREEN, YELLOW, CYAN, WHITE, DIM, BOLD, RESET, header, divider

CONFIG_DIR = os.path.expanduser("~/.config/cyberium")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
NOTES_PATH = os.path.join(CONFIG_DIR, "notes.json")
CACHE_DIR = os.path.expanduser("~/.cache/cyberium")
BOOKS_DIR = os.path.join(CACHE_DIR, "books")


def _atomic_json_write(filepath, data):
    """Safely and atomically writes JSON to disk to avoid corruption with strict POSIX permissions."""
    target_dir = os.path.dirname(filepath)
    os.makedirs(target_dir, mode=0o700, exist_ok=True)
    try:
        os.chmod(target_dir, 0o700)
    except Exception:
        pass

    with tempfile.NamedTemporaryFile("w", dir=target_dir, delete=False) as tf:
        json.dump(data, tf, indent=2)
        temp_name = tf.name

    try:
        os.chmod(temp_name, 0o600)
    except Exception:
        pass

    os.replace(temp_name, filepath)

    try:
        os.chmod(filepath, 0o600)
    except Exception:
        pass


def find_browser_cyberium_cookies():
    """
    Scans all installed web browsers on Linux for live Cyberium Academy session cookies:
    - Firefox, Firefox PWA, LibreWolf, Waterfox, Floorp, Zen Browser, Tor Browser
    - Google Chrome, Chromium, Brave, Microsoft Edge, Vivaldi, Opera
    - Flatpak & Snap sandboxed browser containers
    Returns a dictionary of found cookies or empty dict.
    """
    # 1. Firefox / Gecko databases (moz_cookies table: name, value, host)
    gecko_patterns = [
        os.path.expanduser("~/.config/mozilla/firefox/*/cookies.sqlite"),
        os.path.expanduser("~/.mozilla/firefox/*/cookies.sqlite"),
        os.path.expanduser("~/.local/share/firefoxpwa/profiles/*/cookies.sqlite"),
        os.path.expanduser("~/.var/app/org.mozilla.firefox/.mozilla/firefox/*/cookies.sqlite"),
        os.path.expanduser("~/.var/app/org.mozilla.firefox/data/mozilla/firefox/*/cookies.sqlite"),
        os.path.expanduser("~/snap/firefox/common/.mozilla/firefox/*/cookies.sqlite"),
        os.path.expanduser("~/.librewolf/*/cookies.sqlite"),
        os.path.expanduser("~/.var/app/io.gitlab.librewolf-community/.librewolf/*/cookies.sqlite"),
        os.path.expanduser("~/.waterfox/*/cookies.sqlite"),
        os.path.expanduser("~/.floorp/*/cookies.sqlite"),
        os.path.expanduser("~/.zen/*/cookies.sqlite"),
        os.path.expanduser("~/.var/app/app.zen_browser.zen/.zen/*/cookies.sqlite"),
    ]

    # 2. Chromium databases (cookies table: name, value, host_key)
    chromium_patterns = [
        os.path.expanduser("~/.config/google-chrome/*/Cookies"),
        os.path.expanduser("~/.config/google-chrome/Default/Cookies"),
        os.path.expanduser("~/.config/chromium/*/Cookies"),
        os.path.expanduser("~/.config/chromium/Default/Cookies"),
        os.path.expanduser("~/.var/app/org.chromium.Chromium/config/chromium/*/Cookies"),
        os.path.expanduser("~/.config/BraveSoftware/Brave-Browser/*/Cookies"),
        os.path.expanduser("~/.config/BraveSoftware/Brave-Browser/Default/Cookies"),
        os.path.expanduser("~/.var/app/com.brave.Browser/config/BraveSoftware/Brave-Browser/*/Cookies"),
        os.path.expanduser("~/.config/microsoft-edge/*/Cookies"),
        os.path.expanduser("~/.config/microsoft-edge/Default/Cookies"),
        os.path.expanduser("~/.config/vivaldi/*/Cookies"),
        os.path.expanduser("~/.config/vivaldi/Default/Cookies"),
        os.path.expanduser("~/.config/opera/Cookies"),
        os.path.expanduser("~/.var/app/com.opera.Opera/config/opera/Cookies"),
    ]

    best_cookies = {}
    newest_mtime = 0

    # Scan Gecko / Firefox databases
    for pattern in gecko_patterns:
        for db_path in glob.glob(pattern):
            if not os.path.exists(db_path):
                continue
            try:
                mtime = os.path.getmtime(db_path)
                tmp_db = tempfile.mktemp(suffix=".sqlite")
                shutil.copy2(db_path, tmp_db)
                wal_path = db_path + "-wal"
                if os.path.exists(wal_path):
                    shutil.copy2(wal_path, tmp_db + "-wal")

                con = sqlite3.connect(tmp_db)
                cur = con.cursor()
                cur.execute("SELECT name, value FROM moz_cookies WHERE host LIKE '%cyberium.academy%'")
                rows = cur.fetchall()
                con.close()

                if os.path.exists(tmp_db):
                    os.remove(tmp_db)
                if os.path.exists(tmp_db + "-wal"):
                    os.remove(tmp_db + "-wal")

                if rows:
                    cdict = {r[0]: r[1] for r in rows if r[1]}
                    if "cyb_rt" in cdict:
                        if mtime > newest_mtime or not best_cookies:
                            newest_mtime = mtime
                            best_cookies = cdict
            except Exception:
                pass

    # Scan Chromium databases
    for pattern in chromium_patterns:
        for db_path in glob.glob(pattern):
            if not os.path.exists(db_path):
                continue
            try:
                mtime = os.path.getmtime(db_path)
                if mtime < newest_mtime and best_cookies:
                    continue
                tmp_db = tempfile.mktemp(suffix=".sqlite")
                shutil.copy2(db_path, tmp_db)
                wal_path = db_path + "-wal"
                if os.path.exists(wal_path):
                    shutil.copy2(wal_path, tmp_db + "-wal")

                con = sqlite3.connect(tmp_db)
                cur = con.cursor()
                cur.execute("SELECT name, value FROM cookies WHERE host_key LIKE '%cyberium.academy%'")
                rows = cur.fetchall()
                con.close()

                if os.path.exists(tmp_db):
                    os.remove(tmp_db)
                if os.path.exists(tmp_db + "-wal"):
                    os.remove(tmp_db + "-wal")

                if rows:
                    cdict = {r[0]: r[1] for r in rows if r[1]}
                    if "cyb_rt" in cdict:
                        if mtime > newest_mtime or not best_cookies:
                            newest_mtime = mtime
                            best_cookies = cdict
            except Exception:
                pass

    return best_cookies


def find_firefox_cyberium_cookies():
    """Alias for backwards compatibility."""
    return find_browser_cyberium_cookies()


def auto_sync_browser_cookies(cfg=None):
    """
    Automatically detects and saves live Cyberium cookies from local browser.
    Returns True if valid cookies were found and saved.
    """
    found = find_browser_cyberium_cookies()
    if not found or "cyb_rt" not in found:
        return False

    if cfg is None:
        cfg = load_config()

    cfg.setdefault("cookies", {}).update(found)
    save_config(cfg)
    return True


def auto_sync_firefox_cookies(cfg=None):
    """Alias for backwards compatibility."""
    return auto_sync_browser_cookies(cfg)


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
    Auto-discovers Firefox session if local cookies are missing.
    """
    config = {
        "cookies": {},
        "current_program_id": 10,
        "current_module_id": 88,
        "theme": "cyberium"
    }

    # 1. Base config from ~/.config/cyberium/config.json
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                saved = json.load(f)
                if isinstance(saved, dict):
                    config.update(saved)
        except Exception:
            pass

    # 2. Local .env file in cwd or project root
    local_env = parse_env_file(".env")
    if not local_env:
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

    if not config.get("cookies", {}).get("cyb_rt"):
        auto_cookies = find_firefox_cyberium_cookies()
        if auto_cookies:
            config.setdefault("cookies", {}).update(auto_cookies)
            save_config(config)

    return config


def save_config(cfg):
    try:
        _atomic_json_write(CONFIG_PATH, cfg)
    except Exception as e:
        print(f"{RED}[!] Failed to save config: {e}{RESET}")


def interactive_login(cfg=None, force_manual=False):
    if cfg is None:
        cfg = load_config()

    print(header("STUDENT AUTHENTICATION"))

    if not force_manual:
        auto_cookies = find_firefox_cyberium_cookies()
        if auto_cookies and "cyb_rt" in auto_cookies:
            print(f"{GREEN}[✓] Detected active Cyberium Academy session in your browser!{RESET}")
            ans = input(f"{CYAN}Import session credentials automatically? [Y/n]: {RESET}").strip().lower()
            if ans in ("", "y", "yes"):
                cfg["cookies"] = auto_cookies
                save_config(cfg)
                print(f"\n{GREEN}[✓] Session imported successfully from Firefox to {CONFIG_PATH}!{RESET}\n")
                return True

    print(f"{WHITE}Each student has their own unique session on Cyberium Academy.{RESET}")
    print(f"{DIM}Follow these steps to link your terminal client manually:{RESET}\n")
    print(f"  1. Log into {CYAN}https://cyberium.academy{RESET} in your browser.")
    print(f"  2. Press {BOLD}F12{RESET} -> {BOLD}Storage / Application{RESET} -> {BOLD}Cookies{RESET}.")
    print(f"  3. Copy the value for {BOLD}cyb_rt{RESET} (JWT refresh token).\n")

    cyb_rt = input(f"{YELLOW}Enter cyb_rt:{RESET} ").strip()
    cflb = input(f"{YELLOW}Enter __cflb (optional, press Enter to skip):{RESET} ").strip()
    connect_sid = input(f"{YELLOW}Enter connect.sid (legacy / optional, press Enter to skip):{RESET} ").strip()
    cyb_td = input(f"{YELLOW}Enter cyb_td (optional, press Enter to skip):{RESET} ").strip()

    if not cyb_rt:
        print(f"\n{RED}[!] cyb_rt is required for authentication.{RESET}")
        return False

    cookies = {
        "cyb_rt": cyb_rt
    }
    if cflb:
        cookies["__cflb"] = cflb
    if connect_sid:
        cookies["connect.sid"] = connect_sid
    if cyb_td:
        cookies["cyb_td"] = cyb_td

    cfg["cookies"] = cookies
    save_config(cfg)
    print(f"\n{GREEN}[✓] Credentials saved securely to {CONFIG_PATH}!{RESET}")
    print(f"{DIM}Your session is independent to your local user account.{RESET}\n")
    return True


def load_notes():
    """Load user notes dictionary from ~/.config/cyberium/notes.json."""
    if os.path.exists(NOTES_PATH):
        try:
            with open(NOTES_PATH, "r") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except Exception:
            pass
    return {}


def get_note(module_id, question_index):
    """Retrieve personal note for a specific question."""
    notes = load_notes()
    key = f"{module_id}_{question_index}"
    return notes.get(key, "")


def save_note(module_id, question_index, note_text):
    """Save or update personal note for a specific question."""
    notes = load_notes()
    key = f"{module_id}_{question_index}"
    note_str = str(note_text).strip() if note_text is not None else ""
    if note_str:
        notes[key] = note_str
    elif key in notes:
        del notes[key]
    try:
        _atomic_json_write(NOTES_PATH, notes)
    except Exception as e:
        print(f"{RED}[!] Failed to save note: {e}{RESET}")


def clear_session(cfg=None):
    """Clears saved session cookies from configuration file."""
    if cfg is None:
        cfg = load_config()
    cfg["cookies"] = {}
    save_config(cfg)
    return True
