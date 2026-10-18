"""
Cyberium Academy API Client
Robust, Token-Aware HTTP Client with Automatic Refresh and Error Recovery.
"""

import sys
import os
import json
import re
import urllib.request
import urllib.error
import urllib.parse
from .ui import RED, GREEN, YELLOW, CYAN, BOLD, RESET
from .config import auto_sync_firefox_cookies, BOOKS_DIR

BASE_URL = "https://cyberium.academy"


def get_filename_from_url(url, fallback="course-book.pdf"):
    """Extract human-readable filename from URL or response-content-disposition query param."""
    if not url:
        return fallback
    try:
        parsed = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(parsed.query)
        if "response-content-disposition" in qs:
            disp = qs["response-content-disposition"][0]
            m = re.search(r"filename\*=UTF-8''([^;\"]+)", disp)
            if m:
                return urllib.parse.unquote(m.group(1))
            m = re.search(r"filename=\"?([^;\"]+)\"?", disp)
            if m:
                return urllib.parse.unquote(m.group(1).strip("\"'"))
        path_name = os.path.basename(parsed.path)
        if path_name and "." in path_name:
            return path_name
    except Exception:
        pass
    return fallback


def download_file(url, dest_path, progress_callback=None):
    """
    Downloads a remote file with progress tracking and streaming blocks.
    Returns the absolute path to the downloaded file.
    """
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
    })
    dest_path = os.path.abspath(os.path.expanduser(dest_path))
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    with urllib.request.urlopen(req, timeout=30) as resp:
        total_size = int(resp.headers.get("content-length", 0))
        downloaded = 0
        block_size = 65536
        with open(dest_path, "wb") as f:
            while True:
                chunk = resp.read(block_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if progress_callback:
                    progress_callback(downloaded, total_size)
    return dest_path


class CyberiumClient:
    def __init__(self, config):
        self.config = config
        self.cookies = config.get("cookies", {})
        self.token = None
        self.user = None
        self.authenticate()

    def get_cookie_header(self):
        return "; ".join([f"{k}={v}" for k, v in self.cookies.items()])

    def authenticate(self):
        if not self.cookies or not self.cookies.get("cyb_rt"):
            if auto_sync_firefox_cookies(self.config):
                self.cookies = self.config.get("cookies", {})

        if not self.cookies or not self.cookies.get("cyb_rt"):
            print(f"{RED}[!] No Cyberium session cookies found.{RESET}")
            print(f"Run {BOLD}cyberium login{RESET} or open Cyberium in Firefox to authenticate.")
            sys.exit(1)

        self.refresh_token(exit_on_failure=True)

    def refresh_token(self, exit_on_failure=False, _auto_synced=False):
        """Refreshes the JWT accessToken using persistent cyb_rt refresh token."""
        refresh_url = f"{BASE_URL}/api/auth/refresh"
        req = urllib.request.Request(
            refresh_url,
            data=b"{}",
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
                "Cookie": self.get_cookie_header(),
                "Content-Type": "application/json"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                self.token = data.get("accessToken")
                self.user = data.get("user")
                if not self.token and exit_on_failure:
                    print(f"{RED}[!] Auth refresh failed: No accessToken returned.{RESET}")
                    sys.exit(1)
                return bool(self.token)
        except urllib.error.HTTPError as e:
            if e.code == 401 and not _auto_synced:
                # Cookies expired -> check Firefox for fresh cookies
                if auto_sync_firefox_cookies(self.config):
                    self.cookies = self.config.get("cookies", {})
                    return self.refresh_token(exit_on_failure=exit_on_failure, _auto_synced=True)

            if exit_on_failure:
                print(f"{RED}[!] Auth failed (HTTP {e.code}): Session cookies may have expired.{RESET}")
                print(f"Run {BOLD}cyberium login{RESET} or open {CYAN}https://cyberium.academy{RESET} in Firefox.")
                sys.exit(1)
            return False
        except Exception as e:
            if exit_on_failure:
                print(f"{RED}[!] Network connection error: {e}{RESET}")
                sys.exit(1)
            return False

    def request(self, endpoint, method="GET", body=None, _retried=False):
        url = f"{BASE_URL}{endpoint}" if not endpoint.startswith("http") else endpoint
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
            "Cookie": self.get_cookie_header(),
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        data_bytes = json.dumps(body).encode("utf-8") if body else None
        req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            if e.code == 401 and not _retried:
                # Token may have expired during active session -> attempt transparent refresh
                if self.refresh_token():
                    return self.request(endpoint, method=method, body=body, _retried=True)
            try:
                return json.loads(e.read().decode("utf-8"))
            except Exception:
                return {"error": f"HTTP {e.code}: {e.reason}"}
        except Exception as e:
            return {"error": str(e)}

    def get_programs(self):
        return self.request("/api/student/training/programs")

    def get_modules(self, program_id):
        return self.request(f"/api/student/training/programs/{program_id}/modules")

    def get_questions(self, module_id, q_type="lab"):
        return self.request(f"/api/student/training/modules/{module_id}/questions?type={q_type}")

    def submit_answer(self, module_id, question_index, answer, q_type="lab"):
        payload = {
            "type": q_type,
            "question_index": question_index,
            "answer": str(answer).strip()
        }
        return self.request(f"/api/student/training/modules/{module_id}/answer", method="POST", body=payload)

    def get_profile(self):
        return self.request("/api/student/profile/overview")

    def get_book(self, module_id):
        return self.request(f"/api/student/training/modules/{module_id}/book")

    def get_book_info(self, module_id, module_name=""):
        """Fetches book URL and extracts formatted human-readable metadata."""
        resp = self.get_book(module_id)
        url = resp.get("url") if isinstance(resp, dict) else None
        if not url:
            return None
        fallback_name = f"{module_name.replace('/', '-').strip()}-Book.pdf" if module_name else f"Module-{module_id}-Book.pdf"
        filename = get_filename_from_url(url, fallback_name)
        return {
            "url": url,
            "filename": filename,
            "module_id": module_id,
            "module_name": module_name
        }

    def logout(self):
        """Logs out from the server and invalidates token."""
        try:
            self.request("/api/auth/logout", method="POST")
        except Exception:
            pass
        self.cookies = {}
        self.token = None
        self.user = None


def get_book_info(client_or_mod_id, module_name="", client=None):
    """Top-level helper to fetch book metadata from client."""
    if hasattr(client_or_mod_id, "get_book_info"):
        return client_or_mod_id.get_book_info(module_name)
    if client and hasattr(client, "get_book_info"):
        return client.get_book_info(client_or_mod_id, module_name)
    return None
