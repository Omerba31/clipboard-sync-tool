/**
 * End-to-End Encryption for Cloud Relay
 * Uses Web Crypto API with AES-256-GCM
 * Key is derived from Room ID + optional password using PBKDF2
 */

class ClipboardCrypto {
    constructor() {
        this.key = null;
        this.roomId = null;
        this.password = null;
    }

    /**
     * Initialize encryption with room ID and optional password
     * @param {string} roomId - The room ID
     * @param {string} password - Optional password for extra security
     */
    async init(roomId, password = '') {
        this.roomId = roomId;
        this.password = password;
        
        // Derive key from room ID + password
        const keyMaterial = await this.getKeyMaterial(roomId + password);
        
        // Use room ID as salt (consistent across devices in same room)
        const salt = new TextEncoder().encode('clipboard-sync-' + roomId);
        
        this.key = await crypto.subtle.deriveKey(
            {
                name: 'PBKDF2',
                salt: salt,
                iterations: 100000,
                hash: 'SHA-256'
            },
            keyMaterial,
            { name: 'AES-GCM', length: 256 },
            false,
            ['encrypt', 'decrypt']
        );
        
        console.log('[🔐] Encryption initialized for room:', roomId);
    }

    /**
     * Get key material from passphrase
     */
    async getKeyMaterial(passphrase) {
        const encoder = new TextEncoder();
        return crypto.subtle.importKey(
            'raw',
            encoder.encode(passphrase),
            'PBKDF2',
            false,
            ['deriveBits', 'deriveKey']
        );
    }

    /**
     * Encrypt content
     * @param {string} content - Plain text content to encrypt
     * @returns {string} - Base64 encoded encrypted content with IV
     */
    async encrypt(content) {
        if (!this.key) {
            throw new Error('Encryption not initialized. Call init() first.');
        }

        // Generate random IV for each encryption
        const iv = crypto.getRandomValues(new Uint8Array(12));
        
        // Encode content
        const encoder = new TextEncoder();
        const data = encoder.encode(content);
        
        // Encrypt
        const encrypted = await crypto.subtle.encrypt(
            { name: 'AES-GCM', iv: iv },
            this.key,
            data
        );
        
        // Combine IV + encrypted data and encode as base64
        const combined = new Uint8Array(iv.length + encrypted.byteLength);
        combined.set(iv);
        combined.set(new Uint8Array(encrypted), iv.length);
        
        return btoa(String.fromCharCode(...combined));
    }

    /**
     * Decrypt content
     * @param {string} encryptedBase64 - Base64 encoded encrypted content with IV
     * @returns {string} - Decrypted plain text
     */
    async decrypt(encryptedBase64) {
        if (!this.key) {
            throw new Error('Encryption not initialized. Call init() first.');
        }

        try {
            // Decode base64
            const combined = Uint8Array.from(atob(encryptedBase64), c => c.charCodeAt(0));
            
            // Extract IV and encrypted data
            const iv = combined.slice(0, 12);
            const encrypted = combined.slice(12);
            
            // Decrypt
            const decrypted = await crypto.subtle.decrypt(
                { name: 'AES-GCM', iv: iv },
                this.key,
                encrypted
            );
            
            // Decode to string
            const decoder = new TextDecoder();
            return decoder.decode(decrypted);
        } catch (error) {
            console.error('[🔐] Decryption failed:', error.message);
            throw new Error('Decryption failed. Wrong room ID or password?');
        }
    }

    /**
     * Check if encryption is initialized
     */
    isInitialized() {
        return this.key !== null;
    }
}

// Export singleton instance
const clipboardCrypto = new ClipboardCrypto();
