"""
Comprehensive Automated Test Suite for Cyberium CLI & TUI
Covers: Config, API, UI, CLI Commands, TUI Logic, Edge Cases, Corrupt State Recovery, and Network Faults
"""

import os
import sys
import unittest
import tempfile
import json
import urllib.error
from unittest.mock import patch, MagicMock

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from cyberium import config, ui, api, cli, tui


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.orig_config_dir = config.CONFIG_DIR
        self.orig_config_path = config.CONFIG_PATH
        self.orig_notes_path = config.NOTES_PATH

        config.CONFIG_DIR = self.temp_dir
        config.CONFIG_PATH = os.path.join(self.temp_dir, "config.json")
        config.NOTES_PATH = os.path.join(self.temp_dir, "notes.json")

    def tearDown(self):
        config.CONFIG_DIR = self.orig_config_dir
        config.CONFIG_PATH = self.orig_config_path
        config.NOTES_PATH = self.orig_notes_path

    def test_default_config(self):
        cfg = config.load_config()
        self.assertEqual(cfg.get("theme"), "cyberium")
        self.assertEqual(cfg.get("current_program_id"), 10)
        self.assertEqual(cfg.get("current_module_id"), 88)
        self.assertIsInstance(cfg.get("cookies"), dict)

    def test_save_and_load_config(self):
        cfg = config.load_config()
        cfg["theme"] = "dracula"
        cfg["current_program_id"] = 7
        config.save_config(cfg)

        reloaded = config.load_config()
        self.assertEqual(reloaded["theme"], "dracula")
        self.assertEqual(reloaded["current_program_id"], 7)

    def test_corrupt_config_recovery(self):
        # Write corrupted JSON
        with open(config.CONFIG_PATH, "w") as f:
            f.write("{invalid json: corrupt!!!")

        # load_config should safely fallback to default without crashing
        cfg = config.load_config()
        self.assertEqual(cfg.get("theme"), "cyberium")
        self.assertEqual(cfg.get("current_program_id"), 10)

    def test_corrupt_notes_recovery(self):
        with open(config.NOTES_PATH, "w") as f:
            f.write("NOT_A_JSON")

        notes = config.load_notes()
        self.assertEqual(notes, {})
        self.assertEqual(config.get_note(88, 14), "")

    def test_env_override(self):
        with patch.dict(os.environ, {
            "CYBERIUM_CONNECT_SID": "test_sid_123",
            "CYBERIUM_PROGRAM_ID": "3",
            "CYBERIUM_MODULE_ID": "42"
        }):
            cfg = config.load_config()
            self.assertEqual(cfg["cookies"].get("connect.sid"), "test_sid_123")
            self.assertEqual(cfg["current_program_id"], 3)
            self.assertEqual(cfg["current_module_id"], 42)

    def test_notes_crud(self):
        self.assertEqual(config.get_note(88, 14), "")
        config.save_note(88, 14, "Remember to use --post-file")
        self.assertEqual(config.get_note(88, 14), "Remember to use --post-file")

        # Overwrite note
        config.save_note(88, 14, "Updated note text")
        self.assertEqual(config.get_note(88, 14), "Updated note text")

        # Delete note
        config.save_note(88, 14, "")
        self.assertEqual(config.get_note(88, 14), "")

    def test_notes_safe_types(self):
        # Passing None or integer should not crash
        config.save_note(88, 14, None)
        self.assertEqual(config.get_note(88, 14), "")
        config.save_note(88, 15, 12345)
        self.assertEqual(config.get_note(88, 15), "12345")

    def test_parse_env_file(self):
        env_file = os.path.join(self.temp_dir, ".test.env")
        with open(env_file, "w") as f:
            f.write("# Comment line\nCONNECT_SID=\"secret_val\"\nCYB_RT = token123\nEMPTY=\n")
        
        parsed = config.parse_env_file(env_file)
        self.assertEqual(parsed.get("CONNECT_SID"), "secret_val")
        self.assertEqual(parsed.get("CYB_RT"), "token123")


