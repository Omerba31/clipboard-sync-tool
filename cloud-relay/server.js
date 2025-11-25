// cloud-relay/server.js
/**
 * Cloud Relay Server for Clipboard Sync
 * 
 * This server acts as a relay between desktop and mobile devices,
 * forwarding encrypted clipboard data without decrypting it.
 * 
 * Architecture:
 * Desktop ←→ Cloud Relay ←→ Mobile Web App
 * 
 * The relay simply forwards encrypted data - it never sees plaintext.
 */

const express = require('express');
const http = require('http');
const socketIO = require('socket.io');
const cors = require('cors');
const compression = require('compression');
const rateLimit = require('express-rate-limit');
const path = require('path');

const app = express();

// Trust proxy (required for Railway, Heroku, etc.)
app.set('trust proxy', 1);

const server = http.createServer(app);

// Constants for free tier protection
const MAX_CONNECTIONS = 50; // Max simultaneous connections
const MAX_MESSAGE_SIZE = 100 * 1024; // 100KB max per message
const MAX_MESSAGES_PER_MINUTE = 60; // 60 messages per minute per device
const BANDWIDTH_LIMIT_MB = 150; // 150MB/month (leave buffer from 160GB)
const BANDWIDTH_RESET_HOURS = 720; // 30 days

// Tracking variables
let totalBandwidthUsed = 0;
let bandwidthResetTime = Date.now() + (BANDWIDTH_RESET_HOURS * 60 * 60 * 1000);
let messageCount = new Map(); // Track messages per device

// Configure Socket.IO with CORS for cross-origin connections
const io = socketIO(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST'],
    credentials: true
  },
  pingTimeout: 60000,
  pingInterval: 25000
});

// Rate limiting middleware
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.',
  standardHeaders: true,
  legacyHeaders: false,
});

// Middleware
app.use(cors());
app.use(compression());
app.use(express.json({ limit: '100kb' })); // Limit request size
app.use(limiter);
app.use(express.static('public'));

// Store device connections and rooms
const devices = new Map();
const rooms = new Map();

// Reset bandwidth counter monthly
setInterval(() => {
  if (Date.now() >= bandwidthResetTime) {
    console.log('[📊] Resetting bandwidth counter');
    totalBandwidthUsed = 0;
    bandwidthResetTime = Date.now() + (BANDWIDTH_RESET_HOURS * 60 * 60 * 1000);
  }
}, 60 * 60 * 1000); // Check every hour

// Helper function to check bandwidth limit
function checkBandwidthLimit(dataSize) {
  const newTotal = totalBandwidthUsed + dataSize;
  const limitBytes = BANDWIDTH_LIMIT_MB * 1024 * 1024;
  
  if (newTotal > limitBytes) {
    const timeUntilReset = new Date(bandwidthResetTime).toLocaleString();
    return {
      allowed: false,
      message: `Monthly bandwidth limit reached (${BANDWIDTH_LIMIT_MB}MB). Resets: ${timeUntilReset}`
    };
  }
  
  totalBandwidthUsed = newTotal;
  return { allowed: true };
}

// Helper function to check message rate limit
function checkMessageRateLimit(socketId) {
  const now = Date.now();
  const record = messageCount.get(socketId) || { count: 0, resetTime: now + 60000 };
  
  // Reset counter if time window passed
  if (now >= record.resetTime) {
    record.count = 0;
    record.resetTime = now + 60000;
  }
  
  record.count++;
  messageCount.set(socketId, record);
  
  if (record.count > MAX_MESSAGES_PER_MINUTE) {
    return {
      allowed: false,
      message: 'Rate limit exceeded. Please wait a moment.'
    };
  }
  
  return { allowed: true };
}

// Health check endpoint (for Fly.io)
app.get('/health', (req, res) => {
  const bandwidthUsedMB = (totalBandwidthUsed / (1024 * 1024)).toFixed(2);
  const bandwidthPercentage = ((totalBandwidthUsed / (BANDWIDTH_LIMIT_MB * 1024 * 1024)) * 100).toFixed(1);
  
  res.json({ 
    status: 'healthy',
    timestamp: new Date().toISOString(),
    connections: devices.size,
    rooms: rooms.size,
    bandwidth: {
      used_mb: bandwidthUsedMB,
      limit_mb: BANDWIDTH_LIMIT_MB,
      percentage: bandwidthPercentage,
      resets: new Date(bandwidthResetTime).toISOString()
    }
  });
});

// Stats endpoint
app.get('/api/stats', (req, res) => {
  const bandwidthUsedMB = (totalBandwidthUsed / (1024 * 1024)).toFixed(2);
  
  res.json({
    devices: devices.size,
    rooms: rooms.size,
    uptime: process.uptime(),
    bandwidth: {
      used_mb: bandwidthUsedMB,
      limit_mb: BANDWIDTH_LIMIT_MB,
      percentage: ((totalBandwidthUsed / (BANDWIDTH_LIMIT_MB * 1024 * 1024)) * 100).toFixed(1)
    },
    limits: {
      max_connections: MAX_CONNECTIONS,
      max_message_size_kb: MAX_MESSAGE_SIZE / 1024,
      max_messages_per_minute: MAX_MESSAGES_PER_MINUTE
    }
  });
});

