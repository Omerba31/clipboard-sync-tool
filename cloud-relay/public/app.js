// Mobile Web App JavaScript
let socket = null;
let roomId = null;
let deviceName = null;
let deviceId = null;
let clipboardHistory = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Load saved credentials
    const saved = loadCredentials();
    if (saved) {
        document.getElementById('roomIdInput').value = saved.roomId;
        document.getElementById('deviceNameInput').value = saved.deviceName;
    }
});

function connect() {
    roomId = document.getElementById('roomIdInput').value.trim();
    deviceName = document.getElementById('deviceNameInput').value.trim();

    if (!roomId || !deviceName) {
        showNotification('⚠️ Please enter Room ID and Device Name', 'error');
        return;
    }

    // Generate device ID
    deviceId = 'mobile-' + Math.random().toString(36).substr(2, 9);

    // Save credentials
    saveCredentials(roomId, deviceName);

    // Close modal
    document.getElementById('connectionModal').classList.remove('show');

    // Connect to server
    connectToServer();
}

function connectToServer() {
    updateStatus('Connecting...', false);

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

        // Register device
        socket.emit('register', {
            deviceId,
            deviceName,
            deviceType: 'mobile',
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
    });

    socket.on('device_left', (device) => {
        console.log('[-] Device left:', device.deviceName);
        showNotification(`👋 ${device.deviceName} left`);
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

function sendToDesktop() {
    const text = document.getElementById('sendText').value.trim();
    
    if (!text) {
        showNotification('⚠️ Please enter some text', 'error');
        return;
    }

    if (!socket || !socket.connected) {
        showNotification('❌ Not connected to server', 'error');
        return;
    }

    // Send to relay (NOTE: In production, this should be encrypted!)
    socket.emit('clipboard_data', {
        encrypted_content: btoa(text), // Base64 encode (NOT real encryption!)
        content_type: 'text',
        timestamp: Date.now()
    });

    showNotification('✅ Sent to desktop!');
    document.getElementById('sendText').value = '';
}

function receiveFromDesktop(data) {
    const content = atob(data.encrypted_content); // Base64 decode
    
    // Add to history
    clipboardHistory.unshift({
        content,
        timestamp: data.timestamp || Date.now(),
        from: data.from_name
    });

    // Keep only last 10 items
    if (clipboardHistory.length > 10) {
        clipboardHistory.pop();
    }

    // Update UI
    displayReceivedContent();
    showNotification(`📥 Received from ${data.from_name}`);
}

function displayReceivedContent() {
    const container = document.getElementById('receivedContent');
    
    if (clipboardHistory.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>📭 No content received yet</p>
            </div>
        `;
        return;
    }

    container.innerHTML = clipboardHistory.map(item => {
        const date = new Date(item.timestamp);
        return `
            <div class="clipboard-item" onclick="copyToClipboard('${item.content.replace(/'/g, "\\'")}')">
                <div class="clipboard-item-time">
                    ${date.toLocaleTimeString()} - from ${item.from}
                </div>
                <div class="clipboard-item-content">${escapeHtml(item.content)}</div>
            </div>
        `;
    }).join('');
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('✅ Copied to clipboard!');
    }).catch(() => {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        showNotification('✅ Copied to clipboard!');
    });
}

function updateDevicesList(devices) {
    const list = document.getElementById('devicesList');
    
    if (!devices || devices.length === 0) {
        list.innerHTML = '<li class="empty-state">No other devices connected</li>';
        return;
    }

    list.innerHTML = devices
        .filter(d => d.deviceId !== deviceId) // Don't show self
        .map(device => {
            const icon = device.deviceType === 'desktop' ? '🖥️' : '📱';
            return `
                <li class="device-item">
                    <span class="device-icon">${icon}</span>
                    <div class="device-info">
                        <div class="device-name">${escapeHtml(device.deviceName)}</div>
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

function saveCredentials(roomId, deviceName) {
    localStorage.setItem('clipboard_sync_credentials', JSON.stringify({
        roomId,
        deviceName
    }));
}

function loadCredentials() {
    const saved = localStorage.getItem('clipboard_sync_credentials');
    return saved ? JSON.parse(saved) : null;
}

// Auto-reconnect on page visibility change
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && socket && !socket.connected) {
        console.log('[→] Page visible, reconnecting...');
        socket.connect();
    }
});
