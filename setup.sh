#!/bin/bash
# Carga las claves como secrets del repo SIN mostrarlas. Correr una vez: ./setup.sh
set -e
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
ask(){ read -r -s -p "$1 (Enter para saltear): " v; echo; if [ -n "$v" ]; then printf '%s' "$v" | gh secret set "$2" --repo "$REPO" && echo "  ✓ $2 guardado"; fi; }
ask "PEXELS_API_KEY (pexels.com/api)" PEXELS_API_KEY
ask "META_PAGE_TOKEN (token de la página, largo plazo)" META_PAGE_TOKEN
ask "FB_PAGE_ID (id de la página de Facebook)" FB_PAGE_ID
ask "IG_USER_ID (id de la cuenta de Instagram profesional)" IG_USER_ID
ask "TIKTOK_ACCESS_TOKEN (opcional, experimental)" TIKTOK_ACCESS_TOKEN
echo "Listo. Probá: gh workflow run 'Video diario' -f slot=almuerzo -f dry_run=true"
