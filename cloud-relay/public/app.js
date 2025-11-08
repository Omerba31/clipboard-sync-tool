// Mobile Web App JavaScript
let socket = null;
let roomId = null;
let deviceName = null;
let deviceId = null;
let clipboardHistory = [];
let selectedImage = null; // Store selected image data

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
        socket.emit('clipboard_data', {
            encrypted_content: selectedImage, // Base64 data URL
            content_type: 'image',
            timestamp: Date.now()
        });
        
        showNotification('✅ Image sent to desktop!');
        clearImage();
    }
    
    // Send text if provided
    if (text) {
        socket.emit('clipboard_data', {
            encrypted_content: btoa(text), // Base64 encode
            content_type: 'text',
            timestamp: Date.now()
        });
        
        showNotification('✅ Text sent to desktop!');
        document.getElementById('sendText').value = '';
    }
}

function receiveFromDesktop(data) {
    const contentType = data.content_type || 'text';
    let content;
    
    // Handle different content types
    if (contentType === 'image') {
        content = data.encrypted_content; // Already a data URL
    } else {
        content = atob(data.encrypted_content); // Base64 decode text
    }
    
    // Add to history
    clipboardHistory.unshift({
        content,
        contentType,
        timestamp: data.timestamp || Date.now(),
        from: data.from_name
    });

    // Keep only last 10 items
    if (clipboardHistory.length > 10) {
        clipboardHistory.pop();
    }

    // Update UI
    displayReceivedContent();
    
    const typeEmoji = contentType === 'image' ? '🖼️' : '📝';
    showNotification(`${typeEmoji} Received from ${data.from_name}`);
}

function displayReceivedContent() {
    const container = document.getElementById('receivedContent');
    
    if (clipboardHistory.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>📭 No content received yet</p>
                <p style="font-size: 0.9em; margin-top: 10px;">Content from your desktop will appear here.<br>Tap to copy to clipboard.</p>
            </div>
        `;
        return;
    }

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
                <div class="clipboard-item" onclick="copyToClipboard('${item.content.replace(/'/g, "\\'")}')">
                    <div class="clipboard-item-time">
                        📝 ${date.toLocaleTimeString()} - from ${item.from}
                    </div>
                    <div class="clipboard-item-content">${escapeHtml(item.content)}</div>
                </div>
            `;
        }
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
