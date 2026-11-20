"""Step 3. Search — 질문과 가장 가까운 청크를 찾는다.   TODO 3 : rag/store.py 의 search
실행 : python step3_search.py                       (예시 질문 3개)
       python step3_search.py "기초 세션은 무슨 요일에 해?"   (내 질문)"""
import sys

import numpy as np

import config
from rag import llm
from rag.store import VectorStore
from rag.util import mark, short

# ---------------- Check : 2차원 장난감 벡터 ----------------
toy = VectorStore([{"text": "A"}, {"text": "B"}, {"text": "C"}],
                  np.array([[1.0, 0.0], [0.6, 0.8], [0.0, 1.0]]))
got = [c["text"] for _, c in toy.search(np.array([0.8, 0.6]), k=2)]
print("Check : 질문 (0.8, 0.6)과 가까운 2개 — A (1, 0) · B (0.6, 0.8) · C (0, 1) 중")
print("        → %s   ['B', 'A'] 이어야 함  %s\n" % (got, mark(got == ["B", "A"])))

# ---------------- 진짜 검색 ----------------
store = VectorStore.load()
questions = [" ".join(sys.argv[1:])] if len(sys.argv) > 1 else [
    "러닝메이트 제도가 뭐야?",
    "학교를 마친 사람도 신청할 수 있나요?",
    "경고를 몇 번 받으면 제명돼?",
]
Q = llm.embed(questions)
for q, v in zip(questions, Q):
    print("질문 : %s" % q)
    for rank, (score, c) in enumerate(store.search(v, k=config.TOP_K), start=1):
        body = c["text"].split("\n", 1)[1]
        print("  %d. %.3f  %s > %s" % (rank, score, c["doc_id"], c["section"]))
        print("            %s" % short(body, 72))
    print()

print(llm.cost_report())
print("다음 : python step4_generate.py")
