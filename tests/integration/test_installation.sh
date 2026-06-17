#!/usr/bin/env bash
set -e

echo "=========================================="
echo " TurboWiFi AI - Installation Smoke Tests"
echo "=========================================="

test_commands() {
    local env_name=$1
    echo ">> Running smoke tests for $env_name environment..."
    turbowifi version
    turbowifi doctor
    turbowifi daemon status
    # We use --help for benchmark and watch to avoid actually running long commands in smoke tests
    turbowifi benchmark --help >/dev/null
    turbowifi watch --help >/dev/null
    echo "[OK] $env_name commands executed successfully."
}

echo ">> Scenario C: Editable Installation"
# Use a temporary venv
VENV_DIR=$(mktemp -d)
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install -e .
PATH="$VENV_DIR/bin:$PATH" test_commands "Editable (venv)"
rm -rf "$VENV_DIR"

echo ">> Scenario B: pipx Installation"
if command -v pipx &> /dev/null; then
    pipx install . --force
    # Ensure pipx path is in PATH for this test shell
    export PATH="$HOME/.local/bin:$PATH"
    test_commands "pipx"
else
    echo "[SKIP] pipx not found. Skipping pipx tests."
fi

echo "=========================================="
echo " All installation scenarios PASSED."
echo "=========================================="
