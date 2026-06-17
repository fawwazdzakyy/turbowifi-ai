#!/usr/bin/env bash
set -e

echo "======================================"
echo "  TurboWiFi AI - Termux Installer"
echo "======================================"

echo ">> Updating packages..."
pkg update -y

echo ">> Checking dependencies..."
if ! command -v python &> /dev/null; then
    echo "[!] Python is not installed. Installing..."
    pkg install -y python dnsutils
fi

echo ">> Creating virtual environment..."
VENV_DIR="$HOME/.turbowifi/venv"
mkdir -p "$HOME/.turbowifi"
if [ ! -d "$VENV_DIR" ]; then
    python -m venv "$VENV_DIR"
fi

echo ">> Installing TurboWiFi AI..."
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install .

echo ">> Configuring wrapper..."
WRAPPER="$PREFIX/bin/turbowifi"
cat > "$WRAPPER" <<EOF
#!/usr/bin/env bash
exec $VENV_DIR/bin/turbowifi "\$@"
EOF
chmod +x "$WRAPPER"

echo "======================================"
echo "Installation complete!"
echo "Run 'turbowifi doctor' to verify setup."
echo "Note: Some features require a rooted device."
echo "======================================"