class TestUI(unittest.TestCase):
    def test_all_16_themes_validity(self):
        self.assertGreaterEqual(len(ui.THEMES), 16)
        valid_colors = {"white", "cyan", "green", "yellow", "red", "magenta", "blue", "dim", "black"}

        for tname, tdata in ui.THEMES.items():
            self.assertIn("name", tdata, f"Theme '{tname}' missing name")
            self.assertIn("desc", tdata, f"Theme '{tname}' missing desc")
            for p in range(1, 8):
                key = f"pair{p}"
                self.assertIn(key, tdata, f"Theme '{tname}' missing '{key}'")
                self.assertIn(tdata[key], valid_colors, f"Theme '{tname}' has invalid color '{tdata[key]}'")

    def test_calculate_rank_bounds(self):
        self.assertIn("MASTER", ui.calculate_rank(600)[0])
        self.assertIn("SENIOR", ui.calculate_rank(300)[0])
        self.assertIn("EXPERT", ui.calculate_rank(134)[0])
        self.assertIn("PRACTITIONER", ui.calculate_rank(50)[0])
        self.assertIn("APPRENTICE", ui.calculate_rank(20)[0])
        self.assertIn("RECRUIT", ui.calculate_rank(5)[0])
        self.assertIn("RECRUIT", ui.calculate_rank(0)[0])
        self.assertIn("RECRUIT", ui.calculate_rank(-10)[0])
        self.assertIn("RECRUIT", ui.calculate_rank("invalid")[0])

    def test_progress_bar_bounds(self):
        bar_empty = ui.progress_bar(0, 0)
        self.assertIn("0%", bar_empty)

        bar_half = ui.progress_bar(10, 20, width=10)
        self.assertIn("50%", bar_half)
        self.assertIn("■■■■■□□□□□", bar_half)

        bar_full = ui.progress_bar(83, 83, width=10)
        self.assertIn("100%", bar_full)
        self.assertIn("■■■■■■■■■■", bar_full)

        # Overflow & invalid inputs
        bar_over = ui.progress_bar(120, 83, width=10)
        self.assertIn("100%", bar_over)
        self.assertIn("■■■■■■■■■■", bar_over)

        bar_neg = ui.progress_bar(-5, 83, width=10)
        self.assertIn("0%", bar_neg)

    def test_badges_and_headers(self):
        h = ui.header("TEST MODULE", "Subtitle")
        self.assertIn("C Y B E R I U M", h)
        self.assertIn("TEST MODULE", h)
        self.assertIn("Subtitle", h)

        self.assertIn("✓", ui.badge_success("Solved"))
        self.assertIn("", ui.badge_pending("Active"))
        self.assertIn("✗", ui.badge_failed("Failed"))
        self.assertIn("[ ]", ui.badge_empty("Empty"))


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.cfg = {
            "cookies": {"connect.sid": "mock_sid", "cyb_rt": "mock_rt"},
            "current_program_id": 10,
            "current_module_id": 88
        }

    @patch("urllib.request.urlopen")
    def test_auth_refresh(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "accessToken": "mock_jwt_token",
            "user": {"id": 1, "username": "student"}
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        client = api.CyberiumClient(self.cfg)
        self.assertEqual(client.token, "mock_jwt_token")
        self.assertEqual(client.user["username"], "student")

    @patch("urllib.request.urlopen")
    def test_get_programs(self, mock_urlopen):
        mock_auth = MagicMock()
        mock_auth.read.return_value = json.dumps({"accessToken": "tok"}).encode("utf-8")
        
        mock_progs = MagicMock()
        mock_progs.read.return_value = json.dumps({
            "programs": [{"id": 10, "code": "ZX310", "name": "Cyber Warfare"}]
        }).encode("utf-8")

        mock_urlopen.return_value.__enter__.side_effect = [mock_auth, mock_progs]

        client = api.CyberiumClient(self.cfg)
        progs = client.get_programs()
        self.assertIn("programs", progs)
        self.assertEqual(progs["programs"][0]["code"], "ZX310")

    @patch("urllib.request.urlopen")
    def test_get_book(self, mock_urlopen):
        mock_auth = MagicMock()
        mock_auth.read.return_value = json.dumps({"accessToken": "tok"}).encode("utf-8")

        mock_book = MagicMock()
        mock_book.read.return_value = json.dumps({
            "url": "https://r2.cloudflarestorage.com/cyberium-prod/book.pdf"
        }).encode("utf-8")

        mock_urlopen.return_value.__enter__.side_effect = [mock_auth, mock_book]

        client = api.CyberiumClient(self.cfg)
        res = client.get_book(88)
        self.assertIn("r2.cloudflarestorage.com", res.get("url", ""))

    @patch("urllib.request.urlopen")
    def test_auto_token_refresh_on_401(self, mock_urlopen):
        # 1. Initial auth
        mock_auth1 = MagicMock()
        mock_auth1.read.return_value = json.dumps({"accessToken": "initial_tok"}).encode("utf-8")

        # 2. First call fails with 401
        err_401 = urllib.error.HTTPError("http://url", 401, "Unauthorized", {}, None)

        # 3. Transparent re-auth
        mock_auth2 = MagicMock()
        mock_auth2.read.return_value = json.dumps({"accessToken": "refreshed_tok"}).encode("utf-8")

        # 4. Retried request succeeds
        mock_success = MagicMock()
        mock_success.read.return_value = json.dumps({"questions": []}).encode("utf-8")

        mock_urlopen.return_value.__enter__.side_effect = [mock_auth1, err_401, mock_auth2, mock_success]

        client = api.CyberiumClient(self.cfg)
        res = client.get_questions(88)
        self.assertIn("questions", res)
        self.assertEqual(client.token, "refreshed_tok")

    @patch("urllib.request.urlopen")
    def test_network_offline_recovery(self, mock_urlopen):
        mock_auth = MagicMock()
        mock_auth.read.return_value = json.dumps({"accessToken": "tok"}).encode("utf-8")

        mock_urlopen.return_value.__enter__.side_effect = [mock_auth, urllib.error.URLError("No route to host")]

        client = api.CyberiumClient(self.cfg)
        res = client.get_questions(88)
        self.assertIn("error", res)
        self.assertIn("No route to host", res["error"])


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.cfg = {
            "cookies": {"connect.sid": "mock_sid", "cyb_rt": "mock_rt"},
            "current_program_id": 10,
            "current_module_id": 88,
            "theme": "cyberium"
        }
        self.mock_client = MagicMock()

    def test_cmd_current(self):
        self.mock_client.get_questions.return_value = {
            "module_name": "Post (Linux)",
            "total": 83,
            "answered_count": 14,
            "first_unanswered": 14,
            "questions": [
                {"index": 14, "text": "2.2. Exfiltrate passwd", "answered": False}
            ]
        }
        with patch("builtins.print") as mock_print:
            cli.cmd_current(self.mock_client, self.cfg)
            self.assertTrue(mock_print.called)

    def test_cmd_set_program(self):
        self.mock_client.get_programs.return_value = [
            {"id": 7, "code": "ZX301", "name": "Penetration Testing"},
            {"id": 10, "code": "ZX310", "name": "Cyber Warfare"}
        ]
        self.mock_client.get_modules.return_value = {
            "modules": [{"id": 62, "name": "Recon", "is_open": True, "lab_completed": False}]
        }
        with patch("cyberium.cli.save_config") as mock_save:
            cli.cmd_set_program(self.mock_client, self.cfg, "ZX301")
            self.assertEqual(self.cfg["current_program_id"], 7)
            self.assertEqual(self.cfg["current_module_id"], 62)
            self.assertTrue(mock_save.called)

    def test_cmd_set_program_invalid(self):
        self.mock_client.get_programs.return_value = [
            {"id": 10, "code": "ZX310", "name": "Cyber Warfare"}
        ]
        with patch("builtins.print") as mock_print:
            cli.cmd_set_program(self.mock_client, self.cfg, "INVALID_CODE")
            self.assertTrue(mock_print.called)

    def test_cmd_set_theme(self):
        with patch("cyberium.cli.save_config") as mock_save:
            cli.cmd_set_theme(self.cfg, "dracula")
            self.assertEqual(self.cfg["theme"], "dracula")
            self.assertTrue(mock_save.called)

    def test_cmd_search_special_chars(self):
        self.mock_client.get_questions.return_value = {
            "module_name": "Test",
            "questions": [
                {"index": 1, "text": "Run grep -E '[0-9]+' /etc/passwd", "answered": False},
                {"index": 2, "text": "Run cat *", "answered": True}
            ]
        }
    def test_resolve_question_target(self):
        self.mock_client.get_questions.return_value = {
            "module_name": "Post (Linux)",
            "total": 83,
            "first_unanswered": 14,
            "questions": [
                {"index": 14, "text": "2.2. Exfiltrate passwd", "answered": False},
                {"index": 15, "text": "2.3. Dump shadow", "answered": False}
            ]
        }
        # Resolve None -> active question 14
        idx, q, _ = cli.resolve_question_target(self.mock_client, self.cfg, None)
        self.assertEqual(idx, 14)

        # Resolve section string '2.2' -> question 14
        idx, q, _ = cli.resolve_question_target(self.mock_client, self.cfg, "2.2")
        self.assertEqual(idx, 14)

        # Resolve '#15' -> question 15
        idx, q, _ = cli.resolve_question_target(self.mock_client, self.cfg, "#15")
        self.assertEqual(idx, 15)

    def test_cmd_note_smart_resolution(self):
        self.mock_client.get_questions.return_value = {
            "module_name": "Post (Linux)",
            "total": 83,
            "first_unanswered": 14,
            "questions": [
                {"index": 14, "text": "2.2. Exfiltrate passwd", "answered": False}
            ]
        }
        with patch("cyberium.cli.save_note") as mock_save, patch("builtins.print"):
            # Save by section string
            cli.cmd_note(self.mock_client, self.cfg, ["2.2", "Wget note text"])
            mock_save.assert_called_with(88, 14, "Wget note text")

            # Save without index (to active question)
            cli.cmd_note(self.mock_client, self.cfg, ["Direct active question memo"])
            mock_save.assert_called_with(88, 14, "Direct active question memo")


class TestTUIHelpers(unittest.TestCase):
    def test_safe_addstr_bounds(self):
        mock_win = MagicMock()
        mock_win.getmaxyx.return_value = (24, 80)

        # Normal write within bounds
        tui.safe_addstr(mock_win, 5, 10, "Hello World")
        mock_win.addstr.assert_called_with(5, 10, "Hello World", 0)

        # Coordinate out of bounds
        tui.safe_addstr(mock_win, 25, 10, "Out of bounds")
        tui.safe_addstr(mock_win, -1, 10, "Out of bounds")
        tui.safe_addstr(mock_win, 5, 85, "Out of bounds")

        # Text clipping to max width
        tui.safe_addstr(mock_win, 5, 75, "1234567890")
        mock_win.addstr.assert_called_with(5, 75, "12345", 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
