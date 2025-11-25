# Cloud Relay Server

Node.js relay server for clipboard sync between desktop and mobile devices.

## Deploy to Railway.app

**Free tier:** $5 credit/month (~500 hours)

### Quick Deploy

```bash
# Windows
.\scripts\deploy.ps1

# Mac/Linux
chmod +x scripts/deploy.sh && ./scripts/deploy.sh
```

See [main README](../README.md#deploy-your-own-cloud-relay) for web dashboard instructions.

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
4. Enter Password (optional, for extra security)
5. Connect

### Mobile
1. Open Railway URL in browser
2. Enter same Room ID
3. Enter same Password (if used)
4. Connect

⚠️ **Both devices must use the same Room ID + Password to decrypt each other's messages.**

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

✅ **End-to-End Encrypted (AES-256-GCM)**

- All data is encrypted client-side before sending
- Server only relays encrypted blobs - cannot read your content
- Encryption key derived from Room ID + optional password
- Add a password in the connection dialog for extra security

**How it works:**
1. Key derived from Room ID + password using PBKDF2 (100,000 iterations)
2. Each message encrypted with AES-256-GCM + random IV
3. Server passes encrypted data without decryption

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
