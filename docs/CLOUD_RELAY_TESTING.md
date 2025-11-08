# Testing Cloud Relay Desktop Integration

This guide will help you test the new desktop cloud relay feature.

## Prerequisites

✅ Cloud relay deployed to Fly.io
✅ Desktop app installed (`python main.py` works)
✅ Fly.io app URL (e.g., `https://clipboard-sync-relay.fly.dev`)

## Test Steps

### 1. Test Mobile Connection First

**On your iPhone:**
1. Open your Fly.io URL in Safari: `https://your-app.fly.dev`
2. Enter Room ID: `test-room`
3. Type some text in the "Send" box
4. Click "Send to Clipboard"
5. Type different text
6. Click "Send to Clipboard" again

✅ **Expected:** Text appears in the "Received" section

---

### 2. Test Desktop Connection

**On your desktop:**
1. Launch the app:
   ```bash
   python main.py
   ```

2. Click the **"☁️ Cloud Relay"** button in the header

3. Enter connection details:
   - **Cloud Relay URL:** `https://your-app.fly.dev` (your actual URL)
   - **Room ID:** `test-room` (same as mobile)

4. Click **"🔌 Connect"**

✅ **Expected:** 
- "Connecting..." message appears
- Success dialog shows: "✅ Connected!"
- Status changes to: "🟢 Sync Active (Cloud + Local)"

---

### 3. Test Mobile → Desktop Sync

**On iPhone:**
1. Type some text (e.g., "Hello from iPhone!")
2. Click "Send to Clipboard"

**On Desktop:**
1. Open any app (Notepad, Word, browser)
2. Press `Ctrl+V` (Windows) or `Cmd+V` (Mac)

✅ **Expected:** Text from iPhone pastes successfully!

---

### 4. Test Desktop → Mobile Sync

**On Desktop:**
1. Copy some text (e.g., "Hello from Desktop!")
   - Select text and press `Ctrl+C` / `Cmd+C`
   - OR right-click → Copy

**On iPhone:**
1. Look at the "Received Clipboard" section

✅ **Expected:** Text from desktop appears automatically!

---

### 5. Test Bidirectional Sync

**Rapid-fire test:**
1. Mobile: Send "Message 1" → Desktop: Paste (should work)
2. Desktop: Copy "Message 2" → Mobile: Check received (should appear)
3. Mobile: Send "Message 3" → Desktop: Paste (should work)
4. Desktop: Copy "Message 4" → Mobile: Check received (should appear)

✅ **Expected:** All messages sync correctly in both directions

---

## Troubleshooting

### Desktop won't connect

**Check:**
1. URL is correct (https://your-app.fly.dev)
2. Room ID matches mobile exactly (case-sensitive)
3. Internet connection working
4. Server is running: `fly status` (in cloud-relay folder)

**Logs:**
- Check console output in terminal running `python main.py`
- Look for: "Connected to cloud relay" or error messages

### Mobile works but desktop doesn't receive

**Check:**
1. Desktop is still connected (status shows "Cloud + Local")
2. No errors in console
3. Try copying something on desktop first (triggers sync)

### Desktop works but mobile doesn't receive

**Check:**
1. Mobile browser still on the page (not closed/minimized)
2. Mobile shows "Connected" status
3. Both using same Room ID

### Connection drops

**Expected behavior:**
- Auto-reconnects after 1-5 seconds
- Check console for "Disconnected" / "Reconnecting" messages

---

## Expected Console Output

### Successful Connection
```
[INFO] Connecting to cloud relay: https://your-app.fly.dev
[INFO] Connected to cloud relay: https://your-app.fly.dev
[INFO] Joined room: test-room
```

### Sending Clipboard
```
[INFO] New clipboard content: text
[INFO] Sent clipboard to cloud relay: text (25 bytes)
```

### Receiving Clipboard
```
[INFO] Received clipboard from cloud relay: text
[INFO] ✅ Clipboard updated from cloud relay
```

---

## Rate Limits

The cloud relay has built-in protection:
- **150MB/month bandwidth** (resets monthly)
- **50 simultaneous connections**
- **60 messages/minute per device**
- **100KB max message size**

If you hit a limit:
- Mobile: Error notification appears
- Desktop: Check console for error message
- Wait a minute and try again

---

## Success Criteria

✅ Desktop connects to cloud relay
✅ Mobile → Desktop sync works
✅ Desktop → Mobile sync works
✅ Bidirectional sync works continuously
✅ Status shows "Cloud + Local"
✅ No errors in console

---

## What to Report

If something doesn't work, please share:
1. **Error messages** from desktop console
2. **Steps to reproduce** the issue
3. **Screenshots** of dialogs/errors
4. **Browser console** from mobile (F12 on desktop browsers)

---

## Next Steps

Once testing is complete:
- ✅ Desktop cloud relay working
- ⏳ Add disconnect button
- ⏳ Save last used URL/Room ID
- ⏳ Add connection status indicator
- ⏳ Add settings for auto-connect on startup

Enjoy your cross-device clipboard sync! 🎉
