"""
Cyberium Academy API Client
Robust, Token-Aware HTTP Client with Automatic Refresh and Error Recovery.
"""

import sys
import json
import urllib.request
import urllib.error
from .ui import RED, BOLD, RESET

BASE_URL = "https://cyberium.academy"


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
        if not self.cookies or not self.cookies.get("connect.sid"):
            print(f"{RED}[!] No session cookies configured.{RESET}")
            print(f"Run {BOLD}cyberium login{RESET} to authenticate your terminal client.")
            sys.exit(1)

        self.refresh_token(exit_on_failure=True)

    def refresh_token(self, exit_on_failure=False):
        """Refreshes the JWT accessToken using persistent connect.sid / cyb_rt cookies."""
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
            if exit_on_failure:
                print(f"{RED}[!] Auth failed (HTTP {e.code}): Session cookies may have expired.{RESET}")
                print(f"Run {BOLD}cyberium login{RESET} to update your cookies.")
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
