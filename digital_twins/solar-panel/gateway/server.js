const express = require('express');
const http = require('http');
const net = require('net');
const { Server } = require('socket.io');

const WS_PORT = 4000;
const TCP_PORT = 4001;
const HARDWARE_TX_DELAY_MS = Math.max(0, Number(process.env.HARDWARE_TX_DELAY_MS || 0));
const HARDWARE_RX_DELAY_MS = Math.max(0, Number(process.env.HARDWARE_RX_DELAY_MS || 0));

function parsePowerFrame(line) {
  const text = line.trim();
  const match = text.match(/^>P:([-+]?\d*\.?\d+)$/);
  if (!match) {
    return null;
  }

  const value = Number(match[1]);
  if (Number.isNaN(value)) {
    return null;
  }

  return value;
}

class MockTcpHardwareClient {
  constructor() {
    this.socket = null;
    this.buffer = '';
    this.onDataHandler = null;
  }

  attachSocket(socket) {
    this.socket = socket;
    this.buffer = '';

    socket.on('data', (chunk) => {
      this.buffer += chunk.toString('utf8');
      while (this.buffer.includes('\n')) {
        const idx = this.buffer.indexOf('\n');
        const line = this.buffer.slice(0, idx);
        this.buffer = this.buffer.slice(idx + 1);
        if (this.onDataHandler) {
          this.onDataHandler(line);
        }
      }
    });

    socket.on('close', () => {
      if (this.socket === socket) {
        this.socket = null;
        this.buffer = '';
      }
      console.log('Hardware client disconnected');
    });

    socket.on('error', (error) => {
      console.error('Hardware socket error:', error.message);
    });
  }

  write(frame) {
    if (!this.socket || this.socket.destroyed) {
      return;
    }

    if (HARDWARE_TX_DELAY_MS > 0) {
      setTimeout(() => {
        if (!this.socket || this.socket.destroyed) {
          return;
        }
        this.socket.write(frame);
      }, HARDWARE_TX_DELAY_MS);
      return;
    }

    this.socket.write(frame);
  }

  onData(handler) {
    this.onDataHandler = handler;
  }
}

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: { origin: "*" },
  transports: ["polling", "websocket"], // Allow both
  pingTimeout: 120000,  // 2 minutes (vital for hotspots)
  pingInterval: 30000,
  connectTimeout: 45000
});

let activeControlMode = 'forward';
let manualSetpoint = { pan: 90, tilt: 45 };

app.get('/health', (_req, res) => {
  res.json({ status: 'ok' });
});

const hardwareClient = new MockTcpHardwareClient();
hardwareClient.onData((line) => {
  const power = parsePowerFrame(line);
  if (power === null) {
    return;
  }

  const emitTelemetry = () => {
    io.emit('telemetry_update', { current_power: power });
  };

  if (HARDWARE_RX_DELAY_MS > 0) {
    setTimeout(emitTelemetry, HARDWARE_RX_DELAY_MS);
    return;
  }

  emitTelemetry();
});

const tcpServer = net.createServer((socket) => {
  console.log(`Hardware connected from ${socket.remoteAddress}:${socket.remotePort}`);
  hardwareClient.attachSocket(socket);
});

tcpServer.listen(TCP_PORT, () => {
  console.log(`Gateway TCP hardware server listening on port ${TCP_PORT}`);
});

/*
Hardware swap (TCP mock -> real Arduino with serialport):
1) Remove the net.createServer block above.
2) Install serialport: npm install serialport
3) Open a serial port and bridge bytes to/from hardwareClient logic.

Example outline:
const { SerialPort } = require('serialport');
const serial = new SerialPort({ path: '/dev/ttyUSB0', baudRate: 115200 });
serial.on('data', (chunk) => { ...same line-buffer parsing... });
hardwareClient.write = (frame) => serial.write(frame);
*/

io.on('connection', (socket) => {
  console.log(`Socket.io client connected: ${socket.id}`);

  socket.emit('control_mode', { mode: activeControlMode });

  socket.on('control_mode', (payload) => {
    const nextMode = payload && payload.mode === 'inverse' ? 'inverse' : 'forward';
    activeControlMode = nextMode;
    io.emit('control_mode', { mode: activeControlMode });

    if (activeControlMode === 'forward') {
      const frame = `<${manualSetpoint.pan},${manualSetpoint.tilt}>\n`;
      hardwareClient.write(frame);
    }
  });

  socket.on('set_angles', (payload) => {
    if (!payload || typeof payload.pan !== 'number' || typeof payload.tilt !== 'number') {
      return;
    }

    if (activeControlMode !== 'forward') {
      activeControlMode = 'forward';
      io.emit('control_mode', { mode: activeControlMode });
    }

    manualSetpoint = {
      pan: Number(payload.pan),
      tilt: Number(payload.tilt),
    };

    const frame = `<${payload.pan},${payload.tilt}>\n`;
    hardwareClient.write(frame);
  });

  socket.on('update_target_power', (payload) => {
    const rawTarget = payload && typeof payload.target === 'number' ? payload.target : null;
    if (rawTarget === null || Number.isNaN(rawTarget)) {
      return;
    }

    if (activeControlMode !== 'inverse') {
      activeControlMode = 'inverse';
      io.emit('control_mode', { mode: activeControlMode });
    }

    const target = Number(rawTarget);
    io.emit('update_target_power', { target });
  });

  // Backward compatibility with older emitter name.
  socket.on('set_target_power', (payload) => {
    const rawTarget = payload && typeof payload.target === 'number' ? payload.target : null;
    if (rawTarget === null || Number.isNaN(rawTarget)) {
      return;
    }

    if (activeControlMode !== 'inverse') {
      activeControlMode = 'inverse';
      io.emit('control_mode', { mode: activeControlMode });
    }

    const target = Number(rawTarget);
    io.emit('update_target_power', { target });
  });

  socket.on('model_update', (payload) => {
    if (!payload || typeof payload !== 'object') {
      return;
    }

    const pan = typeof payload.target_pan === 'number' ? payload.target_pan : null;
    const tilt = typeof payload.target_tilt === 'number' ? payload.target_tilt : null;
    const achievable = payload.achievable === false ? false : true;

    const update = {
      target_pan: pan,
      target_tilt: tilt,
      achievable,
    };

    io.emit('model_update', update);
    io.emit('optimization_result', update);

    if (activeControlMode === 'inverse' && pan !== null && tilt !== null) {
      const frame = `<${pan},${tilt}>\n`;
      hardwareClient.write(frame);
    }
  });

  socket.on('disconnect', () => {
    console.log(`Socket.io client disconnected: ${socket.id}`);
  });
});

server.listen(WS_PORT, () => {
  console.log(`Gateway Socket.io server listening on port ${WS_PORT}`);
});

setInterval(() => {
  if (activeControlMode !== 'forward') {
    return;
  }

  const frame = `<${manualSetpoint.pan},${manualSetpoint.tilt}>\n`;
  hardwareClient.write(frame);
}, 1000);
