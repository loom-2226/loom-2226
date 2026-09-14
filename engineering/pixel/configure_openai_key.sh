#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

CONFIG_DIR="$HOME/.config/loom"
ENV_FILE="$CONFIG_DIR/openai.env"
mkdir -p "$CONFIG_DIR"
chmod 700 "$CONFIG_DIR"

printf 'Paste OpenAI API key (input hidden): '
IFS= read -r -s KEY
printf '\n'
if [[ -z "$KEY" ]]; then
  echo "No key entered; nothing changed." >&2
  exit 2
fi

{
  printf 'export OPENAI_API_KEY=%q\n' "$KEY"
  printf 'export LOOM_REPAIR_MODEL=%q\n' "gpt-5.6-terra"
} > "$ENV_FILE"
chmod 600 "$ENV_FILE"
unset KEY

echo "Saved local-only API configuration to $ENV_FILE"
echo "Permissions: $(stat -c '%a' "$ENV_FILE" 2>/dev/null || echo 600)"
echo "Model: gpt-5.6-terra"
echo "The key was not written to the repository or shortcut scripts."
