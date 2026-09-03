"""
Cyberium Academy API Client
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
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                self.token = data.get("accessToken")
                self.user = data.get("user")
                if not self.token:
                    print(f"{RED}[!] Auth refresh failed: No accessToken returned.{RESET}")
                    sys.exit(1)
        except urllib.error.HTTPError as e:
            print(f"{RED}[!] Auth failed (HTTP {e.code}): Session cookies may have expired.{RESET}")
            print(f"Run {BOLD}cyberium login{RESET} to update your cookies.")
            sys.exit(1)
        except Exception as e:
            print(f"{RED}[!] Network connection error: {e}{RESET}")
            sys.exit(1)

    def request(self, endpoint, method="GET", body=None):
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
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
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
            "answer": answer.strip()
        }
        return self.request(f"/api/student/training/modules/{module_id}/answer", method="POST", body=payload)

    def get_profile(self):
        return self.request("/api/student/profile/overview")

    def get_book(self, module_id):
        return self.request(f"/api/student/training/modules/{module_id}/book")
