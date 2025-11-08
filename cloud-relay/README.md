# Cloud Relay Deployment Guide

## 🚀 Deploy to Fly.io (FREE)

### Prerequisites
1. **Create Fly.io account:** https://fly.io/app/sign-up
2. **Install Fly CLI:**
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   
   # Mac/Linux
   curl -L https://fly.io/install.sh | sh
   ```

3. **Login to Fly.io:**
   ```bash
   fly auth login
   ```

### Step 1: Deploy the Relay Server

```bash
# Navigate to cloud-relay directory
cd cloud-relay

# Deploy to Fly.io (first time)
fly launch

# When prompted:
# - App name: clipboard-sync-relay (or your choice)
# - Region: Choose closest to you
# - PostgreSQL: No
# - Redis: No

# Deploy
fly deploy

# Check status
fly status

# View logs
fly logs
```

### Step 2: Get Your Server URL

After deployment, your server will be at:
```
https://clipboard-sync-relay.fly.dev
```

Test it:
```bash
curl https://clipboard-sync-relay.fly.dev/health
```

### Step 3: Update Desktop App

Add cloud relay support to your desktop app (instructions below).

### Step 4: Use Mobile Web App

Open on your iPhone:
```
https://clipboard-sync-relay.fly.dev
```

1. Enter Room ID (any text, e.g., "my-clipboard")
2. Enter Device Name (e.g., "iPhone")
3. Click Connect

### Step 5: Connect Desktop

On your desktop app:
1. Start the app
2. Configure cloud relay with same Room ID
3. Start syncing!

## 📱 Using the Mobile Web App

### First Time Setup:
1. Open `https://clipboard-sync-relay.fly.dev` in Safari
2. Enter a **Room ID** (share this with your desktop)
3. Enter your device name
4. Click "Connect"

### Add to Home Screen (PWA):
1. In Safari, tap the Share button
2. Scroll down and tap "Add to Home Screen"
3. Now it works like a native app!

### Sending from Mobile to Desktop:
1. Paste text in the "Send to Desktop" box
2. Click "Send to Desktop" button
3. Content appears on your desktop instantly!

### Receiving from Desktop:
- When you copy on desktop, content appears in "Received from Desktop" section
- Tap any item to copy it to your iPhone clipboard

## 🔒 Security Note

**Current Implementation:**
- ⚠️ Uses Base64 encoding (NOT real encryption)
- Data visible to relay server
- Suitable for non-sensitive data only

**For Production:**
- Implement end-to-end encryption (same ECC+AES as desktop app)
- Encrypt data before sending to relay
- Relay server never sees plaintext

## 💰 Cost & Limits

**Fly.io Free Tier:**
- 3 shared-cpu VMs
- 160GB bandwidth/month
- Automatic HTTPS
- Global CDN

