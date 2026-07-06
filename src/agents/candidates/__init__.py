"""
agents/candidates/__init__.py
=============================
Candidate Agent 패키지의 '입구'입니다.
오케스트레이터(orchestrator.py)는 여기의 run_static / run_dynamic 만 호출합니다.
(예전에는 candidate.py 한 파일이 하던 일을, 이제 candidates/ 아래 항목별 파일로 나눴습니다.)

  run_static  -> static/  의 파일들(info, conf, scrt, crypt) 실행 = 정적 9개 항목
  run_dynamic -> dynamic/ 의 파일들(authz, info) 실행           = 동적 3개 항목

각 파일이 '취약 판정된 Finding' 만 돌려주므로, 여기서는 결과를 합치기만 합니다.
"""

import json
from ... import store
from ...schemas import StaticRaw, DynamicRaw

# 정적 계열 파일들
from .static import info as s_info, conf as s_conf, scrt as s_scrt, crypt as s_crypt
# 동적 계열 파일들
from .dynamic import authz as d_authz, info as d_info

# 실행 순서를 담은 목록 (파일을 추가/제거하기 쉽도록 한 곳에 모음)
STATIC_AGENTS = [s_info, s_conf, s_scrt, s_crypt]     # 항목 9개
DYNAMIC_AGENTS = [d_authz, d_info]                    # 항목 3개


def run_static(state: dict) -> dict:
    """[4(1)번] 정적 후보 판정. 공유 저장소의 static_raw 를 재사용(조건 11)."""
    raw = StaticRaw(**store.load("static_raw"))
    observed = json.dumps(raw.model_dump(), ensure_ascii=False, indent=2)
    print("[Candidate:static] static/ 하위 에이전트(항목 9개) 판정 시작")

    findings = []
    for mod in STATIC_AGENTS:
        findings += mod.run(observed)
    print(f"[Candidate:static] 취약 판정 {len(findings)}건")
    return {"findings": findings}


def run_dynamic(state: dict) -> dict:
    """[6번] 동적 후보 판정. Dynamic Analysis 의 관찰 결과를 사용."""
    dyn: DynamicRaw = state["dynamic_raw"]
    observed = json.dumps([o.model_dump() for o in dyn.observations],
                          ensure_ascii=False, indent=2)
    print("[Candidate:dynamic] dynamic/ 하위 에이전트(항목 3개) 판정 시작")

    findings = []
    for mod in DYNAMIC_AGENTS:
        findings += mod.run(observed)
    print(f"[Candidate:dynamic] 취약 판정 {len(findings)}건")
    return {"findings": findings}
