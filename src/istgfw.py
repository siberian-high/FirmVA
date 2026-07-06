# istgfw.py: 취약점 후보 생성 및 판정 기준 (OWASP ISTG-FW)
########################################################
# OWASP ISTG-FW 의 항목 중, 조건에 따라 아래 항목은 제외함
#   ISTG-FW[UPDT] (펌웨어 업데이트 메커니즘) 6개 모두 제외
#   ISTG-FW[INST]-CRYPT-001 (부트로더 서명 검증) 1개 제외
#   최종적으로 총 12개(정적 9 + 동적 3) 항목만 사용

# 각 항목은 "하나의 Candidate 하위 에이전트"에 매핑됨
#   STATIC 카테고리 9개 -> 정적 하위 에이전트 4개 (병렬 실행)
#   DYNAMIC 카테고리 3개 -> 동적 하위 에이전트 2개 (병렬 실행)

# 각 항목 필드 설명:
#  id     : OWASP ISTG 테스트 ID (보고서에 그대로 표기)
#  name   : 테스트 이름
#  hint   : LLM 하위 에이전트에게 "무엇을 근거로 판정할지" 알려주는 힌트.
#           블랙박스 분석이므로, 소스코드가 아니라 '관찰된 데이터(로우 데이터)'에서
#           찾을 수 있는 단서를 적어둡니다.
########################################################

# 정적(Static) 카테고리 9개: Static Analysis Agent 의 로우 데이터로 판정
STATIC = [
    {
        "id": "ISTG-FW-INFO-001",
        "name": "Disclosure of Source Code and Binaries",
        "hint": "추출된 파일시스템 안에 소스코드(.c/.lua/.php), 심볼이 남은(not stripped) "
                "바이너리, .git/.svn 흔적이 노출되어 있는지 확인.",
    },
    {
        "id": "ISTG-FW-INFO-002",
        "name": "Disclosure of Implementation Details",
        "hint": "빌드 경로, 개발자 주석, 디버그 문자열, 내부 함수명 등 구현 세부정보가 "
                "문자열/바이너리에 노출되는지 확인.",
    },
    {
        "id": "ISTG-FW-INFO-003",
        "name": "Disclosure of Ecosystem Details",
        "hint": "내부 서버 주소, 업데이트 URL, 클라우드 엔드포인트, 이메일 등 "
                "생태계(백엔드) 정보가 노출되는지 확인.",
    },
    {
        "id": "ISTG-FW-CONF-001",
        "name": "Usage of Outdated Software",
        "hint": "busybox, openssl, dropbear, boa/httpd, 커널 버전 문자열을 근거로 "
                "오래되고 알려진 CVE가 있는 구버전 소프트웨어 사용 여부 확인.",
    },
    {
        "id": "ISTG-FW-CONF-002",
        "name": "Presence of Unnecessary Software and Functionalities",
        "hint": "telnetd, ftpd, 디버그 콘솔, 테스트 CGI(/testbin), 백도어 페이지 등 "
                "운영에 불필요하거나 위험한 기능이 포함되어 있는지 확인.",
    },
    {
        "id": "ISTG-FW-SCRT-001",
        "name": "Secrets Stored in Public Storage",
        "hint": "웹 루트(/home/httpd 등) 공개 위치에 개인키, 인증서, 설정 백업 같은 "
                "비밀 정보가 저장되어 있는지 확인.",
    },
    {
        "id": "ISTG-FW-SCRT-002",
        "name": "Unencrypted Storage of Secrets",
        "hint": "/etc/passwd, /etc/shadow, httpd.passwd, iconfig.cfg 등에 "
                "비밀번호/키가 평문 또는 약한 해시로 저장되어 있는지 확인.",
    },
    {
        "id": "ISTG-FW-SCRT-003",
        "name": "Usage of Hardcoded Secrets",
        "hint": "바이너리/스크립트 안에 하드코딩된 키·비밀번호·백도어 문자열이 있는지 확인. "
                "(예: timepro.cgi 내 원격관리 백도어 Key 문자열)",
    },
    {
        "id": "ISTG-FW-CRYPT-001",
        "name": "Usage of Weak Cryptographic Algorithms",
        "hint": "MD5, DES, RC4, 짧은 RSA 키 등 약한 암호 알고리즘 사용 흔적이 "
                "문자열/임포트 심볼에 나타나는지 확인.",
    },
]

# 동적(Dynamic) 카테고리 3개: Dynamic Analysis Agent의 관찰 결과로 판정
DYNAMIC = [
    {
        "id": "ISTG-FW[INST]-AUTHZ-001",
        "name": "Unauthorized Access to the Firmware",
        "hint": "인증 없이 접근 가능한 진입점(CGI/서비스)에서 실제로 동작이 수행됐는지, "
                "인증 우회가 관찰됐는지 확인. (예: netdetect.cgi 무인증 접근)",
    },
    {
        "id": "ISTG-FW[INST]-AUTHZ-002",
        "name": "Privilege Escalation",
        "hint": "낮은 권한 입력으로 root 권한 명령 실행/쉘 획득이 관찰됐는지 확인. "
                "(예: command injection, 버퍼오버플로우로 쉘 실행)",
    },
    {
        "id": "ISTG-FW[INST]-INFO-001",
        "name": "Disclosure of User Data",
        "hint": "동적 실행 중 응답/메모리/로그에서 사용자 데이터(계정, 설정, 세션 등)가 "
                "노출되는지 확인.",
    },
]

# 전체 12개를 한 번에 참조
ALL = STATIC + DYNAMIC

# phase='static'이면 9개, phase='dynamic'이면 3개 카테고리를 반환
def phase_categories(phase: str):
    
    return STATIC if phase == "static" else DYNAMIC
