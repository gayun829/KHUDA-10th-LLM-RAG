"""Step 4. Generate — 검색한 청크를 프롬프트에 넣어 답하게 한다.   TODO 4 : rag/prompt.py 의 build_messages
실행 : python step4_generate.py                           (예시 질문)
       python step4_generate.py "OT도 꼭 가야 해?"          (내 질문)"""
import sys

import config
from rag import llm
from rag.pipeline import sources
from rag.prompt import build_messages
from rag.store import VectorStore
from rag.util import mark

# ---------------- Check ----------------
m = build_messages("질문?", [(0.9, {"text": "[문서 > 소제목]\n내용"})])
ok = "[1] [문서 > 소제목]" in m[1]["content"] and m[1]["content"].endswith("[질문]\n질문?")
print("Check : build_messages가 청크에 [1] 번호를 붙여 질문 앞에 넣었나  %s\n" % mark(ok))

question = " ".join(sys.argv[1:]) or "KHUDA 임원진의 임기는 얼마나 돼?"
store = VectorStore.load()
print("질문 :", question)

print("\n[1] LLM만 (검색 없이 그냥 물어보기)")
print("    " + llm.chat([{"role": "user", "content": question}]).replace("\n", "\n    "))

hits = store.search(llm.embed([question])[0], k=config.TOP_K)
messages = build_messages(question, hits)
user = messages[1]["content"]
print("\n[2] 실제로 보낸 프롬프트 (system은 rag/prompt.py 의 SYSTEM, 아래는 user 부분)")
print("    " + (user if len(user) < 1500 else user[:1500] + "\n... (생략)").replace("\n", "\n    "))

print("\n[3] RAG (검색 → 프롬프트 → 답)")
print("    " + llm.chat(messages).replace("\n", "\n    "))
print("    출처 : " + sources(hits))

print("\n" + llm.cost_report())
print("다음 : python step5_evaluate.py")