// Socket.IO connection handling
io.on('connection', (socket) => {
  // Check connection limit
  if (devices.size >= MAX_CONNECTIONS) {
    console.log(`[!] Connection rejected: limit reached (${MAX_CONNECTIONS})`);
    socket.emit('error', { 
      message: 'Server at capacity. Please try again later.',
      code: 'MAX_CONNECTIONS'
    });
    socket.disconnect();
    return;
  }
  
  console.log(`[+] Device connected: ${socket.id}`);
  
  // Device registration
  socket.on('register', (data) => {
    const { deviceId, deviceName, deviceType, roomId } = data;
    
    devices.set(socket.id, {
      socketId: socket.id,
      deviceId,
      deviceName,
      deviceType, // 'desktop' or 'mobile'
      roomId,
      connectedAt: new Date()
    });
    
    // Join room
    socket.join(roomId);
    
    // Add to room tracking
    if (!rooms.has(roomId)) {
      rooms.set(roomId, new Set());
    }
    rooms.get(roomId).add(socket.id);
    
    console.log(`[→] ${deviceName} (${deviceType}) joined room: ${roomId}`);
    
    // Notify other devices in room
    socket.to(roomId).emit('device_joined', {
      deviceId,
      deviceName,
      deviceType
    });
    
    // Send list of devices in room
    const roomDevices = Array.from(rooms.get(roomId) || [])
      .map(sid => devices.get(sid))
      .filter(d => d);
    
    socket.emit('room_devices', roomDevices);
  });
  
  // Forward encrypted clipboard data
  socket.on('clipboard_data', (data) => {
    const device = devices.get(socket.id);
    if (!device) return;
    
    const { roomId } = device;
    const { encrypted_content, content_type, timestamp } = data;
    
    // Validate message size
    const messageSize = JSON.stringify(data).length;
    if (messageSize > MAX_MESSAGE_SIZE) {
      socket.emit('error', {
        message: `Message too large (${(messageSize/1024).toFixed(1)}KB). Max: ${MAX_MESSAGE_SIZE/1024}KB`,
        code: 'MESSAGE_TOO_LARGE'
      });
      return;
    }
    
    // Check message rate limit
    const rateCheck = checkMessageRateLimit(socket.id);
    if (!rateCheck.allowed) {
      socket.emit('error', {
        message: rateCheck.message,
        code: 'RATE_LIMIT'
      });
      return;
    }
    
    // Check bandwidth limit
    const bandwidthCheck = checkBandwidthLimit(messageSize);
    if (!bandwidthCheck.allowed) {
      socket.emit('error', {
        message: bandwidthCheck.message,
        code: 'BANDWIDTH_LIMIT'
      });
      // Notify all connected devices
      io.emit('server_message', {
        type: 'warning',
        message: 'Server bandwidth limit reached. Service will resume next month.'
      });
      return;
    }
    
    console.log(`[📋] ${device.deviceName} sent ${content_type} (${messageSize} bytes) - Bandwidth: ${(totalBandwidthUsed/(1024*1024)).toFixed(2)}MB/${BANDWIDTH_LIMIT_MB}MB`);
    
    // Forward to all other devices in the room
    socket.to(roomId).emit('clipboard_data', {
      from_device: device.deviceId,
      from_name: device.deviceName,
      from_type: device.deviceType,
      encrypted_content,
      content_type,
      timestamp: timestamp || Date.now()
    });
  });
  
  // Get devices list
  socket.on('get_devices', () => {
    const device = devices.get(socket.id);
    if (!device) return;
    
    const { roomId } = device;
    const roomDevices = Array.from(rooms.get(roomId) || [])
      .map(sid => devices.get(sid))
      .filter(d => d);
    
    socket.emit('room_devices', roomDevices);
  });
  
  // Ping/pong for connection health
  socket.on('ping', () => {
    socket.emit('pong', { timestamp: Date.now() });
  });
  
  // Device disconnection
  socket.on('disconnect', () => {
    const device = devices.get(socket.id);
    if (device) {
      console.log(`[-] ${device.deviceName} disconnected`);
      
      // Remove from room
      if (rooms.has(device.roomId)) {
        rooms.get(device.roomId).delete(socket.id);
        if (rooms.get(device.roomId).size === 0) {
          rooms.delete(device.roomId);
        }
      }
      
      // Notify other devices
      socket.to(device.roomId).emit('device_left', {
        deviceId: device.deviceId,
        deviceName: device.deviceName
      });
    }
    
    devices.delete(socket.id);
    messageCount.delete(socket.id); // Clean up rate limit tracking
  });
  
  // Error handling
  socket.on('error', (error) => {
    console.error(`[!] Socket error for ${socket.id}:`, error);
  });
});

// Start server
const PORT = process.env.PORT || 8080;
server.listen(PORT, '0.0.0.0', () => {
  console.log(`
╔════════════════════════════════════════════════════════╗
║  Clipboard Sync Cloud Relay Server                    ║
║  Running on port ${PORT}                                  ║
║  Ready to relay encrypted clipboard data              ║
╚════════════════════════════════════════════════════════╝
  `);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('[!] SIGTERM received, closing server...');
  server.close(() => {
    console.log('[✓] Server closed');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('[!] SIGINT received, closing server...');
  server.close(() => {
    console.log('[✓] Server closed');
    process.exit(0);
  });
});
