# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **CI/CD:** GitHub Actions workflow [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) — on push to `main`, SSH into a DigitalOcean Droplet, `git pull`, `uv sync`, and restart the `hackathon` systemd service
- **README:** setup with `uv`, clone URL (`github.com/samokw/PE-Hackathon-2026`), Docker PostgreSQL (ports and `.env`), mermaid App→PostgreSQL diagram, API endpoint tables, and **view logs without SSH** (Loki / Grafana) overview
- **Structured logging:** `structlog` JSON lines to stdout; per-request `http_request` (method, path, status, duration) and `http_request_error` on exceptions; domain events in routes, `app/seed.py`, `app/database.py`, and `run.py`
- **`GET /metrics`:** Prometheus text format via `prometheus_client` (default registry + `http_requests_total`, `http_errors_total`)
- **Observability stack:** optional `LOG_FILE` env duplicates JSON logs to a file for **Promtail → Loki → Grafana**; [`observability/`](observability/) Docker Compose, Loki/Promtail configs, Grafana Loki datasource provisioning, and [`observability/README.md`](observability/README.md)

### Changed

- **`run.py`:** `db.create_tables([User, Url, UrlEvent], safe=True)` so restarts do not fail on existing tables; single `create_app()` before `create_tables` and `app.run()`
- **`.env.example`:** document optional `LOG_FILE` for log shipping

## [0.1.0] - 2026-04-03

### Added

- Flask app with `GET /health` (`{"status": "ok"}`)
- Users: `POST /users/bulk` (CSV via `load_csv`), `GET /users` (optional query params `page` and `per_page`), `GET` / `POST` / `PUT` / `DELETE /users/<id>`
- URLs: `POST` / `GET` / `PUT` / `DELETE /urls/<id>`, `GET /urls/<short_code>/redirect`, `GET /urls` with `user_id` and `is_active` query filters
- Events: `GET /events`, `POST /events`
- Shared JSON serializers in `app/routes/helpers.py` (`user_to_dict`, `url_to_dict`, `event_to_dict`)

<!-- Optional: add compare/release links at the bottom when the repo is public, e.g.
[Unreleased]: https://github.com/OWNER/REPO/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/OWNER/REPO/releases/tag/v0.1.0
-->
