# agents/dynamic.py: Dynamic Analysis Agent
########################################################
# 역할: 공격표면을 받아 QEMU에서 실제로 찔러보고 관찰 결과를 생성
#       또한 전달받은 것 외의 새 진입점이 있는지 찾아 별도로 기록

# 입력 : state["surface"] (AttackSurface)
# 출력 : state["dynamic_raw"] = DynamicRaw
# 전달형식: dynamic_raw.json
#          observations만 Candidate(동적)로 전달
#          new_entrypoints는 Candidate로 넘기지 않고 store에만 기록

from ..tools import qemu_mcp
from ..schemas import AttackSurface, DynamicRaw
from .. import store


def run(state: dict) -> dict:
    surface: AttackSurface = state["surface"]
    print("[Dynamic] QEMU MCP 로 동적 분석 중 ...")

    raw = qemu_mcp.run(surface.model_dump())
    result = DynamicRaw(**{k: v for k, v in raw.items() if not k.startswith("_")})

    # 새로 발견한 진입점은 별도 저장(향후 Attack Surface에 되먹임)
    if result.new_entrypoints:
        store.save("new_entrypoints", [e.model_dump() for e in result.new_entrypoints])
        print(f"[Dynamic] 새 진입점 {len(result.new_entrypoints)}개 별도 기록됨")

    store.save("dynamic_raw", result)
    print(f"[Dynamic] 완료: 관찰 {len(result.observations)}건")
    return {"dynamic_raw": result}
