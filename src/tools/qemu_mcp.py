# qemu_mcp.py: QEMU 에뮬레이션 기반 동적 분석을 수행
########################################################
# 블랙박스 원칙에 따라 소스 없이 실제 실행 동작만 관찰

# 이 서버가 제공하는 도구(예정):
#    - boot(rootfs, kernel)      : QEMU versatilepb 로 부팅
#    - poke(entrypoint)          : 특정 진입점(URL/파라미터)을 실제로 요청/실행
#    - trace(pid)                : strace/ltrace로 위험 함수 호출 관찰
########################################################

from typing import List
from .. import config
from test import demo   # 데모 동적 데이터는 test/demo.py 로 분리됨

# 공격표면(entrypoints)을 받아 QEMU 에서 하나씩 동적 검증
# 반환은 schemas.DynamicRaw로 변환 가능한 dict
def run(surface: dict) -> dict:
    if config.DEMO_MODE:
        return demo.dynamic_raw(surface)

    try:
        return _call_qemu_mcp(surface)
    except Exception as e:                      # noqa
        return demo.dynamic_raw(surface, note=f"(MCP 연결 실패, 데모로 대체: {e})")


def _call_qemu_mcp(surface: dict) -> dict:
    # from langchain_mcp_adapters.client import MultiServerMCPClient
    # client = MultiServerMCPClient({"qemu": {"url": config.QEMU_MCP_URL,
    #                                         "transport": "sse"}})
    # tools = await client.get_tools()  # boot / poke / trace 호출
    raise NotImplementedError("mcp/qemu 서버를 띄운 뒤 호출부를 구현하세요.")
