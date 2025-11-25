// Mobile Web App JavaScript
let socket = null;
let roomId = null;
let deviceName = null;
let deviceId = null;
let clipboardHistory = [];
let selectedImage = null; // Store selected image data
let encryptionEnabled = true; // E2E encryption on by default
let roomPassword = ''; // Optional password for extra security
let soundEnabled = true; // Sound notification enabled by default

// Notification sound using Web Audio API
let audioContext = null;

function playNotificationSound() {
    if (!soundEnabled) return;
    
    try {
        // Create audio context on first use (must be after user interaction)
        if (!audioContext) {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
        
        // Create a simple beep sound
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = 800; // Hz
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.3);
    } catch (err) {
        console.log('[🔊] Sound not available:', err.message);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Load saved credentials
    const saved = loadCredentials();
    if (saved) {
        document.getElementById('roomIdInput').value = saved.roomId;
        document.getElementById('deviceNameInput').value = saved.deviceName;
        if (saved.password) {
            const passwordInput = document.getElementById('roomPasswordInput');
            if (passwordInput) passwordInput.value = saved.password;
        }
        
        // Auto-connect if credentials exist
        roomId = saved.roomId;
        deviceName = saved.deviceName;
        roomPassword = saved.password || '';
        deviceId = 'mobile-' + Math.random().toString(36).substr(2, 9);
        
        // Hide modal and connect
        document.getElementById('connectionModal').classList.remove('show');
        connectToServer();
    }
    
    // Add paste event listener for images
    const textarea = document.getElementById('sendText');
    textarea.addEventListener('paste', handlePaste);
});

// Handle paste events (including images)
function handlePaste(event) {
    const items = (event.clipboardData || event.originalEvent.clipboardData).items;
    
    for (let item of items) {
        if (item.type.indexOf('image') !== -1) {
            event.preventDefault(); // Prevent default paste
            
            const file = item.getAsFile();
            if (file) {
                // Check file size (limit to 5MB)
                if (file.size > 5 * 1024 * 1024) {
                    showNotification('⚠️ Image too large (max 5MB)', 'error');
                    return;
                }
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    selectedImage = e.target.result; // Base64 data URL
                    
                    // Show preview
                    document.getElementById('previewImg').src = selectedImage;
                    document.getElementById('imagePreview').style.display = 'block';
                    document.getElementById('clearImageBtn').style.display = 'inline-block';
                    
                    showNotification('✅ Image pasted! Tap Send to share');
                };
                reader.readAsDataURL(file);
            }
        }
    }
}

function connect() {
    roomId = document.getElementById('roomIdInput').value.trim();
    deviceName = document.getElementById('deviceNameInput').value.trim();
    const passwordInput = document.getElementById('roomPasswordInput');
    roomPassword = passwordInput ? passwordInput.value : '';

    if (!roomId || !deviceName) {
        showNotification('⚠️ Please enter Room ID and Device Name', 'error');
        return;
    }

    // Generate device ID
    deviceId = 'mobile-' + Math.random().toString(36).substr(2, 9);

    // Save credentials
    saveCredentials(roomId, deviceName, roomPassword);

    // Close modal
    document.getElementById('connectionModal').classList.remove('show');

    // Connect to server
    connectToServer();
}

