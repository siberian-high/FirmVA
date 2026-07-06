# FirmVA — 멀티 에이전트 기반 펌웨어 취약점 진단 시스템
> ⚠️ 본 프로젝트는 **본인이 소유·통제하는 안전한 실습 환경**에서만 사용하십시오.


## 1. 개요
**FirmVA란** 블랙박스 방식으로 펌웨어 바이너리 파일을 분석하고, <br/>
OWASP ISTG-FW 항목을 기준으로 취약점 후보를 생성 및 판정 후 보고서 작성까지 수행하는 <br/> 
멀티 에이전트 기반 펌웨어 취약점 진단 시스템입니다. <br/>
<br/>
<br/>

## 2. 실행 방법: 데모 테스트 (DEMO_MODE=true)

```bash
# 1) 가상환경 생성 및 의존성 설치
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2) 환경변수 파일 준비 (데모는 API 키 없이도 동작)
cp .env.example .env        # DEMO_MODE=true 설정 (기본값)

# 3) 실행 (데모 데이터로 전체 파이프라인 시연)
python run.py demo.bin
```
<br/>
<br/>

## 3.실행 방법: API 사용 (DEMO_MODE=false)
```bash
# 1) run.py 실행
python run.py data/input/*.bin
```

```bash
# 2) FastAPI 로 .bin 업로드 실행
uvicorn src.fastapi.server:app --port 8000
# 다른 터미널에서:
curl -F "file=@data/input/*.bin" http://127.0.0.1:8000/scan
```
<br/>
<br/>

## 4. 에이전트별 역할 및 데이터 형식

에이전트는 실행 결과를 **JSON** 형식으로 저장 후, Orchestrator 를 거쳐 다음 에이전트로 넘깁니다. <br/>
데이터 형식은 **src/schemas.py** 에 Pydantic 으로 고정되어 있습니다.

| # | 에이전트 | 사용 도구 | 입력 | 출력(JSON) | 다음 대상 |
|---|----------|------|------|-----------|-----------|
| 2 | Analysis | binwalk(CLI) | `.bin` | `ExtractResult` (부트로더/커널/파일시스템) | Static |
| 3 | Static Analysis | **Ghidra 공개 MCP** | rootfs | `StaticRaw` (임포트/문자열/위험함수) → **Storage 저장** | Candidate(정적)+Surface (병렬) |
| 4-1 | Candidate(정적) | OpenAI API | Storage 의 `StaticRaw` | `Finding[]` (취약 판정만) | Report |
| 4-2 | Attack Surface | 규칙 기반 | Storage 의 `StaticRaw` | `AttackSurface` (진입점+인증태깅) | Dynamic |
| 5 | Dynamic Analysis | **QEMU 자체 MCP** | `AttackSurface` | `DynamicRaw` (관찰결과 / 새 진입점 별도기록) | Candidate(동적) |
| 6 | Candidate(동적) | ChatGPT | `DynamicRaw.observations` | `Finding[]` (취약 판정만) | Report |
| 7 | Report | — | `Finding[]` 전체 | `report.txt` + CLI | 끝 |
<br/>
> **핵심 규칙**
- `StaticRaw`는 Orchestrator의 공유 저장소(`data/storage/static_raw.json`)에 저장되어
  Candidate 및 Attack Surface 가 **재사용**합니다. 
- Dynamic 이 새로 찾은 진입점(`new_entrypoints`)은 Candidate 로 넘기지 않고,
  `data/storage/new_entrypoints.json`에 **별도 기록**합니다.
- Candidate 는 **취약으로 판정된 것만** Report 로 넘깁니다.
---
<br/>
<br/>

## 5. 취약점 진단 기준: OWASP ISTG-FW
OWASP ISTG-FW 카테고리를 취약점 후보 생성 및 판정 기준으로 사용합니다. <br/>
OWASP ISTG-FW 카테고리 중, 아래를 **제외**한 총 **12개** 항목만을 사용합니다. <br/><br/>
각 항목은 `src/istgfw.py` 에 정의되어 있습니다.

> **제외 항목**

`ISTG-FW[UPDT]-*` 6개 + `ISTG-FW[INST]-CRYPT-001` 1개

<br/>

> **사용 항목**

| 정적 9개 (Candidate 정적) | 동적 3개 (Candidate 동적) |
|---|---|
| ISTG-FW-INFO-001/002/003 | ISTG-FW[INST]-AUTHZ-001 |
| ISTG-FW-CONF-001/002 | ISTG-FW[INST]-AUTHZ-002 |
| ISTG-FW-SCRT-001/002/003 | ISTG-FW[INST]-INFO-001 |
| ISTG-FW-CRYPT-001 | |

<br/>
<br/>



## 6. 디렉터리 구조

```
FirmVA/
├── run.py                  # CLI 진입점
├── requirements.txt
├── .env.example            # .env 민감 정보 분리
├── .gitignore
├── src/
│   ├── config.py             # 설정/경로/.env 로드
│   ├── schemas.py            # 에이전트 간 JSON 형식 정의
│   ├── istgfw.py             # OWASP ISTG-FW 카테고리
│   ├── state.py              # LangGraph 공유 상태리
│   ├── orchestrator.py       # Orchestrator 통신 관리
│   ├── store.py              # 공유 저장소 처리
│   ├── llm.py                # OpenAI API 호출
│   ├── agents/
│   │   ├── analysis.py      # 2  Analysis (binwalk) 
│   │   ├── static.py        # 3  Static (Ghidra MCP)
│   │   ├── surface.py       # 4-2 Attack Surface
│   │   ├── dynamic.py       # 5  Dynamic (QEMU MCP)
│   │   ├── candidates/      # 4-1 / 6  Candidate (항목별 하위 에이전트)
│   │   │   ├── base.py       # 공통 판정 엔진(judge)
│   │   │   ├── __init__.py   # 오케스트레이터 호출부(run_static/dynamic)
│   │   │   ├── static/          # 정적 9개 항목
│   │   │   │   ├── info.py       # INFO-001/002/003
│   │   │   │   ├── conf.py       # CONF-001/002
│   │   │   │   ├── scrt.py       # SCRT-001/002/003
│   │   │   │   └── crypt.py      # CRYPT-001
│   │   │   └── dynamic/         # 동적 3개 항목
│   │   │       ├── authz.py       # AUTHZ-001/002서
│   │   │       └── info.py        # INST-INFO-001
│   │   └── report.py          # 7 보고서 생성
│   ├── tools/
│   │   ├── binwalk_tool.py    # binwalk CLI 래퍼
│   │   ├── ghidra_mcp.py      # Ghidra 공개 MCP 클라이언트
│   │   └── qemu_mcp.py        # QEMU 자체 MCP 클라이언트
│   └── fastapi/
│       └── server.py        # FastAPI .bin 업로드
├── test/
│   └── demo.py              # 데모 테스트용 데이터
├── mcp/
│   └── qemu/                # 자체 구축 QEMU MCP 서버
│       ├── server.py
│       └── README.md
├── data/
│   ├── input/              # 업로드된 .bin 저장
│   ├── work/               # binwalk 결과물 저장
│   └── storage/            # 공유 저장소(json)
└── out/                     # 보고서 저장(.txt)
 ``` 



