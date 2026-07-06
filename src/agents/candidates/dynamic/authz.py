# candidates/dynamic/authz.py: 인가(Authorization) 계열 한 파일로 통합
########################################################
# ISTG-FW[INST]-AUTHZ-001  Unauthorized Access to the Firmware
# ISTG-FW[INST]-AUTHZ-002  Privilege Escalation

# 통합 이유:
# 두 항목 모두 'QEMU 동적 실행 관찰 결과'라는 같은 데이터를 근거로,
#  무인증 접근이 성립했는지 / 그로 인해 권한 상승까지 갔는지만 달리 봄

# 입력 : observed (DynamicRaw.observations 를 JSON 문자열로 만든 관찰 데이터)
# 출력 : 취약 판정 Finding 목록
########################################################

from ..base import judge

PHASE = "dynamic"
LOC = "qemu-runtime"

# 인증 없이 접근 가능한 진입점에서 실제 동작/인증 우회가 관찰됐는지 확인
def check_authz_001(observed: str):
    
    return judge("ISTG-FW[INST]-AUTHZ-001", PHASE, observed, LOC)

# 낮은 권한 입력으로 root 명령 실행/쉘 획득(권한 상승)이 관찰됐는지 확인
def check_authz_002(observed: str):
    return judge("ISTG-FW[INST]-AUTHZ-002", PHASE, observed, LOC)


def run(observed: str) -> list:
    results = [check_authz_001(observed), check_authz_002(observed)]
    return [f for f in results if f]
