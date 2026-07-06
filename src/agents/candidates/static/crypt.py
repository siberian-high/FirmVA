# candidates/static/crypt.py: 약한 암호(Cryptography) (단독 항목)
########################################################
# ISTG-FW-CRYPT-001  Usage of Weak Cryptographic Algorithms

# 이 계열은 항목이 1개뿐이라 파일 하나가 곧 하위 에이전트 하나임

# 입력 : observed (StaticRaw JSON)
# 출력 : 취약 판정 Finding 목록
########################################################

from ..base import judge

PHASE = "static"
LOC = "filesystem/binaries"

# MD5/DES/RC4, 짧은 RSA 키 등 약한 암호 알고리즘 사용 흔적 여부
def check_crypt_001(observed: str):
    return judge("ISTG-FW-CRYPT-001", PHASE, observed, LOC)


def run(observed: str) -> list:
    f = check_crypt_001(observed)
    return [f] if f else []
