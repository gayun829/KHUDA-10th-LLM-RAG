"""Step 0. 환경 확인 — 파이썬 · 패키지 · API 키를 확인하고, OpenAI 모델 두 개를 한 번씩 불러 본다.
실행 : python step0_check.py"""
import os
import sys

import openai

import config
from rag import llm

print("Python", sys.version.split()[0], "/ openai", openai.__version__)
key = os.getenv("OPENAI_API_KEY", "")
if not key or "여기에" in key:
    sys.exit("OPENAI_API_KEY가 없습니다 → .env 파일에 OPENAI_API_KEY=sk-... 를 적었는지 확인하세요")
if not key.isascii() or any(c.isspace() for c in key):
    sys.exit("키에 한글 · 특수 따옴표 · 띄어쓰기가 섞여 있습니다 → nano .env 에서 OPENAI_API_KEY=sk-... 한 줄만 남기세요")
print("API 키 :", key[:8] + "..." + key[-4:])

try:
    resp = llm.get_client().embeddings.create(model=config.EMBED_MODEL, input=["안녕하세요"])
    llm.USAGE["embed"] += resp.usage.total_tokens
    print("embedding OK : %s → %d차원 벡터" % (config.EMBED_MODEL, len(resp.data[0].embedding)))
    reply = llm.chat([{"role": "user", "content": "RAG를 한 문장으로 설명해 줘."}])
    print("chat OK      : %s → %s" % (config.CHAT_MODEL, reply))
except openai.AuthenticationError:
    sys.exit("\nAPI 키가 틀렸습니다 (401) → .env 의 키를 다시 확인하세요")
except openai.NotFoundError as e:
    sys.exit("\n모델을 찾을 수 없습니다 (404) → config.py 의 모델 이름을 확인하세요\n%s" % e)
except openai.RateLimitError as e:
    sys.exit("\n요청이 너무 많거나 크레딧이 부족합니다 (429) → 잠시 뒤 다시 실행, 계속되면 강사에게\n%s" % e)
except openai.BadRequestError as e:
    sys.exit("\n요청 형식 오류 (400) → 추론 설정이 없는 모델이라면 config.py 의 REASONING_EFFORT를 \"\"로\n%s" % e)
except openai.APIConnectionError:
    sys.exit("\nOpenAI 서버에 연결할 수 없습니다 → 인터넷 연결을 확인하세요")

print(llm.cost_report())
print("\n준비 완료! 다음 : python step1_chunk.py")