async function connectToServer() {
    updateStatus('Connecting...', false);
    
    // Initialize encryption
    if (encryptionEnabled && typeof clipboardCrypto !== 'undefined') {
        try {
            console.log('[🔐] Initializing encryption with:');
            console.log('     Room ID:', roomId);
            console.log('     Password length:', roomPassword.length);
            console.log('     Password (masked):', roomPassword ? '*'.repeat(roomPassword.length) : '(empty)');
            
            await clipboardCrypto.init(roomId, roomPassword);
            console.log('[🔐] E2E encryption enabled');
        } catch (err) {
            console.error('[🔐] Encryption init failed:', err);
            encryptionEnabled = false;
        }
    } else {
        console.warn('[🔐] Encryption disabled or crypto not available');
    }

    // Connect to relay server
    socket = io({
        transports: ['websocket', 'polling'],
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionAttempts: 5
    });

    socket.on('connect', () => {
        console.log('[✓] Connected to relay server');
        updateStatus('Connected', true);
        
        // Update encryption status indicator
        const encStatus = document.getElementById('encryptionStatus');
        if (encStatus) {
            if (encryptionEnabled && clipboardCrypto.isInitialized()) {
                encStatus.textContent = '🔐 E2E';
                encStatus.title = 'End-to-end encrypted';
            } else {
                encStatus.textContent = '⚠️ No E2E';
                encStatus.title = 'Not encrypted - set a password';
                encStatus.style.color = '#ff9800';
            }
        }

        // Detect device type automatically
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        const isTablet = /iPad|Android/i.test(navigator.userAgent) && !/Mobile/i.test(navigator.userAgent);
        
        let detectedType = 'desktop';
        if (isMobile && !isTablet) {
            detectedType = 'mobile';
        } else if (isTablet) {
            detectedType = 'tablet';
        }

        // Register device
        socket.emit('register', {
            deviceId,
            deviceName,
            deviceType: detectedType,
            roomId
        });

        showNotification('✅ Connected to cloud relay!');
    });

    socket.on('disconnect', () => {
        console.log('[✗] Disconnected from relay server');
        updateStatus('Disconnected', false);
        showNotification('⚠️ Disconnected from server', 'error');
    });

    socket.on('room_devices', (devices) => {
        console.log('[📱] Devices in room:', devices);
        updateDevicesList(devices);
    });

    socket.on('device_joined', (device) => {
        console.log('[+] Device joined:', device.deviceName);
        showNotification(`📱 ${device.deviceName} joined`);
        // Request updated device list
        socket.emit('get_devices');
    });

    socket.on('device_left', (device) => {
        console.log('[-] Device left:', device.deviceName);
        showNotification(`👋 ${device.deviceName} left`);
        // Request updated device list
        socket.emit('get_devices');
    });

    socket.on('clipboard_data', (data) => {
        console.log('[📋] Received clipboard data from:', data.from_name);
        receiveFromDesktop(data);
    });

    socket.on('error', (data) => {
        console.error('[!] Server error:', data);
        showNotification(`⚠️ ${data.message}`, 'error');
        
        if (data.code === 'BANDWIDTH_LIMIT' || data.code === 'MAX_CONNECTIONS') {
            updateStatus('Server Limit Reached', false);
        }
    });

    socket.on('server_message', (data) => {
        console.log('[📢] Server message:', data.message);
        showNotification(`📢 ${data.message}`, data.type === 'warning' ? 'error' : 'success');
    });

    socket.on('connect_error', (error) => {
        console.error('[!] Connection error:', error);
        updateStatus('Connection Error', false);
        showNotification('❌ Connection failed', 'error');
    });
}

// Load and display server stats
function loadServerStats() {
    fetch('/api/stats')
        .then(r => r.json())
        .then(stats => {
            console.log('[📊] Server stats:', stats);
            // Could display this in UI if needed
        })
        .catch(err => console.error('Failed to load stats:', err));
}

function handleImageSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Check file size (limit to 5MB for cloud relay)
    if (file.size > 5 * 1024 * 1024) {
        showNotification('⚠️ Image too large (max 5MB)', 'error');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = function(e) {
        selectedImage = e.target.result; // Base64 data URL
        
        // Show preview
        document.getElementById('previewImg').src = selectedImage;
        document.getElementById('imagePreview').style.display = 'block';
        document.getElementById('clearImageBtn').style.display = 'inline-block';
        
        showNotification('✅ Image ready to send');
    };
    reader.readAsDataURL(file);
}

function clearImage() {
    selectedImage = null;
    document.getElementById('imageInput').value = '';
    document.getElementById('imagePreview').style.display = 'none';
    document.getElementById('clearImageBtn').style.display = 'none';
}

// Helper to add item to history
function addToHistory(content, contentType, from) {
    clipboardHistory.unshift({
        content,
        contentType,
        timestamp: Date.now(),
        from
    });
    
    // Keep only last 10 items
    if (clipboardHistory.length > 10) {
        clipboardHistory.pop();
    }
    
    displayReceivedContent();
}

// Helper to send clipboard data (with encryption)
async function sendClipboardData(content, contentType) {
    let encryptedContent;
    
    if (encryptionEnabled && clipboardCrypto.isInitialized()) {
        try {
            // Encrypt content
            const dataToEncrypt = contentType === 'text' ? content : content;
            encryptedContent = await clipboardCrypto.encrypt(dataToEncrypt);
        } catch (err) {
            console.error('[🔐] Encryption failed:', err);
            showNotification('⚠️ Encryption failed', 'error');
            return;
        }
    } else {
        // Fallback to base64 only (not secure)
        encryptedContent = contentType === 'text' ? btoa(unescape(encodeURIComponent(content))) : content;
    }
    
    socket.emit('clipboard_data', {
        encrypted_content: encryptedContent,
        content_type: contentType,
        encrypted: encryptionEnabled && clipboardCrypto.isInitialized(),
        timestamp: Date.now()
    });
}

