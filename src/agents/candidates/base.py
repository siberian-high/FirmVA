# agents/candidates/base.py:
# candidates/ 아래 모든 하위 에이전트 파일이 공통으로 쓰는 판정 엔진
########################################################
# 각 항목 파일(static/info.py, static/scrt.py, dynamic/authz.py ...)은
# '자기 항목을 어떤 관찰 데이터로 판정할지'만 담고, 
# 실제로 LLM 에게 물어보고 Finding 을 만드는 반복 작업은 여기 judge() 에 모아둠
# '판정이 어떻게 이뤄지는가'는 이 파일 하나만 보면 됨

# 항목의 이름/힌트(카탈로그)는 여전히 src/istgfw.py 가 유일한 출처(single source)
# 여기서는 항목 ID 로 그 카탈로그를 찾아 사용
########################################################

from ... import llm, istgfw
from ...schemas import Finding

# istgfw.py의 12개 카탈로그에서 해당 ID 항목(id/name/hint)을 찾아 반환
def spec(istg_id: str) -> dict:    
    for cat in istgfw.ALL:
        if cat["id"] == istg_id:
            return cat
    raise KeyError(f"알 수 없는 ISTG 항목: {istg_id}")

# 관찰 데이터를 근거로 해당 ISTG 항목의 취약 여부를 판
# 취약하면 Finding을, 아니면 None을 반환한다 (취약 판정만 다음 단계로 전달)
def judge(istg_id: str, phase: str, observed_text: str, location: str) -> Finding | None:    
    cat = spec(istg_id)
    system = (
        "너는 임베디드 펌웨어 취약점 진단 하위 에이전트다. "
        "블랙박스로 관찰된 데이터만 근거로, 아래 OWASP ISTG 항목에 해당하는 "
        "취약점이 실제로 존재하는지 보수적으로 판정하라."
    )
    user = (
        f"[판정 대상 항목]\n{cat['id']} - {cat['name']}\n"
        f"[판정 힌트]\n{cat['hint']}\n\n"
        f"[관찰된 데이터]\n{observed_text}"
    )
    verdict = llm.ask_json(system, user)

    if verdict.get("verdict") != "vulnerable":
        return None

    return Finding(
        istg_id=cat["id"],
        name=cat["name"],
        phase=phase,
        severity=verdict.get("severity", "medium"),
        confidence=float(verdict.get("confidence", 0.5)),
        evidence=verdict.get("evidence", ""),
        location=location,
    )
