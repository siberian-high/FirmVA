# ghidra_mcp.py: Ghidra를 사용해 정적 분석을 수행
########################################################
# Ghidra는 공개된 MCP 서버 존재
# LaurieWired/GhidraMCP  (https://github.com/LaurieWired/GhidraMCP)
# 따라서  공개 MCP 를 그대로 사용

#  이 모듈은 위 MCP 서버에 붙어서 decompile / list_imports / list_strings 같은
#  도구를 호출하고, 그 결과를 우리 형식(StaticRaw)에 맞게 정리해 돌려줍니다.

#  블랙박스 원칙에 따라 원본 소스코드 없이, Ghidra 가 디컴파일한 결과와
#  문자열/임포트만으로 관찰 데이터(로우 데이터)를 생성

# 사용 방법(요약):
#    1) Ghidra 실행 -> 대상 바이너리 import 후 GhidraMCP 플러그인 활성화
#    2) 별도 터미널에서:
#       python bridge_mcp_ghidra.py --transport sse --mcp-host 127.0.0.1 --mcp-port 8081
#    3) .env 의 GHIDRA_MCP_URL 을 위 주소로 맞춤
########################################################

from typing import List
from .. import config
from test import demo   # 데모 정적 데이터는 test/demo.py 로 분리됨

# rootfs 안의 실행 바이너리(CGI 등)를 Ghidra MCP 로 정적 분석.
# 반환은 schemas.StaticRaw 로 변환 가능한 dict."""
def analyze(rootfs: str) -> dict:
    
    if config.DEMO_MODE:
        return demo.static_raw(rootfs)

    # 실제 MCP 연결부
    # langchain-mcp-adapters 를 쓰면 MCP 도구를 LangGraph 툴처럼 바로 호출
    #   from langchain_mcp_adapters.client import MultiServerMCPClient
    #   client = MultiServerMCPClient({"ghidra": {"url": config.GHIDRA_MCP_URL,
    #                                             "transport": "sse"}})
    #   tools = await client.get_tools()
    #   # tools 중 decompile_function / list_imports / list_strings 등을 호출
    #
    # 실제 구현은 팀에서 Ghidra를 띄운 뒤 추가
    # 여기서는 연결 실패 시 데모 데이터로 폴백
    try:
        return _call_ghidra_mcp(rootfs)
    except Exception as e:                      # noqa
        return demo.static_raw(rootfs, note=f"(MCP 연결 실패, 데모로 대체: {e})")


def _call_ghidra_mcp(rootfs: str) -> dict:
    raise NotImplementedError("Ghidra 를 띄운 뒤 MCP 호출부를 구현하세요.")
