# 🔐 Encryption Guide

How encryption works in Clipboard Sync Tool - practical examples included.

---

## Quick Summary

| Mode | Algorithm | Key Source |
|------|-----------|------------|
| **Cloud Relay** | AES-256-GCM | Room ID + Password |
| **Local P2P** | ECDH + AES-256-GCM | QR code key exchange |

**Both modes are end-to-end encrypted** - the server never sees your plaintext data.

---

## Cloud Relay Encryption

### How It Works

```
You type: "Hello World"
     ↓
Encrypt with AES-256-GCM
     ↓
Send: "gGrsPiT7H6yPk5t4Vrd+6ytl..."  (encrypted blob)
     ↓
Server relays (can't read it)
     ↓
Other device decrypts → "Hello World"
```

### Key Derivation

Your encryption key is derived from **Room ID + Password**:

```
Key = PBKDF2(room_id + password, salt, 100000 iterations, SHA-256)
```

**Example:**
```
Room ID:  "my-room"
Password: "secret123"
    ↓
Input:    "my-roomsecret123"
Salt:     "clipboard-sync-my-room"
    ↓
Key:      e65421233e213485d54df4bad0908890... (256-bit)
```

### Password Groups

Devices with **different passwords** cannot decrypt each other's messages, even in the same room:

```
Room: "office"

┌─────────────────────────────────────────────────────┐
│  Password: "team-a"          Password: "team-b"     │
│  ┌─────────────────┐        ┌─────────────────┐     │
│  │ Alice's Desktop │ ←───→  │ Bob's Desktop   │     │
│  │ Alice's Phone   │   ✗    │ Bob's Phone     │     │
│  └─────────────────┘        └─────────────────┘     │
│         ↕ ✓                        ↕ ✓              │
│  Can decrypt each other    Can decrypt each other   │
└─────────────────────────────────────────────────────┘
```

- Alice & Alice's phone (same password) → ✅ Can sync
- Bob & Bob's phone (same password) → ✅ Can sync  
- Alice & Bob (different passwords) → ❌ Can't decrypt

### Encryption Format

Each encrypted message contains:

```
┌──────────┬─────────────────────────┬──────────────┐
│ IV       │ Ciphertext              │ Auth Tag     │
│ 12 bytes │ (same length as input)  │ 16 bytes     │
└──────────┴─────────────────────────┴──────────────┘
                    ↓
            Base64 encoded for transmission
```

**Example:**
```
Plaintext:  "hello" (5 bytes)
Encrypted:  "O4MKkRoX+YBGwjR6ft9E8c6VRlPVaLrTxPUcjEdtq2ny" (44 chars base64)
            └─ Contains: 12-byte IV + 5-byte ciphertext + 16-byte auth tag
```

---

## Local P2P Encryption

### How It Works

Uses **Elliptic Curve Diffie-Hellman (ECDH)** for key exchange:

```
Computer A                           Computer B
    │                                    │
    ├── Generate keypair ──────────────► │
    │   (public key in QR code)          │
    │                                    ├── Generate keypair
    │ ◄────────────── Exchange ──────────┤
    │                                    │
    ├── Compute shared secret ───────────┤
    │   (both get same key)              │
    │                                    │
    └── AES-256-GCM encryption ──────────┘
```

### Why It's More Secure

| Feature | Cloud Relay | Local P2P |
|---------|-------------|-----------|
| Key exchange | Password-based | ECDH (cryptographic) |
| Forward secrecy | ❌ Same key always | ✅ New key per session |
| Network | Internet | Local only |
| Server involvement | Relay server | None |

---

## Code Examples

### Python (Desktop)

```python
from core.cloud_relay_crypto import CloudRelayCrypto

# Initialize
crypto = CloudRelayCrypto()
crypto.init(room_id="my-room", password="secret123")

# Encrypt
plaintext = "Hello, World!"
encrypted = crypto.encrypt(plaintext)
# → "gGrsPiT7H6yPk5t4Vrd+6ytlaBtScg70Z0KZbWobi9mP..."

# Decrypt
decrypted = crypto.decrypt(encrypted)
# → "Hello, World!"
```

### JavaScript (Web/Mobile)

```javascript
// Initialize
await clipboardCrypto.init("my-room", "secret123");

// Encrypt
const encrypted = await clipboardCrypto.encrypt("Hello, World!");
// → "gGrsPiT7H6yPk5t4Vrd+6ytlaBtScg70Z0KZbWobi9mP..."

// Decrypt
const decrypted = await clipboardCrypto.decrypt(encrypted);
// → "Hello, World!"
```

### Cross-Platform Compatibility

Python and JavaScript produce **identical encryption** - they can decrypt each other's messages:

```
Python encrypts → JavaScript decrypts ✓
JavaScript encrypts → Python decrypts ✓
```

---

## Security Properties

### What's Protected

| Threat | Protected? | How |
|--------|------------|-----|
| Server reading your data | ✅ Yes | E2E encryption |
| Network eavesdropping | ✅ Yes | TLS + E2E encryption |
| Wrong room accessing data | ✅ Yes | Different key per room |
| Brute force password | ✅ Resistant | PBKDF2 100k iterations |
| Replay attacks | ✅ Yes | Random IV per message |
| Tampering | ✅ Yes | GCM authentication tag |

### What's NOT Protected

| Threat | Protected? | Why |
|--------|------------|-----|
| Weak password guessing | ⚠️ Partially | Use strong passwords |
| Device compromise | ❌ No | Key is in memory |
| Metadata (who's online) | ❌ No | Server sees connections |

---

## Best Practices

1. **Use a password** - Even a simple one adds security
2. **Unique room IDs** - Don't use "test" or "room1"
3. **Same password everywhere** - Or you'll get decryption errors
4. **Local P2P for sensitive data** - No server involved

---

## Testing Encryption

Run the encryption tests:

```bash
# Test Python encryption
python -m pytest tests/unit/test_encryption.py -v

# Test Python↔JavaScript compatibility
python -m pytest tests/unit/test_crypto_compatibility.py -v

# Test live encrypted relay
python -m pytest tests/integration/test_cloud_relay_live.py::TestCloudRelayMessaging::test_encrypted_message_relay -v
```

### Browser Console Test

Open the web app and run in browser console:

```javascript
// Test encryption works
await clipboardCrypto.init("test-room", "test123");
const enc = await clipboardCrypto.encrypt("hello");
const dec = await clipboardCrypto.decrypt(enc);
console.log(dec); // → "hello"
```
