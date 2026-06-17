#!/usr/bin/env bash
set -e

echo "======================================"
echo "  TurboWiFi AI - Ubuntu Installer"
echo "======================================"

if [[ "$EUID" -eq 0 ]]; then
  echo "[!] Please do not run this script as root. pipx should be run as a normal user."
  exit 1
fi

echo ">> Checking dependencies..."
if ! command -v pipx &> /dev/null; then
    echo "[!] pipx is not installed. Installing via apt..."
    sudo apt update && sudo apt install -y pipx
fi

echo ">> Ensuring pipx is in PATH..."
pipx ensurepath

echo ">> Installing TurboWiFi AI via pipx..."
# Use pipx install with --force to make it idempotent
pipx install . --force

echo "======================================"
echo "Installation complete!"
echo "Please restart your terminal or run 'source ~/.bashrc' if this is your first time using pipx."
echo "Run 'turbowifi doctor' to verify setup."
echo "======================================"
