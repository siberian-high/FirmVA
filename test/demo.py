# demo.py: 데모 테스트용 코드 모음
########################################################
# DEMO_MODE=true 이거나 도구/API 키가 없을 때 사용하는 테스트용 데이터

# 목적: 실제 도구(binwalk/Ghidra/QEMU)나 ChatGPT 키가 없어도
#       파이프라인 전체 동작을 끝까지 테스트하기 위함.

# 주의: 실제 진단 로직과는 분리돼 있으며, .env에서 DEMO_MODE=false일 경우
#       이 파일의 함수들은 호출되지 않음
########################################################

from src import config


# 1) LLM 판정 데모
# 데모 모드에서 '취약'으로 보여줄 항목
_DEMO_HITS = {
    "ISTG-FW-SCRT-003": ("high", 0.9,
        "timepro.cgi 내 하드코딩된 원격관리 백도어 Key 문자열 발견"),
    "ISTG-FW-CONF-001": ("medium", 0.7,
        "구버전 툴체인/구성요소 문자열 관찰(Sourcery 2009q3) — 알려진 취약점 가능성"),
    "ISTG-FW-CONF-002": ("medium", 0.6,
        "운영에 불필요한 원격관리 백도어(remote_support) 기능 존재"),
    "ISTG-FW[INST]-AUTHZ-001": ("high", 0.9,
        "netdetect.cgi 가 인증 없이 접근 가능하며 실제 동작 재현됨"),
    "ISTG-FW[INST]-AUTHZ-002": ("high", 0.85,
        "무인증 진입점에서 strcpy 버퍼오버플로우로 PC 덮어쓰기(SIGSEGV) 관찰"),
}


def llm_verdict(user: str) -> dict:
    # 프롬프트(user)에 특정 ISTG 항목 ID 가 들어있으면 취약으로 판정
    for istg_id, (sev, conf, ev) in _DEMO_HITS.items():
        # 프롬프트에 해당 항목 ID가 들어있으면 취약으로 판정
        if istg_id in user:      
            return {"verdict": "vulnerable", "severity": sev,
                    "confidence": conf, "evidence": f"(demo) {ev}"}
    return {"verdict": "not_vulnerable", "severity": "low",
            "confidence": 0.0, "evidence": "(demo mode: 해당 없음)"}


# 2) binwalk 분해 데모
def binwalk_result(bin_path: str) -> dict:
    # binwalk 미설치/데모 모드일 때의 모의 분해 결과
    return {
        "arch": "ARM",
        "endian": "little",
        "signatures": [
            "0             0x0             uImage header, OS: Linux, CPU: ARM",
            "720896        0xB0000         Squashfs filesystem, little endian, version 3.0",
        ],
        "rootfs": str(config.WORK_DIR / "demo_squashfs-root"),
        "kernel": str(config.WORK_DIR / "demo_zImage"),
        "bootloader": None,
    }


# 3) 정적 분석 데모
def static_raw(rootfs: str, note: str = "") -> dict:
    # Ghidra 미연결/데모 모드일 때의 모의 정적 로우 데이터
    return {
        "binaries": [
            {
                "path": "/cramfs/bin/timepro.cgi",
                "stripped": True,
                "imports": ["strcpy", "sprintf", "system", "getenv"],
                "strings": [
                    "aaksjdkfj=#notenoughmineral^",     # 하드코딩 백도어 Key (SCRT-003)
                    "remote_support=1",
                    "GCC: (Sourcery G++ Lite 2009q3-67)",  # 구버전 툴체인 (CONF-001)
                ],
                "dangerous_calls": ["strcpy(buf, getenv(\"commit\"))"],  # CRYPT/overflow 단서
            },
            {
                "path": "/cramfs/ndbin/netdetect.cgi",   # timepro.cgi 로의 심볼릭 링크
                "stripped": True,
                "imports": ["strcpy", "getenv"],
                "strings": ["commit", "flag", "Content-Type"],
                "dangerous_calls": ["strcpy(buf, param)"],
            },
        ],
        "files": [
            "/etc/passwd", "/etc/httpd.passwd", "/etc/iconfig.cfg",
            "/home/httpd/index.html", "/var/boa_vh.conf", "/bin/busybox",
        ],
        "configs": [
            "boa_vh.conf: ScriptAlias /nd-bin/ /ndbin/ ; Auth /cgi-bin /etc/httpd.passwd",
            "iconfig.cfg: remote_support 관련 항목 존재",
        ],
        "services": ["httpd(boa)", "dhcpd", "pptpd", "upnpd"],
        "_note": note,
    }


# 4) 동적 분석 데모
def dynamic_raw(surface: dict, note: str = "") -> dict:
    # QEMU 미연결/데모 모드일 때의 모의 동적 로우 데이터
    # netdetect.cgi 에 긴 문자열 전달 -> strcpy -> SIGSEGV(0x42424242) 재현
    eps = surface.get("entrypoints", [])
    observations = []
    for ep in eps:
        if "netdetect" in ep.get("target", ""):
            observations.append({
                "ep_id": ep["ep_id"], "target": ep["target"],
                "reproduced": True,
                "result": "SIGSEGV, si_addr=0x42424242 (PC 덮어쓰기 관찰)",
                "trace": "[..] strcpy(...) 이후 크래시; ASLR/DEP 미적용",
            })
        else:
            observations.append({
                "ep_id": ep["ep_id"], "target": ep["target"],
                "reproduced": False, "result": "특이사항 없음", "trace": "",
            })
    return {
        "observations": observations,
        # 새로 발견한 진입점은 Candidate로 넘기지 않고 여기에만 기록
        "new_entrypoints": [{
            "ep_id": "new1", "type": "service", "target": "/sbin/pptpd",
            "param": None, "auth_required": True,
            "note": "동적 관찰 중 발견. 향후 Attack Surface 에 되먹임 예정.",
        }],
        "_note": note,
    }
