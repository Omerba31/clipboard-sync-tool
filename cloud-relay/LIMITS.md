# Rate Limiting & Protection Details

This document explains all the built-in protections to ensure you **never exceed Fly.io free tier limits**.

## 🛡️ Protection Layers

### 1. Bandwidth Protection (Primary)
**Monthly Limit:** 150MB  
**Free Tier:** 160GB (we use 10MB buffer for safety)

```javascript
const BANDWIDTH_LIMIT_MB = 150;
```

**How it works:**
- Every message is counted in bytes
- Running total tracked in memory
- When limit reached: new clipboard data rejected
- All users notified: "Bandwidth limit reached"
- Automatically resets on 1st of each month

**Math:**
- Typical clipboard text: 1KB
- 150MB = 153,600 copies/month
- 5,120 syncs per day
- 213 syncs per hour
- Enough for heavy personal use!

### 2. Connection Limit
**Max Simultaneous:** 50 devices

```javascript
const MAX_CONNECTIONS = 50;
```

**Why this matters:**
- Each connection uses memory
- Prevents resource exhaustion
- Typical use: 2-5 devices per user
- 50 allows for growth

### 3. Message Rate Limiting
**Per Device:** 60 messages per minute

```javascript
const MAX_MESSAGES_PER_MINUTE = 60;
```

**Prevents:**
- Accidental infinite loops
- Malicious spam
- Runaway scripts

**Normal use:**
- Humans copy ~1-2 times per minute
- 60/min is very generous

### 4. Message Size Limit
**Max Size:** 100KB per message

```javascript
const MAX_MESSAGE_SIZE = 100 * 1024; // 100KB
```

**Why:**
- Clipboard text rarely exceeds 10KB
- Prevents single huge transfers
- Forces chunking for large content

**Recommendation:**
- Text/code: Usually <10KB ✅
- Rich text: 10-50KB ✅
- Images/files: Use file sharing instead ❌

### 5. IP-based Rate Limiting
**Per IP:** 100 requests per 15 minutes

```javascript
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100
});
```

**Prevents:**
- DDoS attacks
- Abuse from single source
- Accidental hammering

## 📊 Monitoring

### Real-time Stats Endpoint
```bash
curl https://your-app.fly.dev/stats
```

**Returns:**
```json
{
  "status": "ok",
  "connections": 3,
  "bandwidth": {
    "used": "24.5 MB",
    "limit": "150 MB",
    "percentage": 16.3,
    "resetDate": "2024-02-01T00:00:00.000Z"
  }
}
```

### In Mobile App
Tap "Server Stats" to see:
- Current connections
- Bandwidth used
- Days until reset
- Connection status

## 🚨 What Happens at Limit?

### Bandwidth Limit Reached
1. Server stops accepting new clipboard data
2. All connected users get notification:
   ```
   "Bandwidth limit reached for this month. 
    Resets on [date]. Existing connections maintained."
   ```
3. Health check shows limit status
4. Can still connect/disconnect
5. **No charges or overage fees!**

### Connection Limit Reached
1. New connections rejected with message:
   ```
   "Server at max capacity (50 connections). 
    Please try again later."
   ```
2. Existing connections unaffected

### Rate Limit Hit
1. Device gets cooldown message:
   ```
   "Too many messages. Please wait a minute."
   ```
2. Counter resets after 1 minute
3. Other devices unaffected

## 🔧 Adjusting Limits

If you need different limits, edit `server.js`:

```javascript
// Conservative (saves bandwidth)
const MAX_CONNECTIONS = 25;
const MAX_MESSAGE_SIZE = 50 * 1024;      // 50KB
const MAX_MESSAGES_PER_MINUTE = 30;
const BANDWIDTH_LIMIT_MB = 100;          // 100MB/month

// Generous (uses more bandwidth)
const MAX_CONNECTIONS = 100;
const MAX_MESSAGE_SIZE = 200 * 1024;     // 200KB
const MAX_MESSAGES_PER_MINUTE = 120;
const BANDWIDTH_LIMIT_MB = 500;          // 500MB/month (still well under 160GB)
```

Then redeploy:
```bash
fly deploy
```

## 📈 Bandwidth Calculator

**Text Only (1KB average):**
- 150MB = 153,600 syncs/month ✅
- 5,120 per day
- Safe for any text-based workflow

**Rich Text/Code (5KB average):**
- 150MB = 30,720 syncs/month ✅
- 1,024 per day
- Still plenty for coding

**Mixed Content (10KB average):**
- 150MB = 15,360 syncs/month ✅
- 512 per day
- Good for varied use

**Heavy Use (50KB average):**
- 150MB = 3,072 syncs/month ⚠️
- 102 per day
- Consider local P2P instead

## 🎯 Best Practices

1. **Use for appropriate content:**
   - ✅ Text snippets
   - ✅ Code
   - ✅ URLs
   - ✅ Small formatted text
   - ❌ Images (use image hosting)
   - ❌ Files (use file sharing)

2. **Monitor usage:**
   - Check `/stats` periodically
   - Watch for unexpected spikes
   - Mobile app shows real-time stats

3. **Multiple projects:**
   - Deploy separate relay per project
   - Each gets own 150MB/month
   - Or increase limit in one deployment

4. **Hybrid approach:**
   - Use local P2P when on same network
   - Use cloud relay when remote
   - Best of both worlds!

## 🔒 Security Notes

**Current Implementation:**
- ⚠️ Base64 encoding (NOT encryption)
- Rate limiting prevents spam
- Bandwidth prevents abuse
- Good for non-sensitive data

**For Production:**
- Add E2E encryption
- Use HTTPS (already included)
- Rotate room IDs regularly
- Implement authentication

## 🆘 Manual Reset

If you need to reset bandwidth counter before month end:

```bash
# Restart app (resets counter to 0)
fly apps restart your-app-name

# Or redeploy
fly deploy
```

**Note:** Only do this if you understand your usage patterns and won't exceed free tier!

## 📞 Support

**Fly.io limits:**
- Dashboard: https://fly.io/dashboard
- Pricing: https://fly.io/docs/about/pricing/

**Check your actual usage:**
```bash
fly dashboard
# Shows real bandwidth used by Fly.io
```

**The built-in limits are conservative:**
- 150MB limit << 160GB free tier
- You have 1,000x safety margin
- Would need to increase limit significantly to risk overage
