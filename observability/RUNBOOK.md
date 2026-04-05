# Hackathon App — Incident Runbook

## Overview
This runbook describes how to respond to alerts fired by the Hackathon monitoring stack.
Grafana Dashboard: http://143.198.39.134:3000
Application URL: https://url.foundre.app

---

## Alert: Service Down

### What it means
The Flask app has not responded to a health check in the last 5 minutes.

### Impact
All API endpoints are unavailable. Users cannot create or access URLs.

### Steps
1. Check if the service is running:
   ```bash
   ssh deploy@143.198.39.134
   sudo systemctl status hackathon
   ```

2. If stopped, restart it:
   ```bash
   sudo systemctl start hackathon
   ```

3. Verify it's back up:
   ```bash
   curl https://url.foundre.app/health
   ```

4. Check logs for the cause:
   ```bash
   sudo journalctl -u hackathon -n 50
   ```

5. If it won't start, check if the database is running:
   ```bash
   docker ps | grep hackathon-pg
   docker start hackathon-pg  # if stopped
   ```

---

## Alert: High Error Rate

### What it means
More than 5 HTTP 5xx errors have occurred in the last 5 minutes.

### Impact
Some requests are failing. Users may be seeing errors.

### Steps
1. Check the Grafana dashboard for which endpoints are erroring:
   - Open `Error Rate` panel
   - Look for spikes in the graph

2. Check logs in Grafana:
   - Go to Explore → Loki
   - Query: `{job="hackathon"} |= "error"`

3. SSH in and check recent logs:
   ```bash
   tail -f /var/log/hackathon/app.log
   ```

4. Check if the database is responding:
   ```bash
   docker exec -it hackathon-pg psql -U postgres -d hackathon_db -c "SELECT 1"
   ```

5. If a bad deployment caused it, roll back:
   ```bash
   cd /home/deploy/PE-Hackathon-2026
   git log --oneline -5  # find the last good commit
   git checkout <commit-hash>
   sudo systemctl restart hackathon
   ```

---

## General Health Check
```bash
# App status
sudo systemctl status hackathon

# Database status
docker ps | grep hackathon-pg

# Caddy status
sudo systemctl status caddy

# Recent logs
tail -f /var/log/hackathon/app.log
```