function sendToDesktop() {
    const text = document.getElementById('sendText').value.trim();
    
    if (!text && !selectedImage) {
        showNotification('⚠️ Please enter text or choose an image', 'error');
        return;
    }

    if (!socket || !socket.connected) {
        showNotification('❌ Not connected to server', 'error');
        return;
    }

    // Send image if selected
    if (selectedImage) {
        sendClipboardData(selectedImage, 'image');
        addToHistory(selectedImage, 'image', 'You (sent)');
        showNotification('✅ Image sent to other devices!');
        clearImage();
    }
    
    // Send text if provided
    if (text) {
        sendClipboardData(text, 'text');
        addToHistory(text, 'text', 'You (sent)');
        showNotification('✅ Text sent to other devices!');
        document.getElementById('sendText').value = '';
    }
}

async function receiveFromDesktop(data) {
    const contentType = data.content_type || 'text';
    const isEncrypted = data.encrypted === true;
    let content;
    
    console.log('[📋] Processing received data:', { 
        contentType, 
        isEncrypted, 
        hasEncryptedContent: !!data.encrypted_content,
        encryptedContentPreview: data.encrypted_content ? data.encrypted_content.substring(0, 50) + '...' : 'none',
        cryptoInitialized: clipboardCrypto.isInitialized(),
        encryptionEnabled: encryptionEnabled
    });
    
    try {
        if (isEncrypted) {
            // Data is encrypted - must decrypt
            if (!encryptionEnabled || !clipboardCrypto.isInitialized()) {
                console.error('[🔐] Cannot decrypt: encryption not initialized');
                showNotification('⚠️ Cannot decrypt - enter password and reconnect', 'error');
                return;
            }
            
            try {
                console.log('[🔐] Attempting decryption...');
                content = await clipboardCrypto.decrypt(data.encrypted_content);
                console.log('[🔐] Successfully decrypted content:', content.substring(0, 50));
            } catch (decryptError) {
                console.error('[🔐] Decryption failed:', decryptError);
                console.error('[🔐] Current crypto state - room:', clipboardCrypto.roomId, 'password length:', clipboardCrypto.password?.length || 0);
                showNotification('⚠️ Decryption failed - wrong password?', 'error');
                return;
            }
        } else if (contentType === 'image') {
            // Unencrypted image data URL - use as-is
            content = data.encrypted_content;
        } else {
            // Legacy unencrypted base64 decode for text
            try {
                content = decodeURIComponent(escape(atob(data.encrypted_content)));
            } catch {
                content = atob(data.encrypted_content);
            }
        }
        
        addToHistory(content, contentType, data.from_name);
        
        const typeEmoji = contentType === 'image' ? '🖼️' : '📝';
        const lockEmoji = isEncrypted ? '🔐' : '';
        showNotification(`${typeEmoji}${lockEmoji} Received from ${data.from_name}`);
        
        // Play notification sound
        playNotificationSound();
    } catch (err) {
        console.error('[🔐] Failed to process received data:', err);
        showNotification('⚠️ Failed to process data', 'error');
    }
}

