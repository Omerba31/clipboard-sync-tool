# Troubleshooting

## Cloud Relay Issues

| Problem | Solution |
|---------|----------|
| Can't connect | Check URL and Room ID are correct |
| Mobile not receiving | Refresh browser, check same Room ID |
| Desktop not receiving | Reconnect via "Cloud Relay" button |
| Garbled/corrupted text | Password mismatch - use same password on all devices |
| "Decryption failed" | Room ID or password doesn't match |
| "Already connected" | Restart app, refresh mobile browser |

## Local P2P Issues

| Problem | Solution |
|---------|----------|
| Devices not found | Both must be on same WiFi |
| Pairing fails | Copy QR data exactly (full JSON) |
| Connection drops | Check firewall allows Python |

## App Won't Start

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check Python version (need 3.8+)
python --version
```

## Rate Limits

Free tier limits (Railway.app):
- 150MB/month bandwidth
- 60 messages/minute

Wait a minute or deploy your own relay.

## Security Tips

- ⚠️ **Password must match exactly** on all devices (or leave empty on all)
- Use unique Room IDs to avoid conflicts with other users
- Both Cloud Relay and Local P2P use end-to-end encryption

See [main README](../README.md#security) for encryption details.
