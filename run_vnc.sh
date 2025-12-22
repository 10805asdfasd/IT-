#!/usr/bin/env bash
# Simple script to install Xvfb, x11vnc and a minimal window manager (fluxbox),
# then start an X server on :99 and expose it via VNC on port 5900.

set -e

if [ "$(id -u)" -ne 0 ]; then
  echo "이 스크립트는 패키지 설치를 위해 root 권한이 필요합니다. sudo로 실행하세요."
  echo "예: sudo ./run_vnc.sh"
  exit 1
fi

apt-get update
apt-get install -y xvfb x11vnc fluxbox || {
  echo "패키지 설치 실패. 네트워크나 권한을 확인하세요."; exit 1;
}

X_DISPLAY=":99"
SCREEN_GEOM="1024x768x24"

echo "Starting Xvfb on ${X_DISPLAY}..."
Xvfb ${X_DISPLAY} -screen 0 ${SCREEN_GEOM} -nolisten tcp &
XVFB_PID=$!
sleep 0.5

export DISPLAY=${X_DISPLAY}

echo "Starting a lightweight window manager (fluxbox)..."
fluxbox &

echo "Starting x11vnc on ${X_DISPLAY} (port 5900, no password)..."
x11vnc -display ${X_DISPLAY} -nopw -forever -shared -rfbport 5900 &
VNC_PID=$!

echo
echo "Xvfb PID: ${XVFB_PID}, x11vnc PID: ${VNC_PID}"
echo "VNC server is running on port 5900. Connect with a VNC client to <HOST>:5900."
echo "To run the game in this virtual display, in another shell run:" 
echo "  export DISPLAY=${X_DISPLAY}"
echo "  SDL_VIDEODRIVER=x11 python3 enn.py"
echo
echo "To stop the servers, kill the PIDs:"
echo "  kill ${VNC_PID} ${XVFB_PID}"

echo "Done."
