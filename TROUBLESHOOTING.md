# 🔧 Quick Fixes

## Connection Issues

### "Connecting..." Dialog Won't Close

**Fixed in latest version!** Just pull the latest code:
```bash
git pull
python main.py
```

If still stuck:
1. Close the dialog manually (X button)
2. Check console for "Connected to cloud relay" message
3. Status bar should show "Cloud + Local"

---

### Can't Connect to Cloud Relay

**Check these:**
1. ✅ URL is correct: `https://clipboard-sync-tool.fly.dev`
2. ✅ Room ID matches on desktop and mobile
3. ✅ Internet connection working
4. ✅ No firewall blocking

**Try:**
- Use the public relay first: `https://clipboard-sync-tool.fly.dev`
- Room ID is case-sensitive: `test` ≠ `Test`
- Check console output for error messages

---

### Mobile Not Receiving Clipboard

**Check:**
1. Mobile browser tab is still open (not closed/minimized)
2. Mobile shows "Connected" status (green)
3. Same Room ID on both devices
4. Try copying something on desktop first

**If still not working:**
- Refresh mobile browser page
- Re-enter Room ID
- Check desktop console for "Sent clipboard to cloud relay"

---

### Desktop Not Receiving from Mobile

**Check:**
1. Desktop shows "Cloud + Local" in status bar
2. Console shows "Connected to cloud relay"
3. Try copying something on desktop first (triggers sync)

**If still not working:**
- Click "Cloud Relay" button again
- Reconnect with same Room ID
- Check console for errors

---

## Performance Issues

### Slow Sync

**This is normal:**
- Cloud relay: ~1-2 second delay (internet routing)
- Local P2P: Instant (same network)

**If slower than 5 seconds:**
- Check internet speed
- Try public relay instead of your own
- Check Fly.io status page

---

### Rate Limit Errors

**You hit the free tier limit:**
- 150MB/month bandwidth
- 60 messages/minute per device
- 100KB message size

**Solutions:**
- Wait a few minutes (rate limits reset)
- Deploy your own relay (separate quota)
- Use local P2P for desktop-to-desktop

---

## Installation Issues

### "No module named 'PyQt6'"

```bash
pip install -r requirements.txt
```

### "Python not found"

Install Python 3.8+ from python.org

### "flyctl: command not found"

Only needed if deploying your own relay:
```bash
.\deploy-cloud-relay.ps1  # Installs Fly CLI automatically
```

---

## Common Questions

### Do I need to deploy a relay?

**No!** Use the public relay:
- URL: `https://clipboard-sync-tool.fly.dev`
- FREE for everyone
- Already deployed and running

Deploy your own only if you want:
- Private relay
- More bandwidth
- Custom domain

### Is my data secure?

**Public relay:**
- Data sent in Base64 encoding (not encrypted)
- Don't send passwords or sensitive data
- Anyone with your Room ID can join

**Local P2P:**
- End-to-end encrypted (ECC + AES-256-GCM)
- Fully secure

**Recommendation:** Use unique Room IDs like `my-secret-room-xyz123`

### Can multiple people use the same Room ID?

**Yes!** All devices in the same room sync clipboards together.

**Example:**
- Desktop 1 in room "office"
- Desktop 2 in room "office"
- Mobile in room "office"
→ All 3 devices sync

---

## Still Having Issues?

1. **Check console output**: Look for errors when running `python main.py`
2. **Check browser console**: F12 on mobile/desktop browser
3. **Try public relay first**: Rule out deployment issues
4. **Open an issue**: https://github.com/Omerba31/clipboard-sync-tool/issues

Include:
- Error messages from console
- Steps to reproduce
- OS and Python version
