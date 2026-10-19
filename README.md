<p align="center">
  <img src="assets/hero_banner.svg" width="100%" alt="Cyberium CLI — Pure Python 3 Stdlib Headless Cybersecurity Learning Platform Client &amp; Curses TUI" />
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Language-Python_3_Stdlib-38bdf8?style=for-the-badge&amp;logo=python&amp;logoColor=white&amp;labelColor=06090e" alt="Language" /></a>
  <a href="cyberium/tui.py"><img src="https://img.shields.io/badge/Interface-Curses_TUI_%2B_CLI-10b981?style=for-the-badge&amp;logo=gnubash&amp;logoColor=white&amp;labelColor=06090e" alt="Interface" /></a>
  <a href="cyberium/config.py"><img src="https://img.shields.io/badge/Auth_Sync-SQLite_Cookie_Harvest-d4a359?style=for-the-badge&amp;logo=sqlite&amp;logoColor=white&amp;labelColor=06090e" alt="Auth Engine" /></a>
  <a href="docs/Cyberium_CLI_POC_Denis_Albin.pdf"><img src="https://img.shields.io/badge/Capstone_Dossier-PDF_(8_Pages)-56d364?style=for-the-badge&amp;logo=readthedocs&amp;logoColor=white&amp;labelColor=06090e" alt="Capstone Dossier" /></a>
</p>

<p align="center">
  <img src="assets/pipeline.svg" width="100%" alt="Cyberium CLI Four-Stage Platform Client Architecture" />
</p>

<p align="center">
  <img src="assets/sec_1_capabilities.svg" width="100%" alt="I · Architectural Capabilities &amp; Core" />
  <img src="assets/panel_1_capabilities.svg" width="100%" alt="Cyberium CLI Core Architectural Capabilities" />
</p>

<p align="center">
  <img src="assets/sec_2_modules.svg" width="100%" alt="II · Command Dispatch Matrix &amp; TUI Controls" />
  <img src="assets/panel_2_modules.svg" width="100%" alt="Cyberium CLI Command Dispatch Matrix &amp; TUI Controls" />
</p>

<p align="center">
  <img src="assets/sec_3_walkthrough.svg" width="100%" alt="III · Capstone Evidence &amp; POC Gallery" />
  <a href="docs/Cyberium_CLI_POC_Denis_Albin.pdf" title="Open Cyberium CLI Official Capstone Dossier (8-Page PDF)"><img src="assets/evidence/poc_plate_1_auth_and_tui.png" width="100%" alt="Cyberium CLI Execution Evidence Plate I — Browser Session Harvest, Full-Screen Curses TUI Navigator &amp; Sub-Second Flag Solve (Cyberium_CLI_POC_Denis_Albin.pdf Figures 1, 5, 6)" /></a>
  <a href="docs/Cyberium_CLI_POC_Denis_Albin.pdf" title="Open Cyberium CLI Official Capstone Dossier (8-Page PDF)"><img src="assets/evidence/poc_plate_2_cli_streaming_and_notes.png" width="100%" alt="Cyberium CLI Execution Evidence Plate II — POSIX Command Tree, Cloudflare R2 Textbook Streaming, Live Metasploitable 2 Recon &amp; Scratchpad Notes (Cyberium_CLI_POC_Denis_Albin.pdf Figures 2, 3, 4, 7)" /></a>
</p>

<p align="center">
  <img src="assets/sec_4_execution.svg" width="100%" alt="IV · Deployment, Runtime &amp; Persistence" />
</p>

```bash
git clone https://github.com/ArtistS24/cyberium-cli.git
cd cyberium-cli

# Run zero-dependency automated installer (links binary to ~/.local/bin/cyberium)
./install.sh

# Verify comprehensive standard-library test suite (37 automated unit tests)
python3 -m unittest discover tests

# Launch full-screen interactive curses TUI dashboard
cyberium tui
```

<p align="center">
  <img src="assets/panel_3_workspace.svg" width="100%" alt="Client Config, Cache Persistence &amp; Stdlib Test Harness Matrix" />
</p>

```toml
[instant_lab_submission]
# Submit active lab objective flag directly from CLI without launching TUI
command = "cyberium submit 'FLAG{memory_carved_vad_svchost}'"

# Submit specific question index across any enrolled track
target  = "cyberium submit -i 14 'FLAG{auditd_rule_triggered}'"
```

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Runtime-Python_3.8%2B_Stdlib-0d131c?style=flat-square&amp;logo=python&amp;logoColor=38bdf8&amp;labelColor=06090e" alt="Python" /></a>
  <a href="https://docs.python.org/3/library/curses.html"><img src="https://img.shields.io/badge/Interface-POSIX_Curses-0d131c?style=flat-square&amp;logo=gnubash&amp;logoColor=10b981&amp;labelColor=06090e" alt="Curses" /></a>
  <a href="https://sqlite.org/"><img src="https://img.shields.io/badge/Session_Sync-SQLite3-0d131c?style=flat-square&amp;logo=sqlite&amp;logoColor=d4a359&amp;labelColor=06090e" alt="SQLite" /></a>
  <a href="https://www.cloudflare.com/"><img src="https://img.shields.io/badge/Delivery-Cloudflare_R2-0d131c?style=flat-square&amp;logo=cloudflare&amp;logoColor=f59e0b&amp;labelColor=06090e" alt="Cloudflare" /></a>
  <a href="https://www.mozilla.org/firefox/"><img src="https://img.shields.io/badge/Browser_Jar-Gecko_moz__cookies-0d131c?style=flat-square&amp;logo=firefox&amp;logoColor=ff7139&amp;labelColor=06090e" alt="Mozilla" /></a>
</p>

```toml
[academic_attribution]
engineer    = "Denis Albin"
handle      = "@ArtistS24"
role        = "Security Researcher & Tooling Engineer"
institution = "John Bryce Academy // Division RTX2026"
status      = "Officially Submitted Capstone Research Project"
dossier     = "docs/Cyberium_CLI_POC_Denis_Albin.pdf (8 Pages, 2.8 MB)"

[disclaimer]
notice = "Unofficial open-source client developed independently for educational purposes. Not affiliated with, sponsored by, or endorsed by Cyberium Academy or John Bryce Academy. All trademarks belong to their respective owners."
```
