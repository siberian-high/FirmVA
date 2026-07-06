# llm.py: OpenAI API 호출
########################################################
# API 키는 config 를 통해 .env 에서만 읽어옴
# Candidate 하위 에이전트가 "이 관찰 데이터가 취약한가?" 를 판정할 때 이 함수를 사용함
# 판정은 항상 JSON 으로만 답하도록 프롬프트를 강제, 코드 파싱이 쉽도록 함
########################################################

import json
from typing import Optional
from . import config
from test import demo   # 데모 판정은 test/demo.py 로 분리됨
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# LLM 에게 물어보고, JSON 형태의 dict 로 결과를 받음
# DEMO_MODE 이거나 API 키가 없으면, 실제 호출 대신 데모 판정을 돌려줌
# 도구 및 API 키가 준비되지 않아도 파이프라인 전체를 돌려볼 수 있게 하기 위함
def ask_json(system: str, user: str) -> dict:

    if config.DEMO_MODE or not config.OPENAI_API_KEY:
        return demo.llm_verdict(user)

    # langchain-openai 사용
    llm = ChatOpenAI(model=config.OPENAI_MODEL,
                     api_key=config.OPENAI_API_KEY,
                     temperature=0)
    guard = ("\n\n반드시 아래 JSON 형식으로만, 다른 말 없이 답하세요:\n"
             '{"verdict":"vulnerable|not_vulnerable","severity":"low|medium|high",'
             '"confidence":0.0~1.0,"evidence":"근거 한두 문장"}')
    resp = llm.invoke([SystemMessage(content=system),
                       HumanMessage(content=user + guard)])
    text = resp.content.strip()

    # 코드블록(```)으로 감싸져 오면 벗겨냄
    text = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"verdict": "not_vulnerable", "severity": "low",
                "confidence": 0.0, "evidence": f"(파싱 실패: {text[:120]})"}
