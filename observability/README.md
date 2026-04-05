# Observability stack (quest: view logs and metrics without SSH)

This stack ships **JSON log lines** from the API into **Grafana** via **Promtail → Loki**, and scrapes **`GET /metrics`** with **Prometheus** so you can build dashboards (traffic, errors, process stats) in Grafana.

## Prerequisites

- Docker and Docker Compose on the server (same host as the API, or mount logs over NFS).
- API writing logs to a file: set **`LOG_FILE=/var/log/hackathon/app.log`** (see repo `.env.example`).
- API reachable at **`http://HOST:5000/metrics`** from the host (default scrape target). The Prometheus container uses **`host.docker.internal:5000`** (see `prometheus.yml` and `extra_hosts` in Compose) to reach the API on the same machine.

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

## Start Loki / Promtail / Prometheus / Grafana

```bash
cd observability
docker compose up -d
```

- **Grafana:** `http://SERVER_IP:3000` — login `admin` / `admin` (change on first login), or use anonymous (enabled for demo).
- **Explore → Loki** — try: `{job="hackathon"}` or `{service="api"}`.
- **Explore → Prometheus** — try: `http_requests_total`, `http_errors_total`, `process_cpu_seconds_total`.
- **Prometheus UI:** `http://SERVER_IP:9090` — **Status → Targets** should show `hackathon-api` as **UP** if the API is listening on the host at port 5000.
- **Promtail** tails `/var/log/hackathon/*.log` inside the container (host path mounted read-only).

### Scrape target (same host vs HTTPS)

- **API on the same host as Docker, port 5000:** default `prometheus.yml` is enough; ensure Flask binds to `0.0.0.0:5000` (not only `127.0.0.1`) if the scrape fails.
- **Public HTTPS only:** edit `prometheus.yml` and use `scheme: https` and `targets: ['your.domain']` with `metrics_path: /metrics` (see comments at the top of that file).

## Stop

```bash
docker compose down
```

## Security note

Anonymous Grafana admin is convenient for a hackathon demo. For a real deployment, disable anonymous auth, use strong passwords, and restrict ports **3000** / **3100** / **9090** with a firewall or VPN.