**Built-in Protection (Won't Exceed Free Tier):**
This relay has comprehensive limits to ensure you NEVER go over the free tier:

### 🛡️ Bandwidth Protection
- **Monthly Limit:** 150MB/month (10MB safety buffer)
- **Automatic Reset:** First day of each month
- **Tracking:** Real-time bandwidth monitoring
- **Notifications:** All users notified when limit reached

**Why 150MB is enough:**
- Typical clipboard text: ~1KB
- Can sync 153,600 times/month
- That's 5,120 syncs per day!
- Even with 10KB average (rich text/code): 15,360 syncs/month

### 🔒 Rate Limiting
- **Per Device:** 60 messages per minute
- **Per IP:** 100 requests per 15 minutes
- **Prevents:** Spam and abuse

### 📊 Connection Limits
- **Max Simultaneous:** 50 devices
- **Prevents:** Resource exhaustion
- **Typical Use:** 2-5 devices per user

### 📦 Message Size
- **Max Size:** 100KB per message
- **Recommended:** Keep clipboard items under 50KB
- **For Large Files:** Use file sharing instead

### 📈 Monitoring Your Usage

**Check usage anytime:**
```bash
# View server stats
curl https://clipboard-sync-relay.fly.dev/stats

# Response includes:
# - Active connections
# - Bandwidth used this month
# - Remaining bandwidth
# - Reset date
```

**In the mobile app:**
- Tap "Server Stats" to see real-time usage
- Shows bandwidth percentage used
- Days until reset

**What Happens at Limit:**
- Server stops accepting new clipboard data
- You receive a notification
- Existing connections stay alive
- Resets automatically next month
- No charges or overage fees!

## 🔧 Maintenance

### View Logs:
```bash
fly logs
```

### Check Bandwidth Usage:
```bash
# See server stats
curl https://clipboard-sync-relay.fly.dev/stats

# Or check Fly.io dashboard
fly dashboard
```

### Adjust Limits (Optional):
Edit `server.js` constants:
```javascript
const MAX_CONNECTIONS = 50;              // Simultaneous devices
const MAX_MESSAGE_SIZE = 100 * 1024;    // 100KB per message
const MAX_MESSAGES_PER_MINUTE = 60;     // Per device
const BANDWIDTH_LIMIT_MB = 150;         // Monthly bandwidth
```

Then redeploy:
```bash
fly deploy
```

### Scale Up (if needed):
```bash
# Add more VMs (uses more resources)
fly scale count 2

# Increase memory (if needed)
fly scale memory 512
```

### Update Deployment:
```bash
# Make changes to code
fly deploy
```

### Reset Bandwidth Counter:
```bash
# Restart the app (resets counter)
fly apps restart clipboard-sync-relay

# Or redeploy
fly deploy
```

### Delete App:
```bash
fly apps destroy clipboard-sync-relay
```

## 🐛 Troubleshooting

### Can't Connect from Mobile:
1. Check server is running: `fly status`
2. Check logs: `fly logs`
3. Make sure using HTTPS (not HTTP)
4. Check if bandwidth limit reached: `/stats`

### Desktop Won't Connect:
1. Verify Room ID matches mobile
2. Check firewall isn't blocking connections
3. Try restarting desktop app
4. Check server health: `curl https://clipboard-sync-relay.fly.dev/health`

### "Disconnected" After Few Minutes:
- Mobile browser may sleep connection
- Reopen the app to reconnect
- Consider adding to home screen (PWA mode)
- Check if you hit connection limit (50 max)

### "Bandwidth Limit Reached" Error:
- You've used 150MB this month
- Wait until next month for automatic reset
- Or restart app to reset counter: `fly apps restart clipboard-sync-relay`
- Consider increasing limit in `server.js` if needed

### "Rate Limit Exceeded":
- Sending too fast (max 60 messages/minute)
- Wait a minute and try again
- Normal clipboard use won't hit this limit

### "Too Many Connections":
- Max 50 simultaneous devices
- Disconnect unused devices
- Check for stuck connections in logs
- Restart server: `fly apps restart clipboard-sync-relay`

### Messages Not Syncing:
1. Check Room ID matches on all devices
2. Verify server is running: `fly status`
3. Check message size (max 100KB)
4. Check bandwidth usage: `/stats`
5. Look at logs: `fly logs`

### High Bandwidth Usage:
- Check what you're syncing (images? large code?)
- Keep clipboard items under 10KB for efficiency
- Monitor with `/stats` endpoint
- Consider local P2P sync instead for large files

## 📊 Monitoring

Check your app status:
```bash
fly status
fly logs
fly dashboard
```

Or visit: https://fly.io/dashboard

## 🎯 Next Steps

1. Deploy the relay server (above)
2. Update desktop app to support cloud relay
3. Test with mobile web app
4. (Optional) Implement proper end-to-end encryption
5. (Optional) Build native iOS app

## 🔐 Adding Real Encryption (Optional)

To make it production-ready with E2E encryption:

1. **Desktop Side:**
   - Generate ephemeral keypair for session
   - Encrypt clipboard data before sending to relay
   - Only send encrypted data

2. **Mobile Side:**
   - Implement same encryption in JavaScript (Web Crypto API)
   - Exchange keys via QR code scan
   - Decrypt received data client-side

3. **Relay Server:**
   - Stays the same (just forwards encrypted data)
   - Never sees plaintext

This ensures even the relay server can't read your clipboard!

## 📞 Support

If you encounter issues:
1. Check Fly.io docs: https://fly.io/docs
2. Check server logs: `fly logs`
3. Open GitHub issue

---

**Note:** Remember to share your Room ID securely between devices!
