# candidates/dynamic/info.py: 사용자 데이터 노출 (단독 항목)
########################################################
# ISTG-FW[INST]-INFO-001  Disclosure of User Data

# 이 계열은 항목이 1개뿐이라 파일 하나가 곧 하위 에이전트 하나임
# 정적 info.py 와 이름은 같지만, 서로 다른 폴더(static/ vs dynamic/)라 충돌 X

# 입력 : observed (DynamicRaw.observations JSON)
# 출력 : 취약 판정 Finding 목록

from ..base import judge

PHASE = "dynamic"
LOC = "qemu-runtime"

# 동적 실행 중 응답/메모리/로그에서 사용자 데이터가 노출됐는지 확인
def check_info_001(observed: str):
    return judge("ISTG-FW[INST]-INFO-001", PHASE, observed, LOC)


def run(observed: str) -> list:
    f = check_info_001(observed)
    return [f] if f else []
