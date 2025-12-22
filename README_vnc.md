설명
---
이 프로젝트는 Pygame 기반 간단 게임입니다. Codespace/헤드리스 환경에서 창을 보려면 가상 X 서버와 VNC를 사용해야 합니다.

빠른 시작
---
1. `run_vnc.sh`를 루트 권한으로 실행해 필요한 패키지를 설치하고 Xvfb와 x11vnc를 시작합니다:

```bash
sudo ./run_vnc.sh
```

2. 로컬 머신에서 VNC 클라이언트(예: TigerVNC, RealVNC)를 열고 Codespace 호스트의 포트 5900에 접속합니다. (예: `host:5900`)

3. VNC에 연결된 후, 컨테이너 안 또는 터미널에서 다음을 실행해 게임을 가상 디스플레이에서 띄웁니다:

```bash
export DISPLAY=:99
SDL_VIDEODRIVER=x11 python3 enn.py
```

중요사항
---
- 이 스크립트는 `sudo` 권한이 필요합니다.
- VNC는 암호 없이 실행되므로 네트워크 환경에서 주의하세요. 공개 네트워크에서는 포트 포워딩을 사용하거나 비밀번호를 설정하세요.

문제 해결
---
- VNC에 화면이 비어있다면 `fluxbox`가 실행중인지, `DISPLAY`가 `:99`인지 확인하세요.
- 포트 충돌이 있는 경우 `x11vnc` 옵션 `-rfbport` 값을 변경하세요.
