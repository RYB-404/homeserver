#!/usr/bin/env bash
set -euo pipefail

APP_NAME="Eka Dashboard"
ENV_FILE=".env"

info() { printf "\033[1;34m[INFO]\033[0m %s\n" "$1"; }
ok() { printf "\033[1;32m[OK]\033[0m %s\n" "$1"; }
warn() { printf "\033[1;33m[WARN]\033[0m %s\n" "$1"; }
fail() { printf "\033[1;31m[ERROR]\033[0m %s\n" "$1"; exit 1; }

if [ "$(id -u)" -ne 0 ]; then
  warn "Installer tidak harus root, tapi user ini perlu akses Docker."
fi

if ! command -v docker >/dev/null 2>&1; then
  info "Docker belum terpasang. Menginstall Docker dari repo OS..."
  apt-get update
  apt-get install -y docker.io docker-compose-plugin
  systemctl enable --now docker || true
fi

if docker compose version >/dev/null 2>&1; then
  COMPOSE=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE=(docker-compose)
else
  fail "Docker Compose tidak ditemukan. Install docker-compose-plugin terlebih dahulu."
fi

if [ ! -f "$ENV_FILE" ]; then
  if [ -f ".env.example" ]; then
    cp .env.example "$ENV_FILE"
  else
    cat > "$ENV_FILE" <<'EOF'
SECRET_KEY=change-this-to-a-long-random-secret
DASHBOARD_BIND=127.0.0.1
DASHBOARD_PORT=8080
ALLOWED_ORIGINS=http://127.0.0.1:8080,http://localhost:8080
EOF
  fi

  SECRET="$(python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
)"
  sed -i "s|^SECRET_KEY=.*|SECRET_KEY=${SECRET}|" "$ENV_FILE"
  ok "File .env dibuat dengan SECRET_KEY acak."
else
  ok "File .env sudah ada."
fi

mkdir -p data

MODE="${1:-safe}"
if [ "$MODE" = "host-control" ]; then
  warn "Menjalankan Host Control Mode. Mode ini memberi akses kuat ke host."
  "${COMPOSE[@]}" -f docker-compose.yml -f docker-compose.host-control.yml up -d --build
else
  info "Menjalankan Safe Mode."
  "${COMPOSE[@]}" up -d --build
fi

PORT="$(grep '^DASHBOARD_PORT=' "$ENV_FILE" | cut -d= -f2- || true)"
BIND="$(grep '^DASHBOARD_BIND=' "$ENV_FILE" | cut -d= -f2- || true)"
PORT="${PORT:-8080}"
BIND="${BIND:-127.0.0.1}"

ok "$APP_NAME berjalan."
info "Akses lokal: http://127.0.0.1:${PORT}"
if [ "$BIND" = "0.0.0.0" ]; then
  IP_ADDR="$(hostname -I 2>/dev/null | awk '{print $1}' || true)"
  if [ -n "${IP_ADDR:-}" ]; then
    info "Akses LAN: http://${IP_ADDR}:${PORT}"
  fi
fi

info "Cek log: ${COMPOSE[*]} logs -f"
