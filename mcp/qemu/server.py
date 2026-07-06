# server.py:  별도 구현 QEMU MCP Server
########################################################
# QEMU는 이 프로젝트에 적절한 공개 MCP가 존재하지 않음
# 따라서, 프로젝트를 위한 QEMU MCP Server를 별도 구현해 사용
# FastMCP 를 사용하면 함수에 데코레이터만 붙여 MCP 도구를 간편하게 사용 가능함
########################################################

from fastmcp import FastMCP

mcp = FastMCP("qemu-firmva")


# 추출한 파일시스템을 사용해 QEMU versatilepb 가상 공유기를 부팅
@mcp.tool()
def boot(rootfs: str, kernel: str = "") -> dict: 
    # TODO: 실제 subprocess 실행부 구현
    return {"status": "booted", "rootfs": rootfs, "http": "127.0.0.1:8080"}


"""
부팅된 가상 공유기의 특정 진입점(URL/파라미터)에 요청을 보내 동작을 관찰합니다.
"""
@mcp.tool()
def poke(url: str, param: str = "", payload: str = "") -> dict:
    # TODO: requests 로 실제 요청 후 응답/종료코드/크래시 관찰
    return {"url": url, "param": param, "observed": "TODO"}


"""
실행 중 프로세스를 strace/ltrace 로 추적해 위험 함수 호출을 관찰합니다.
 """
@mcp.tool()
def trace(pid: int) -> dict:
    # TODO: strace 실행부 구현
    return {"pid": pid, "trace": "TODO"}


if __name__ == "__main__":
    # SSE 트랜스포트로 실행 -> .env 의 QEMU_MCP_URL과 맞춤
    mcp.run(transport="sse", host="127.0.0.1", port=8090)
