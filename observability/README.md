# Observability stack (quest: view logs without SSH)

This stack ships **JSON log lines** from the API into **Grafana** via **Promtail → Loki**.

## Prerequisites

- Docker and Docker Compose on the server (same host as the API, or mount logs over NFS).
- API writing logs to a file: set **`LOG_FILE=/var/log/hackathon/app.log`** (see repo `.env.example`).

## Server setup

```bash
sudo mkdir -p /var/log/hackathon
sudo chown YOUR_SERVICE_USER:YOUR_SERVICE_USER /var/log/hackathon
```

Add to the environment for your **`hackathon`** systemd unit (or `.env`):

```bash
LOG_FILE=/var/log/hackathon/app.log
```

Restart the API so it creates `app.log`.

## Start Loki / Promtail / Grafana

```bash
cd observability
docker compose up -d
```

- **Grafana:** `http://SERVER_IP:3000` — login `admin` / `admin` (change on first login), or use anonymous (enabled for demo).
- **Explore → Loki** — try: `{job="hackathon"}` or `{service="api"}`.
- **Promtail** tails `/var/log/hackathon/*.log` inside the container (host path mounted read-only).

## Stop

```bash
docker compose down
```

## Security note

Anonymous Grafana admin is convenient for a hackathon demo. For a real deployment, disable anonymous auth, use strong passwords, and restrict ports **3000** / **3100** with a firewall or VPN.
