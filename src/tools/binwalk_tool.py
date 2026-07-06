# binwalk_tool.py: binwalk 을 호출해 펌웨어 .bin 을 분해
########################################################
#  binwalk 로 시그니처 스캔 -> Squashfs, 커널, 부트로더 위치 확인
########################################################

import re
import shutil
import subprocess
from pathlib import Path
from .. import config
from test import demo   # 데모 결과는 test/demo.py 로 분리됨


def run(bin_path: str) -> dict:
    """binwalk 실행 결과를 dict 로 반환.
    반환 예: {"arch","endian","signatures":[...],"rootfs","kernel","bootloader"}"""
    if config.DEMO_MODE or shutil.which("binwalk") is None:
        return demo.binwalk_result(bin_path)

    workdir = config.WORK_DIR
    # 1) 시그니처 스캔
    scan = subprocess.run(["binwalk", bin_path],
                          capture_output=True, text=True)
    signatures = [ln.strip() for ln in scan.stdout.splitlines()
                  if ln.strip() and ln[0].isdigit()]

    # 2) 추출 (-e). 결과는 _<name>.extracted 폴더에 생성
    subprocess.run(["binwalk", "-e", "--run-as=root", bin_path],
                   capture_output=True, text=True, cwd=workdir)

    extracted = _find_extracted_dir(workdir, Path(bin_path).name)
    rootfs = _find_rootfs(extracted) if extracted else None

    return {
        "arch": _guess_arch(signatures),
        "endian": "little" if "little endian" in scan.stdout else "unknown",
        "signatures": signatures,
        "rootfs": str(rootfs) if rootfs else None,
        "kernel": _find_first(extracted, ["*uImage*", "*zImage*", "*kernel*"]),
        "bootloader": _find_first(extracted, ["*u-boot*", "*uboot*", "*bootloader*"]),
    }


# 이하 보조 함수들
def _guess_arch(signatures) -> str:
    text = " ".join(signatures).lower()
    for a in ("arm", "mips", "x86", "aarch64"):
        if a in text:
            return a.upper()
    return "unknown"


def _find_extracted_dir(workdir: Path, name: str):
    cand = workdir / f"_{name}.extracted"
    return cand if cand.exists() else None


def _find_rootfs(extracted):
    if not extracted:
        return None
    for p in extracted.rglob("squashfs-root"):
        return p
    # cramfs 등 다른 파일시스템도 고려
    for p in extracted.rglob("*-root*"):
        if p.is_dir():
            return p
    return None


def _find_first(base, patterns):
    if not base:
        return None
    for pat in patterns:
        for p in base.rglob(pat):
            return str(p)
    return None
