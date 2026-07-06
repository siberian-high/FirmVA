# state.py: LangGraph 그래프 노드(=에이전트) 사이의 '공유 상태' 정의
########################################################
# LangGraph는 각 노드가 이 딕셔너리를 조금씩 채워 나가는 방식으로 동작
# Analysis 노드가 extract 를 채우고, Static 노드가 static_raw 를 채우는 방식

# 주의사항: 정적 후보(9개)와 공격표면 -> 동적 -> 동적 후보(3개) 는 병렬로 갈라졌다가 합쳐짐
# 여러 노드가 동시에 findings 를 추가할 수 있으므로,
# findings 필드는 누적(add) 되도록 reducer를 붙입니다.
########################################################

import operator
from typing import Annotated, List, Optional
from typing_extensions import TypedDict

from .schemas import ExtractResult, StaticRaw, AttackSurface, DynamicRaw, Finding


class FirmState(TypedDict, total=False):
    # 입력
    firmware_path: str                 # 진단할 .bin 파일 경로

    # 각 단계 산출물
    extract: ExtractResult             # 2번 Analysis 결과
    static_raw: StaticRaw              # 3번 Static 결과(공유 저장소에도 저장)
    surface: AttackSurface             # 4(2)번 Attack Surface 결과
    dynamic_raw: DynamicRaw            # 5번 Dynamic 결과

    # 취약점 판정 결과 (정적 9 + 동적 3 하위 에이전트가 누적으로 추가)
    findings: Annotated[List[Finding], operator.add]

    # 최종 보고서 경로
    report_path: Optional[str]
