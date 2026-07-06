# agents/static.py: Static Analysis Agent
########################################################
# 역할: Ghidra로 파일시스템 안의 바이너리를 정적 분석해 로우 데이터 추출

# 입력 : state["extract"] (특히 rootfs 경로)
# 출력 : state["static_raw"] = StaticRaw
# 저장 : Orchestrator 공유 저장소(store)에 'static_raw' 키로 저장
#        -> Candidate(정적)과 Attack Surface가 같은 데이터 재사용
# 전달형식: static_raw.json (Orchestrator 거쳐 Candidate + Attack Surface로 병렬 전달)
########################################################

from ..tools import ghidra_mcp
from ..schemas import StaticRaw
from .. import store


def run(state: dict) -> dict:
    extract = state["extract"]
    rootfs = extract.rootfs or ""
    print(f"[Static] Ghidra MCP 로 정적 분석 중: {rootfs}")

    raw = ghidra_mcp.analyze(rootfs)
    result = StaticRaw(**{k: v for k, v in raw.items() if not k.startswith("_")})

    # 핵심: 공유 저장소에 저장 -> 여러 에이전트가 재사용
    store.save("static_raw", result)
    print(f"[Static] 완료: 바이너리 {len(result.binaries)}개 관찰, store 에 저장됨")
    return {"static_raw": result}
