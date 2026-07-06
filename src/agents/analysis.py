# agents/analysis.py: Analysis Agent
########################################################
# 역할: binwalk으로 펌웨어 .bin 을 분해해 부트로더/커널/파일시스템을 분리

# 입력 : state["firmware_path"]  (.bin 경로)
# 출력 : state["extract"] = ExtractResult
# 전달형식: extract.json (Orchestrator를 거쳐 Static Analysis Agent로 전달)
########################################################

from ..tools import binwalk_tool
from ..schemas import ExtractResult
from .. import store
from pathlib import Path


def run(state: dict) -> dict:
    bin_path = state["firmware_path"]
    print(f"[Analysis] binwalk 로 분해 중: {bin_path}")

    raw = binwalk_tool.run(bin_path)
    result = ExtractResult(
        firmware=Path(bin_path).name,
        arch=raw.get("arch", "unknown"),
        endian=raw.get("endian", "unknown"),
        bootloader=raw.get("bootloader"),
        kernel=raw.get("kernel"),
        rootfs=raw.get("rootfs"),
        signatures=raw.get("signatures", []),
    )

    # 공유 저장소에도 남겨 재현/디버깅에 활용
    store.save("extract", result)
    print(f"[Analysis] 완료: arch={result.arch}, rootfs={result.rootfs}")
    return {"extract": result}
