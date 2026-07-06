# agents/report.py: Report Agent
########################################################
# 정적(4-1)과 동적(6)에서 올라온 취약 판정 결과를 모아 보고서 생성

# 입력 : state["findings"] (정적/동적 Finding 누적)
# 출력 : CLI 출력 + out/report.txt
########################################################

from datetime import datetime
from .. import config
from ..schemas import Finding


def run(state: dict) -> dict:
    findings = state.get("findings", [])
    extract = state.get("extract")
    fw_name = extract.firmware if extract else config.TARGET_NAME

    lines = []
    lines.append("=" * 64)
    lines.append("  FirmVA - 펌웨어 취약점 진단 보고서")
    lines.append("=" * 64)
    lines.append(f"  대상 펌웨어 : {fw_name}")
    lines.append(f"  생성 시각   : {datetime.now():%Y-%m-%d %H:%M:%S}")
    if extract:
        lines.append(f"  아키텍처    : {extract.arch} ({extract.endian})")
    lines.append(f"  취약점 판정  : 총 {len(findings)}건")
    lines.append("")

    static_f = [f for f in findings if f.phase == "static"]
    dynamic_f = [f for f in findings if f.phase == "dynamic"]

    lines.append("-" * 64)
    lines.append(f"[정적 분석 결과] {len(static_f)}건")
    lines.append("-" * 64)
    _dump(lines, static_f)

    lines.append("")
    lines.append("-" * 64)
    lines.append(f"[동적 분석 결과] {len(dynamic_f)}건")
    lines.append("-" * 64)
    _dump(lines, dynamic_f)

    lines.append("")
    lines.append("=" * 64)
    lines.append("  보고서 끝")
    lines.append("=" * 64)

    text = "\n".join(lines)

    # 1) CLI 출력
    print("\n" + text + "\n")

    # 2) .txt 파일 저장
    out_path = config.OUT_DIR / f"report_{datetime.now():%Y%m%d_%H%M%S}.txt"
    out_path.write_text(text, encoding="utf-8")
    print(f"[Report] 보고서 저장: {out_path}")

    return {"report_path": str(out_path)}


def _dump(lines: list, findings: list):
    if not findings:
        lines.append("  (해당 없음)")
        return
    # 심각도 높은 순으로 정렬
    order = {"high": 0, "medium": 1, "low": 2}
    for f in sorted(findings, key=lambda x: order.get(x.severity, 3)):
        lines.append(f"  ● {f.istg_id}  {f.name}")
        lines.append(f"     - 심각도   : {f.severity}  (확신도 {f.confidence:.2f})")
        lines.append(f"     - 위치     : {f.location}")
        lines.append(f"     - 근거     : {f.evidence}")
        lines.append("")
