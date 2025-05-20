const WebSocket = require('ws');

// Replace with your backend WebSocket URL
const socket = new WebSocket('ws://localhost:8000/ws/stream');

socket.on('open', () => {
  console.log('[WS] Connected to WebSocket');
});

socket.on('message', (data) => {
  try {
    const message = JSON.parse(data);
    console.log('[WS] Received:', message);
  } catch (e) {
    console.error('[WS] Invalid JSON:', data);
  }
});

socket.on('error', (err) => {
  console.error('[WS] Error:', err);
});

socket.on('close', () => {
  console.log('[WS] Connection closed');
});

