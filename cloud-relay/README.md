# Cloud Relay Deployment Guide

## 🚀 Deploy to Railway.app ($5 FREE Credit/Month)

### Prerequisites
1. **Create Railway account:** https://railway.app/
2. **Sign up with GitHub** (easiest method)

### Deploy in 3 Steps:

1. **Push code to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Deploy to Railway"
   git push
   ```

2. **Deploy to Railway:**
   - Go to https://railway.app/new
   - Click "Deploy from GitHub repo"
   - Select `clipboard-sync-tool` repository
   - Railway auto-detects the Node.js app
   - Click "Deploy Now"

3. **Configure Service:**
   - After deployment, click on your service
   - Go to "Settings" tab
   - Under "Service" section:
     - **Root Directory:** Set to `cloud-relay`
     - **Start Command:** `npm start` (auto-detected)
   - Click "Generate Domain" to get your public URL

### Get Your Server URL

After deployment (~1-2 minutes), Railway generates a URL:
```
https://clipboard-sync-relay-production.up.railway.app
```

Or set a custom domain in Settings → Domains.

Test it:
```bash
curl https://your-service.up.railway.app/health
```

### Step 3: Update Desktop App

Add cloud relay support to your desktop app (instructions below).

### Step 4: Use Mobile Web App

Open on your iPhone:
```
https://your-service.up.railway.app
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
1. Open `https://your-service.up.railway.app` in Safari
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

**Railway.app Hobby Plan:**
- $5 FREE credit per month (no credit card required for trial)
- ~500 hours of uptime (about 21 days 24/7)
- Automatic HTTPS
- No auto-sleep (always-on)
- Custom domains included
- After free credit: $5/month for 500 hours

**Cost Estimate:**
- This lightweight relay uses ~$0.01/hour
- $5 = ~500 hours = ~21 days continuous uptime
- For personal use: $5/month covers most needs

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
curl https://your-service.up.railway.app/stats

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
- Go to https://railway.app/dashboard
- Click on your project
- Select your service
- Click "Deployments" → View logs

### Check Usage & Costs:
```bash
# See server stats
curl https://your-service.up.railway.app/stats

# Check Railway usage dashboard
https://railway.app/account/usage
```

### Adjust Limits (Optional):
Edit `server.js` constants:
```javascript
const MAX_CONNECTIONS = 50;              // Simultaneous devices
const MAX_MESSAGE_SIZE = 100 * 1024;    // 100KB per message
const MAX_MESSAGES_PER_MINUTE = 60;     // Per device
const BANDWIDTH_LIMIT_MB = 150;         // Monthly bandwidth
```

Then push to GitHub (auto-deploys):
```bash
git add .
git commit -m "Update limits"
git push
```

### Scale Up (if needed):
- Railway auto-scales based on usage
- Costs scale with actual usage ($0.01/hour typical)
- Monitor costs at https://railway.app/account/usage

### Update Deployment:
```bash
# Make changes to code
git add .
git commit -m "Update"
git push  # Auto-deploys!
```

### Manual Restart:
- Go to https://railway.app/dashboard
- Click on your service
- Click "..." menu → "Restart"

### Delete Service:
- Go to https://railway.app/dashboard
- Click on your project
- Settings → "Danger" → "Delete Project"

## 🐛 Troubleshooting

### Can't Connect from Mobile:
1. Check service is running in Railway dashboard
2. Check logs in Railway dashboard
3. Make sure using HTTPS (not HTTP)
4. Check if bandwidth limit reached: `/stats`
5. Verify you have remaining credit (check usage page)

### Desktop Won't Connect:
1. Verify Room ID matches mobile
2. Check firewall isn't blocking connections
3. Try restarting desktop app
4. Check server health: `curl https://your-service.up.railway.app/health`
5. Check Railway service status in dashboard

### "Disconnected" After Few Minutes:
- Mobile browser may sleep connection
- Reopen the app to reconnect
- Consider adding to home screen (PWA mode)
- Check if you hit connection limit (50 max)

### "Bandwidth Limit Reached" Error:
- You've used 150MB this month
- Wait until next month for automatic reset
- Or restart service via Railway dashboard
- Add more credit at https://railway.app/account/billing

### "Rate Limit Exceeded":
- Sending too fast (max 60 messages/minute)
- Wait a minute and try again
- Normal clipboard use won't hit this limit

### "Too Many Connections":
- Max 50 simultaneous devices
- Disconnect unused devices
- Check for stuck connections in logs
- Restart service via Railway dashboard

### Messages Not Syncing:
1. Check Room ID matches on all devices
2. Verify service is running in Railway dashboard
3. Check message size (max 100KB)
4. Check bandwidth usage: `/stats`
5. Look at logs in Railway dashboard
6. Check you have remaining Railway credit

### High Bandwidth Usage:
- Check what you're syncing (images? large code?)
- Keep clipboard items under 10KB for efficiency
- Monitor with `/stats` endpoint
- Consider local P2P sync instead for large files

## 📊 Monitoring

**Railway Dashboard:** https://railway.app/dashboard

From the dashboard you can:
- View real-time logs
- Check usage and costs
- Monitor uptime and metrics
- See deployment history
- Configure environment variables
- Manual deploy/restart

**Usage Tracking:** https://railway.app/account/usage
- See current month's usage
- Remaining free credit
- Estimated costs
- Historical usage

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
1. Check Railway docs: https://docs.railway.app/
2. Check server logs in dashboard
3. Check Railway status: https://railway.statuspage.io/
4. Railway Discord: https://discord.gg/railway
5. Open GitHub issue

## ⚡ Performance Notes

**Always-On Service:**
- Railway services don't auto-sleep
- Instant connections (no cold starts)
- Pay only for actual usage
- Typical cost: $0.01/hour = ~$7/month for 24/7 uptime

**Cost Optimization:**
- Free $5 credit covers ~500 hours (~21 days)
- For occasional use: Pause service when not needed
- Service settings → "Pause" to stop billing
- Resume when needed (instant startup)

---

**Note:** Remember to share your Room ID securely between devices!
