#!/usr/bin/env bash
#
# Cyberium CLI & TUI Installer
# Installs 'cyberium' and 'cyberium-tui' into ~/.local/bin or /usr/local/bin
#

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${HOME}/.local/bin"

mkdir -p "$TARGET_DIR"

echo "[*] Installing cyberium CLI & TUI suite..."

if [ "$EUID" -eq 0 ]; then
    TARGET_DIR="/usr/local/bin"
fi

ln -sfn "${DIR}/bin/cyberium" "${TARGET_DIR}/cyberium"
ln -sfn "${DIR}/bin/cyberium-tui" "${TARGET_DIR}/cyberium-tui"
chmod +x "${DIR}/bin/cyberium" "${DIR}/bin/cyberium-tui"

# Shell completions
BASH_COMP_DIR="${HOME}/.local/share/bash-completion/completions"
if [ -d "$BASH_COMP_DIR" ] || mkdir -p "$BASH_COMP_DIR" 2>/dev/null; then
    cp -f "${DIR}/completions/cyberium.bash" "${BASH_COMP_DIR}/cyberium" 2>/dev/null || true
fi

ZSH_COMP_DIR="${HOME}/.zfunc"
if [ -d "$ZSH_COMP_DIR" ] || [ -d "${HOME}/.zsh/completion" ]; then
    mkdir -p "${HOME}/.zfunc" 2>/dev/null || true
    cp -f "${DIR}/completions/_cyberium" "${HOME}/.zfunc/_cyberium" 2>/dev/null || true
fi

echo "[✓] Successfully installed binaries to ${TARGET_DIR}/"
echo "    • cyberium      (Terminal Client & Submission Tool)"
echo "    • cyberium-tui  (Full-Screen Terminal Dashboard)"
echo ""
echo "Try running: cyberium"
