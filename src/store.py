# store.py: Orchestrator가 관리하는 공유 저장소 처리 과정
########################################################
# Static Analysis Agent의 로우 데이터처럼, 여러 에이전트가 재사용하는
# 결과물을 data/storage/*.json에 저장
# Candidate Agent, Attack Surface Agent 등이 같은 데이터를 재사용

# 키 이름으로 json 파일을 저장/조회하는 형태
########################################################

import json
from pathlib import Path
from typing import Any
from . import config

# data(dict 또는 Pydantic 모델)를 storage/<key>.json 으로 저장
def save(key: str, data: Any) -> Path:
    if hasattr(data, "model_dump"):        # Pydantic 모델이면 dict 로 변환
        data = data.model_dump()
    path = config.STORAGE_DIR / f"{key}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path

# storage/<key>.json 을 읽어 dict로 반환. 없으면 None
def load(key: str) -> Any:
    path = config.STORAGE_DIR / f"{key}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def exists(key: str) -> bool:
    return (config.STORAGE_DIR / f"{key}.json").exists()
