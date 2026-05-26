# maeng Dashboard

Dashboard pribadi untuk monitor dan kontrol homeserver berbasis Docker. Target utama proyek ini adalah laptop/mini PC/STB yang menjalankan Ubuntu Server atau Debian di jaringan pribadi.

## Status

Proyek masih tahap build/beta. Pakai untuk lab dan homeserver pribadi dulu sebelum dibuka ke jaringan yang lebih luas.

## Fitur Utama

- Dashboard metrics CPU, RAM, disk, network, uptime.
- Health Check untuk melihat `Safe Mode` vs `Host Control Mode`.
- App Store template untuk Caddy, Nginx Proxy Manager, Tailscale, Uptime Kuma, Jellyfin, dan Immich.
- Storage Planner untuk folder `/mnt/photos/immich`, `/mnt/media`, `/opt/homeserver`, `/opt/homeserver/www`, dan `/mnt/backups`.
- Security page untuk password, role, session, dan audit log.
- Optional host-control untuk Docker manager, terminal host, file manager host, WireGuard, dan LXD.

## Mode Jalan

### Safe Mode

Mode default. Container tidak mendapat Docker socket, root filesystem host, PID host, atau privileged access.

```bash
docker compose up -d --build
```

Gunakan mode ini untuk dashboard monitoring dasar, setup awal, dan testing lokal.

### Host Control Mode

Mode ini memberi akses kuat ke host untuk fitur Docker manager, terminal host, file manager host, WireGuard, dan LXD.

```bash
docker compose -f docker-compose.yml -f docker-compose.host-control.yml up -d --build
```

Aktifkan hanya di server pribadi yang diakses lewat LAN/VPN, bukan internet publik.

## Install dari GitHub

```bash
sudo apt-get update
sudo apt-get install -y git docker.io docker-compose-plugin

git clone https://github.com/<USERNAME>/<REPO>.git homeserver-dashboard
cd homeserver-dashboard

cp .env.example .env
nano .env

docker compose up -d --build
```

Buka lokal:

```text
http://127.0.0.1:8080
```

Untuk akses dari perangkat lain di LAN, ubah `.env`:

```env
DASHBOARD_BIND=0.0.0.0
DASHBOARD_PORT=8080
ALLOWED_ORIGINS=http://IP_SERVER:8080
```

Lalu restart:

```bash
docker compose up -d
```

## Stack Homeserver yang Disiapkan

- Dashboard ini: monitor/control.
- Docker Compose: semua app.
- Caddy atau Nginx Proxy Manager: domain/reverse proxy.
- Tailscale: akses aman dari luar rumah.
- Immich: foto dan video backup.
- Jellyfin: media server pribadi.
- Uptime Kuma: monitoring service.

## Folder yang Disarankan

```text
/mnt/photos/immich      # Foto/video Immich
/mnt/media              # Film/series/music Jellyfin
/opt/homeserver         # Config dan data app kecil
/opt/homeserver/www     # Website files
/mnt/backups            # Backup config/database
```

## Keamanan

- Wajib set `SECRET_KEY` di `.env`.
- Jangan commit `.env` atau folder `data/`.
- Jangan expose dashboard langsung ke internet.
- Pakai Tailscale/WireGuard atau reverse proxy dengan HTTPS.
- Ganti password admin setelah setup pertama.

## Update

```bash
git pull
docker compose up -d --build
```

Untuk Host Control Mode:

```bash
git pull
docker compose -f docker-compose.yml -f docker-compose.host-control.yml up -d --build
```

## Catatan Lisensi

Copyright 2026. Semua hak cipta dilindungi. Jika repo dibuat publik, tentukan lisensi resmi sebelum menerima kontribusi atau penggunaan ulang oleh pihak lain.
