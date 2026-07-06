# QEMU MCP Server
  
## 개요
Ghidra와 달리, QEMU는 이 프로젝트에 적절한 공개 MCP가 존재하지 않습니다.
  
따라서, 프로젝트를 위한 QEMU MCP Server를 별도 구현해 사용합니다.

  
## 제공 도구
| 도구 | 설명 |
|------|------|
| `boot(rootfs, kernel)` | 추출한 파일시스템 사용해 QEMU versatilepb 가상 공유기 부팅 |
| `poke(url, param, payload)` | 특정 진입점(CGI URL)에 요청 보내 동작 및 크래시 관찰 |
| `trace(pid)` | strace, ltrace 사용해 실행 프로세스 추적 |
  

## 실행 방법
```bash
pip install fastmcp
sudo apt-get install qemu-system-arm      # QEMU 설치
python mcp/qemu/server.py                 # 127.0.0.1:8090 (SSE) 대기
```

QEMU 설치 후 `.env` 의 `QEMU_MCP_URL` 이 `http://127.0.0.1:8090/sse` 인지 확인합니다.
  
`DEMO_MODE=false` 로 바꾸면 `Dynamic Analysis Agent` 가 이 QEMU MCP Server를 실제 호출합니다.
  

## 기능 추가 방법
`server.py` 의 각 도구 안 `TODO` 부분에 추가할 명령을 `subprocess` 로 추가합니다.