function displayReceivedContent() {
    const container = document.getElementById('receivedContent');
    const copyAllBtn = document.getElementById('copyAllBtn');
    
    if (clipboardHistory.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>📭 No content received yet</p>
                <p style="font-size: 0.9em; margin-top: 10px;">Content from your desktop will appear here.<br>Tap to copy to clipboard.</p>
            </div>
        `;
        copyAllBtn.style.display = 'none';
        return;
    }
    
    // Show Copy All button when there's content
    copyAllBtn.style.display = 'inline-block';

    container.innerHTML = clipboardHistory.map((item, index) => {
        const date = new Date(item.timestamp);
        const isImage = item.contentType === 'image';
        
        if (isImage) {
            return `
                <div class="clipboard-item" onclick="downloadImage(${index})">
                    <div class="clipboard-item-time">
                        🖼️ ${date.toLocaleTimeString()} - from ${item.from}
                    </div>
                    <img src="${item.content}" class="clipboard-item-image" alt="Clipboard image">
                    <div style="font-size: 0.8em; color: #666; margin-top: 5px;">Tap to download</div>
                </div>
            `;
        } else {
            return `
                <div class="clipboard-item" onclick="copyToClipboard(${index})">
                    <div class="clipboard-item-time">
                        📝 ${date.toLocaleTimeString()} - from ${item.from}
                    </div>
                    <div class="clipboard-item-content">${escapeHtml(item.content)}</div>
                </div>
            `;
        }
    }).join('');
}

// Helper function for clipboard operations with fallback
function writeToClipboard(text) {
    return navigator.clipboard.writeText(text).catch(() => {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        return Promise.resolve();
    });
}

function copyToClipboard(index) {
    const item = clipboardHistory[index];
    if (!item || item.contentType !== 'text') return;
    
    writeToClipboard(item.content).then(() => {
        showNotification('✅ Copied to clipboard!');
    });
}

function copyAllContent() {
    const textItems = clipboardHistory.filter(item => item.contentType !== 'image');
    const allText = textItems.map(item => item.content).join('\n\n---\n\n');
    
    if (!allText) {
        showNotification('⚠️ No text content to copy', 'error');
        return;
    }
    
    writeToClipboard(allText).then(() => {
        showNotification(`✅ Copied ${textItems.length} items!`);
    });
}

function downloadImage(index) {
    const item = clipboardHistory[index];
    if (!item || item.contentType !== 'image') return;
    
    // Create download link
    const link = document.createElement('a');
    link.href = item.content;
    link.download = `clipboard-image-${Date.now()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showNotification('✅ Image downloaded!');
}

function updateDevicesList(devices) {
    const list = document.getElementById('devicesList');
    
    if (!devices || devices.length === 0) {
        list.innerHTML = '<li class="empty-state">No devices connected</li>';
        return;
    }

    // Show all devices including self
    list.innerHTML = devices
        .map(device => {
            const icon = device.deviceType === 'desktop' ? '🖥️' : '📱';
            const isSelf = device.deviceId === deviceId;
            const nameDisplay = isSelf ? `${escapeHtml(device.deviceName)} (You)` : escapeHtml(device.deviceName);
            
            return `
                <li class="device-item">
                    <span class="device-icon">${icon}</span>
                    <div class="device-info">
                        <div class="device-name">${nameDisplay}</div>
                        <div class="device-type">${device.deviceType}</div>
                    </div>
                </li>
            `;
        }).join('');
}

function updateStatus(text, connected) {
    document.getElementById('statusText').textContent = text;
    const indicator = document.getElementById('statusIndicator');
    if (connected) {
        indicator.classList.add('connected');
    } else {
        indicator.classList.remove('connected');
    }
}

function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = 'notification show';
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function saveCredentials(roomId, deviceName, password = '') {
    localStorage.setItem('clipboard_sync_credentials', JSON.stringify({
        roomId,
        deviceName,
        password
    }));
}

function loadCredentials() {
    const saved = localStorage.getItem('clipboard_sync_credentials');
    return saved ? JSON.parse(saved) : null;
}

function clearCredentials() {
    localStorage.removeItem('clipboard_sync_credentials');
}

function toggleSound() {
    soundEnabled = !soundEnabled;
    const btn = document.getElementById('soundToggle');
    btn.textContent = soundEnabled ? '🔊' : '🔇';
    btn.title = soundEnabled ? 'Sound on - click to mute' : 'Sound off - click to unmute';
    
    // Play a test sound if enabling
    if (soundEnabled) {
        playNotificationSound();
    }
}

function disconnect() {
    if (socket && socket.connected) {
        socket.disconnect();
    }
    
    // Clear credentials
    clearCredentials();
    
    // Reset state
    roomId = null;
    deviceName = null;
    deviceId = null;
    roomPassword = '';
    clipboardHistory = [];
    encryptionEnabled = true;
    
    // Reset crypto
    if (typeof clipboardCrypto !== 'undefined') {
        clipboardCrypto.key = null;
        clipboardCrypto.roomId = null;
        clipboardCrypto.password = null;
    }
    
    // Clear UI
    document.getElementById('receivedContent').innerHTML = `
        <div class="empty-state">
            <p>📭 No content yet</p>
            <p style="font-size: 0.9em; margin-top: 10px;">Content from other devices will appear here.<br>Tap to copy to clipboard.</p>
        </div>
    `;
    document.getElementById('devicesList').innerHTML = '';
    document.getElementById('copyAllBtn').style.display = 'none';
    
    // Show connection modal
    document.getElementById('connectionModal').classList.add('show');
    
    // Clear input fields for fresh start
    document.getElementById('roomIdInput').value = '';
    document.getElementById('roomPasswordInput').value = '';
    document.getElementById('deviceNameInput').value = '';
    
    updateStatus('Disconnected', false);
    showNotification('👋 Disconnected - enter new credentials');
}

// Auto-reconnect on page visibility change
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && socket && !socket.connected) {
        console.log('[→] Page visible, reconnecting...');
        socket.connect();
    }
});
