# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- (move items here while developing; cut a dated section when you tag a release)

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
