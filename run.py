# run.py: FirmVA CLI 진입점
########################################################
# 사용 방법: python run.py <펌웨어.bin 경로>
# 예시: python run.py data/input/g104_kr_7_60.bin
# 동작:
#    1) 입력 .bin 경로로 상태를 생성
#    2) Orchestrator를 실행
#    3) 최종 보고서를 CLI와 out/report_*.txt 형식으로 출력
########################################################

import sys
from pathlib import Path
from src.orchestrator import build_graph
from src import config


def main():
    if len(sys.argv) < 2:
        print("[사용 방법] python run.py <펌웨어.bin 경로>")
        print("예시:    python run.py data/input/g104_kr_7_60.bin")
        if config.DEMO_MODE:
            print("[안내] 현재 DEMO_MODE=true 입니다.")
            print("실제 .bin 파일이 없어도 데모 모드로 동작합니다.")
            print("아래와 같이 아무 경로를 입력해 데모 테스트를 진행할 수 있습니다.")
            print("예시:    python run.py demo.bin")
        return

    bin_path = sys.argv[1]
    if not Path(bin_path).exists() and not config.DEMO_MODE:
        print(f"[오류] 파일을 찾을 수 없습니다: {bin_path}")
        return

    print(f"======= FirmVA 시작: {bin_path} =======")
    graph = build_graph()
    graph.invoke({"firmware_path": bin_path})
    print("======= FirmVA 종료 =======")


if __name__ == "__main__":
    main()
