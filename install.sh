#!/usr/bin/env bash
#
# Cyberium CLI Installer
# Installs 'cyberium' into ~/.local/bin or /usr/local/bin
#

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${HOME}/.local/bin"

mkdir -p "$TARGET_DIR"

echo "[*] Installing cyberium CLI..."

# If running as root or with sudo access, offer /usr/local/bin
if [ "$EUID" -eq 0 ]; then
    TARGET_DIR="/usr/local/bin"
fi

ln -sfn "${DIR}/bin/cyberium" "${TARGET_DIR}/cyberium"
chmod +x "${DIR}/bin/cyberium"

echo "[✓] Successfully installed to ${TARGET_DIR}/cyberium"
echo ""
echo "Try running: cyberium"
EOF && chmod +x /home/artist/Projects/cyberium-cli/install.sh
