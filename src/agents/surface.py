# agents/surface.py: Attack Surface Agent
########################################################
# 역할: 정적 로우 데이터로부터 공격 가능한 진입점 목록(공격표면)을 생성
#       각 진입점에 '인증 필요 여부'를 태깅
#       (인증 없는 진입점이 동적 분석 우선순위 최상위이므로 앞으로 정렬)

# 입력 : 공유 저장소의 static_raw (Candidate 정적과 병렬 실행)
# 출력 : state["surface"] = AttackSurface
# 전달형식: surface.json (Orchestrator 거쳐 Dynamic Analysis Agent로 전달)

# 주의: 이 에이전트는 Candidate(정적) 하위 에이전트들과 '병렬 실행1' 그룹임
#       LLM 판정이 아닌, 관찰 데이터에서 진입점을 규칙적으로 뽑아내는 역할


from ..schemas import StaticRaw, AttackSurface, EntryPoint
from .. import store

# 공유 저장소에서 static_raw 를 재사용해서 읽음
def run(state: dict) -> dict:
    raw = StaticRaw(**store.load("static_raw"))
    print("[Surface] 공격표면(진입점) 생성 중 ...")

    eps = []
    n = 0

    # 1) 웹 CGI 진입점: 위험 함수(strcpy 등)를 쓰는 CGI는 우선 후보
    for b in raw.binaries:
        if b.path.endswith(".cgi"):
            n += 1
            # netdetect처럼 인증 설정에 걸리지 않는 경로는 무인증으로 태깅
            no_auth = "ndbin" in b.path or "netdetect" in b.path
            eps.append(EntryPoint(
                ep_id=f"ep{n}",
                type="http-cgi",
                target=_to_url(b.path),
                param=_guess_param(b),
                auth_required=not no_auth,
                note="위험함수 사용: " + ", ".join(b.dangerous_calls) if b.dangerous_calls else "",
            ))

    # 2) 네트워크 서비스 진입점
    for svc in raw.services:
        n += 1
        eps.append(EntryPoint(
            ep_id=f"ep{n}", type="service", target=svc,
            param=None, auth_required=True, note="원격 서비스",
        ))

    # 3) 인증 없는 진입점을 맨 앞으로 정렬 (동적 분석 우선순위 최상위)
    eps.sort(key=lambda e: e.auth_required)
    result = AttackSurface(entrypoints=eps)
    store.save("surface", result)
    print(f"[Surface] 완료: 진입점 {len(eps)}개 (무인증 우선 정렬)")
    return {"surface": result}

# /cramfs/ndbin/netdetect.cgi -> /nd-bin/netdetect.cgi 형태로 대략 매핑
def _to_url(path: str) -> str:
    
    name = path.split("/")[-1]
    if "ndbin" in path or "netdetect" in name:
        return f"/nd-bin/{name}"
    return f"/cgi-bin/{name}"


def _guess_param(b) -> str:
    for s in b.strings:
        if s in ("commit", "flag", "cmd"):
            return s
    return "commit"
