# Panduan Instalasi Eka Dashboard

Panduan ini untuk menjalankan Eka Dashboard dari GitHub di Ubuntu Server/Debian.

## 1. Persiapan

```bash
sudo apt-get update
sudo apt-get install -y git docker.io docker-compose-plugin
sudo systemctl enable --now docker
```

Opsional, agar user non-root bisa menjalankan Docker:

```bash
sudo usermod -aG docker $USER
```

Logout dan login ulang setelah menjalankan perintah di atas.

## 2. Clone Repository

```bash
git clone https://github.com/<USERNAME>/<REPO>.git homeserver-dashboard
cd homeserver-dashboard
```

Ganti `<USERNAME>/<REPO>` dengan repo GitHub yang nanti dipakai.

## 3. Buat `.env`

```bash
cp .env.example .env
nano .env
```

Minimal isi:

```env
SECRET_KEY=isi-dengan-random-secret-panjang
DASHBOARD_BIND=127.0.0.1
DASHBOARD_PORT=8080
ALLOWED_ORIGINS=http://127.0.0.1:8080,http://localhost:8080
```

Untuk akses dari LAN:

```env
DASHBOARD_BIND=0.0.0.0
DASHBOARD_PORT=8080
ALLOWED_ORIGINS=http://IP_SERVER:8080
```

## 4. Jalankan Safe Mode

```bash
docker compose up -d --build
```

Buka:

```text
http://127.0.0.1:8080
```

Safe Mode cocok untuk setup awal dan monitoring dasar. Fitur Docker manager, terminal host, file manager host, WireGuard, dan LXD belum aktif.

## 5. Jalankan Host Control Mode

Jika butuh kontrol penuh host:

```bash
docker compose -f docker-compose.yml -f docker-compose.host-control.yml up -d --build
```

Mode ini memberi container akses kuat ke host. Gunakan hanya di server pribadi yang diakses lewat LAN/VPN.

## 6. Login Pertama

Saat pertama dibuka, dashboard akan menampilkan setup admin. Buat username dan password baru. Setelah itu buka halaman Health untuk memastikan mode dan capability yang aktif.

## 7. Stack Homeserver

Template App Store sudah menyiapkan:

- Caddy
- Nginx Proxy Manager
- Tailscale
- Uptime Kuma
- Jellyfin
- Immich Server
- Immich Postgres
- Immich Redis
- Immich Machine Learning

Immich sebaiknya nanti dijalankan sebagai stack/compose group agar server, database, Redis, dan machine learning berada di network yang sama.

## 8. Folder Data yang Disarankan

```bash
sudo mkdir -p /mnt/photos/immich
sudo mkdir -p /mnt/media
sudo mkdir -p /mnt/backups
sudo mkdir -p /opt/homeserver/www
sudo mkdir -p /opt/homeserver
```

Sesuaikan owner sesuai user server:

```bash
sudo chown -R $USER:$USER /mnt/photos /mnt/media /mnt/backups /opt/homeserver
```

## 9. Update

Safe Mode:

```bash
git pull
docker compose up -d --build
```

Host Control Mode:

```bash
git pull
docker compose -f docker-compose.yml -f docker-compose.host-control.yml up -d --build
```

## 10. Troubleshooting

Cek log:

```bash
docker compose logs -f
```

Reset admin setup:

```bash
rm -f data/security_config.json
docker compose restart
```

Jika halaman dari perangkat lain tidak bisa dibuka, pastikan:

- `DASHBOARD_BIND=0.0.0.0`
- firewall mengizinkan port `DASHBOARD_PORT`
- `ALLOWED_ORIGINS` berisi URL yang dipakai browser
