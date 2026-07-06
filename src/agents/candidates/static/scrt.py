# candidates/static/scrt.py: 비밀정보(Secrets) 계열 (한 파일로 통합)
########################################################
# ISTG-FW-SCRT-001  Secrets Stored in Public Storage
# ISTG-FW-SCRT-002  Unencrypted Storage of Secrets
# ISTG-FW-SCRT-003  Usage of Hardcoded Secrets

# 통합 이유:
# 세 항목 모두 '파일/문자열 안의 비밀정보(키·비밀번호·인증서)'라는
# 같은 관찰 데이터를 근거로, 저장 위치/암호화 여부/하드코딩 여부만 달리 봄

# 입력 : observed (StaticRaw JSON)
# 출력 : 취약 판정 Finding 목록
########################################################

from ..base import judge

PHASE = "static"
LOC = "filesystem/binaries"

# 공개 위치(웹 루트 등)에 비밀정보가 저장돼 있는지
def check_scrt_001(observed: str):    
    return judge("ISTG-FW-SCRT-001", PHASE, observed, LOC)

# 비밀정보가 평문/약한 해시로 저장돼 있는지
def check_scrt_002(observed: str):    
    return judge("ISTG-FW-SCRT-002", PHASE, observed, LOC)

# 바이너리/스크립트에 하드코딩된 키·비밀번호·백도어 문자열이 있는지
def check_scrt_003(observed: str):    
    return judge("ISTG-FW-SCRT-003", PHASE, observed, LOC)


def run(observed: str) -> list:
    results = [
        check_scrt_001(observed),
        check_scrt_002(observed),
        check_scrt_003(observed),
    ]
    return [f for f in results if f]
