#!/usr/bin/env bash
set -e

echo "======================================"
echo "  TurboWiFi AI - Uninstaller"
echo "======================================"

echo ">> Stopping Daemon..."
if command -v turbowifi &> /dev/null; then
    turbowifi daemon stop || true
fi

echo ">> Removing binaries..."
if [ -f "/usr/local/bin/turbowifi" ]; then
    sudo rm "/usr/local/bin/turbowifi"
fi

if command -v pip &> /dev/null; then
    pip uninstall -y turbowifi-ai || true
fi

echo ">> Cleaning up environment..."
rm -rf "$HOME/.turbowifi"
rm -rf "$HOME/.local/share/turbowifi"

echo "======================================"
echo "TurboWiFi AI has been successfully uninstalled."
echo "======================================"
