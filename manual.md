# FirmVA 사용 매뉴얼
> ⚠️ 본 프로젝트는 **본인이 소유·통제하는 안전한 실습 환경**에서만 사용하십시오.
<br/>


## 1. 레포지터리 clone
```bash
# 1) 레포지터리 clone
git clone https://github.com/siberian-high/FirmVA.git
```
<br/>

## 2. 환경 설정
```bash
# clone한 레포지터리 경로로 이동
# 1) 가상환경 생성
python3.10 -m venv .venv

# 2) 가상환경 활성화
source .venv/bin/activate
```
<br/>


## 3. pip 패키지 설치
```bash
# requirements.txt 설치
pip install -r requirements.txt
```
<br/>


## 4. apt/snap/zip 패키지 설치
```bash
# 1) binwalk 설치
snap install binwalk

# 2) JDK v21.0.11 설치
apt install -y openjdk-21-jdk
java -version

# 3) Ghidra 설치
# 공식 배포본 v11.3.2 .zip 파일 다운로드 후 압축 해제
# 압축 해제 후 ~/ghidra_11.3.2_PUBLIC/ 생성
# https://github.com/NationalSecurityAgency/ghidra/releases?page=2#release-Ghidra_11.3.2_build
unzip <파일명>.zip

# 4) GhidraMCP 설치
# 레포지터리 클론한 경우 FirmVA/mcp/ghidra에 압축 해제 되어있으므로 생략 가능
#   .zip 파일 다운로드 후 FirmVA/mcp/ghidra에 압축 해제
#   압축 해제 후 GhidraMCP-1-4.zip(플러그인), bridge_mcp_ghidra.py 생성
#   https://github.com/LaurieWired/GhidraMCP/releases#release-1.4
unzip <파일명>.zip

# 5) GhidraMCP 플러그인 설치
#   1. Ghidra 실행
~/ghidra_11.3.2_PUBLIC/ghidraRun
#   2. File → Install Extensions → 우측 상단 + 클릭 → FirmVA/mcp/ghidra/GhidraMCP-release-1-4/GhidraMCP-1-4.zip 선택 → OK
#   3. Ghidra 재시작
#   4. 프로젝트 생성 후 대상 바이너리(binwalk로 추출한 ELF 등) import → 더블클릭해 CodeBrowser 열기
#   5. CodeBrowser에서 File → Configure → Developer → GhidraMCPPlugin 체크

# 6) Python bridge 의존성 설치 확인
source .venv/bin/activate 
pip install mcp requests

# 7)  bridge 실행 (SSE 모드)
python ~/FirmVA/mcp/ghidra/GhidraMCP-release-1-4/bridge_mcp_ghidra.py \
  --transport sse \
  --mcp-host 127.0.0.1 \
  --mcp-port 8081 \
  --ghidra-server http://127.0.0.1:8080/

# 8)  bridge 연결 확인
# bridge가 뜬 상태에서 .env 확인: GHIDRA_MCP_URL=http://127.0.0.1:8081/sse
# 그리고 tools/ghidra.py의 MCP 클라이언트가 이 URL로 붙는지 확인
```
<br/>


## 5. FirmVA 전체 실행: 데모 테스트 (DEMO_MODE=true)

```bash
# 실행 (데모 데이터로 전체 파이프라인 시연)
python run.py demo.bin
```
<br/>


## 6.FirmVA 전체 실행: API 사용 (DEMO_MODE=false)
```bash
# 1. run.py 실행
python run.py data/input/*.bin
```
  
  또는
  
```bash
# 2, FastAPI로 .bin 업로드 실행 (터미널 2개 사용)
# 1번 터미널
uvicorn src.fastapi.server:app --port 8000
# 2번 터미널
curl -F "file=@data/input/*.bin" http://127.0.0.1:8000/scan
```