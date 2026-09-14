#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SHORTCUT_DIR="$HOME/.shortcuts"
mkdir -p "$SHORTCUT_DIR"

cat > "$SHORTCUT_DIR/LOOM_Qualify.sh" <<EOF
#!/data/data/com.termux/files/usr/bin/bash
exec bash "$REPO_ROOT/engineering/pixel/loom_pixel_run.sh"
EOF

cat > "$SHORTCUT_DIR/LOOM_Qualify_AI.sh" <<EOF
#!/data/data/com.termux/files/usr/bin/bash
exec bash "$REPO_ROOT/engineering/pixel/loom_pixel_run_assisted.sh"
EOF

chmod +x "$SHORTCUT_DIR/LOOM_Qualify.sh" "$SHORTCUT_DIR/LOOM_Qualify_AI.sh"

echo "Installed Termux shortcuts:"
echo "  LOOM_Qualify.sh     -> raw governed qualification"
echo "  LOOM_Qualify_AI.sh  -> governed qualification + bounded local mechanical repair on failure"
