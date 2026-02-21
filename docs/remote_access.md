# Remote Access Options

The service runs on port 8000. To call it from a machine on a different network, choose one
of the following approaches.

---

## Option 1: Direct Port (Recommended for simplicity)

Bind the service to `0.0.0.0:8000` (already the case) and open the port in UFW:

```bash
sudo ufw allow 8000/tcp
```

Then call from any machine:

```bash
curl http://<public-ip>:8000/health
```

**Pros:** Zero dependencies, lowest latency, no upload size limit.
**Cons:** Requires the ISP/router to allow inbound connections on port 8000. Check that the
machine has a static or stable public IP. No TLS unless you add a reverse proxy (nginx/caddy).

To find the public IP: `curl -s https://ifconfig.me`

---

## Option 2: Cloudflare Tunnel

Add `cloudflared` as a second Docker Compose service. Works behind NAT, provides HTTPS, free.

```yaml
services:
  cloudflared:
    image: cloudflare/cloudflared:latest
    command: tunnel --no-autoupdate run --token ${CLOUDFLARE_TUNNEL_TOKEN}
    restart: unless-stopped
```

**Pros:** Works behind NAT, free, HTTPS out of the box, stable URL.
**Cons:** **100MB request body limit** imposed by Cloudflare — unsuitable for large audio files.
Requires a Cloudflare account and tunnel setup.

---

## Option 3: Tailscale (Most Secure)

Install Tailscale on both the server and every client machine. All traffic goes through the
Tailscale mesh VPN; no public port needed.

```bash
# On server
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

**Pros:** End-to-end encrypted, no public exposure, stable `*.ts.net` hostname.
**Cons:** Requires Tailscale installed on every client machine.

---

## Option 4: ngrok

```bash
ngrok http 8000
```

**Pros:** Instant setup, HTTPS.
**Cons:** Free tier has bandwidth limits and rotating URLs (paid tier for stable URLs).

---

## Recommendation

For a home/lab server with a public IP: **Option 1** (direct port). If behind NAT and audio
files stay under 100MB: **Option 2** (Cloudflare Tunnel). For multi-machine team access:
**Option 3** (Tailscale).
