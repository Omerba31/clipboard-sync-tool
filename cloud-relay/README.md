# Cloud Relay Server

Node.js relay server for clipboard sync between desktop and mobile devices.

## Deploy to Railway.app

**Free tier:** $5 credit/month (~500 hours)

### Option 1: CLI (Recommended)

```bash
# Windows
.\deploy.ps1

# Mac/Linux
chmod +x deploy.sh && ./deploy.sh
```

### Option 2: Web Dashboard

1. **Go to** https://railway.app/new
2. **Click** "Deploy from GitHub repo"
3. **Select** `clipboard-sync-tool` repository
4. **Set Root Directory** to `cloud-relay` (Settings → Service)
5. **Generate Domain** (Settings → Domains)

Your URL: `https://your-app.up.railway.app`

### Test

```bash
curl https://your-app.up.railway.app/health
```

---

## Usage

### Desktop App
1. Click **☁️ Cloud Relay**
2. Enter your Railway URL
3. Enter Room ID (e.g., `my-room`)
4. Connect

### Mobile
1. Open Railway URL in browser
2. Enter same Room ID
3. Connect

---

## Limits (Built-in Protection)

| Limit | Value | Purpose |
|-------|-------|---------|
| Bandwidth | 150MB/month | Stay in free tier |
| Rate | 60 msg/min | Prevent spam |
| Connections | 50 devices | Resource limit |
| Message size | 100KB | Memory limit |

Check usage: `GET /stats`

---

## Security

⚠️ **Base64 encoding only** (not encrypted)

- Use unique Room IDs
- Don't sync passwords or sensitive data
- For sensitive data, use Local P2P mode (end-to-end encrypted)

---

## Local Development

```bash
cd cloud-relay
npm install
node server.js
# Opens on http://localhost:3000
```

---

## API

| Endpoint | Description |
|----------|-------------|
| `GET /` | Mobile web app |
| `GET /health` | Health check |
| `GET /stats` | Usage statistics |

### Socket.IO Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `join_room` | Client → Server | Join sync room |
| `clipboard_data` | Both | Sync clipboard content |
| `device_list` | Server → Client | Connected devices |
