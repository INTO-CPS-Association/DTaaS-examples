#!/usr/bin/env python3
"""Mock solar panel hardware using Arduino-style text frames over TCP.

Optimized for high-latency mobile hotspots with TCP Keep-Alives.
"""

from __future__ import annotations

import math
import socket
import time

GATEWAY_HOST = "127.0.0.1"
GATEWAY_PORT = 4001

SUN_PAN = 90.0
SUN_TILT = 45.0
MAX_POWER_W = 20.0

# Delay knobs (seconds). Keep at 0.0 for instant mock behavior.
# Set these to simulate real communication and actuator latency.
CMD_RX_APPLY_DELAY_SEC = 0.0
POWER_TX_DELAY_SEC = 0.0

def parse_command(command: str) -> tuple[float, float] | None:
    text = command.strip()
    if not (text.startswith("<") and text.endswith(">")):
        return None

    payload = text[1:-1]
    parts = payload.split(",")
    if len(parts) != 2:
        return None

    try:
        pan = float(parts[0].strip())
        tilt = float(parts[1].strip())
    except ValueError:
        return None

    return pan, tilt

def calculate_power(pan: float, tilt: float) -> float:
    # Calculate the max physical distance possible from the sun's position
    max_dist = max(
        math.hypot(0 - SUN_PAN, 0 - SUN_TILT),
        math.hypot(180 - SUN_PAN, 0 - SUN_TILT),
        math.hypot(0 - SUN_PAN, 90 - SUN_TILT),
        math.hypot(180 - SUN_PAN, 90 - SUN_TILT)
    )
    
    distance = math.hypot(pan - SUN_PAN, tilt - SUN_TILT)
    
    # Normalize dynamically: the furthest possible point will perfectly hit 0.0W
    normalized = max(0.0, 1.0 - (distance / max_dist))
    return MAX_POWER_W * normalized

def run_session(conn: socket.socket) -> None:
    buffer = ""
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                print("Gateway disconnected (Zero bytes received)")
                return

            buffer += data.decode("utf-8", errors="ignore")
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                parsed = parse_command(line)
                if parsed is None:
                    continue

                pan, tilt = parsed
                if CMD_RX_APPLY_DELAY_SEC > 0:
                    time.sleep(CMD_RX_APPLY_DELAY_SEC)
                power = calculate_power(pan, tilt)
                response = f">P:{power:.2f}\n"
                if POWER_TX_DELAY_SEC > 0:
                    time.sleep(POWER_TX_DELAY_SEC)
                conn.sendall(response.encode("utf-8"))
        except socket.timeout:
            continue
        except Exception as e:
            print(f"Session error: {e}")
            return

def main() -> None:
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            
            if hasattr(socket, 'TCP_KEEPIDLE'):
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 10)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 5)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)

            sock.settimeout(15)
            sock.connect((GATEWAY_HOST, GATEWAY_PORT))
            
            print(f"mock_panel connected to gateway at {GATEWAY_HOST}:{GATEWAY_PORT}")
            
            with sock:
                run_session(sock)
                
        except (OSError, socket.error) as error:
            print(f"mock_panel retrying connection: {error}")
            time.sleep(3)

if __name__ == "__main__":
    main()