# server.py: FastAPI 펌웨어 입력 처리
########################################################
# 펌웨어 .bin 파일을 업로드받아 진단 파이프라인을 실행하는 API 서버
# 엔드포인트:
# POST /scan   : .bin 파일을 업로드하면 저장 후 FirmVA 그래프를 실행,
#                보고서 경로와 판정 요약을 JSON으로 돌려줌

# 실행 방법:
#    uvicorn src.fastapi.server:app --reload --port 8000
#    CLI 로만 쓰고 싶으면 run.py 를 사용. API 는 파일 입력 처리 용도임
########################################################

from fastapi import FastAPI, UploadFile, File
from pathlib import Path

from .. import config
from ..orchestrator import build_graph

app = FastAPI(title="FirmVA", description="멀티 에이전트 펌웨어 취약점 진단")


@app.post("/scan")
async def scan(file: UploadFile = File(...)):
    # 1) 업로드된 .bin 저장
    save_path = config.INPUT_DIR / file.filename
    save_path.write_bytes(await file.read())

    # 2) 그래프(오케스트레이터) 실행
    graph = build_graph()
    final = graph.invoke({"firmware_path": str(save_path)})

    # 3) 결과 요약 반환
    findings = final.get("findings", [])
    return {
        "firmware": file.filename,
        "total_findings": len(findings),
        "report_path": final.get("report_path"),
        "findings": [f.model_dump() for f in findings],
    }


@app.get("/")
def health():
    return {"status": "ok", "service": "FirmVA"}
