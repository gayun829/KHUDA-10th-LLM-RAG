"""Step 6. 지식 업데이트 — 모델은 그대로 두고 문서(인덱스)만 바꾼다.   TODO 없음, 실행하고 읽어 보기
논문의 index hot-swapping을 작게 : 바뀐 문서의 청크만 지우고 새로 임베딩해서 끼워 넣는다.
실행 : python step6_update.py          (원래 index/는 그대로 둔다)
       python step6_update.py --save   (바뀐 인덱스를 index/에 저장 → chat.py도 새 문서를 본다)"""
import sys

import numpy as np

import config
from rag import llm
from rag.chunking import load_docs, make_chunks
from rag.pipeline import answer, sources
from rag.store import VectorStore
from rag.util import pad

questions = ["활동비는 얼마야?",
             "YB가 수료하려면 뭘 해야 해?",
             "OB 혜택은 뭐가 있어?"]

store = VectorStore.load()
before = [answer(store, q)[0] for q in questions]

# ---------------- 인덱스 업데이트 ----------------
new_docs = load_docs(config.UPDATES_DIR)                                   # 바뀐 FAQ (활동비 문항 추가) + 새 공지 (수료 조건 · OB 혜택)
changed = {d["doc_id"] for d in new_docs}
keep = [i for i, c in enumerate(store.chunks) if c["doc_id"] not in changed]
new_chunks = make_chunks(new_docs, config.CHUNK_SIZE, config.OVERLAP)
new_vecs = llm.embed([c["text"] for c in new_chunks])                     # 새 청크만 임베딩

chunks = [store.chunks[i] for i in keep] + new_chunks
for i, c in enumerate(chunks):
    c["id"] = i
updated = VectorStore(chunks, np.vstack([store.vectors[keep], new_vecs]))
print("바뀐 문서 : %s" % ", ".join(sorted(changed)))
print("지운 청크 %d개, 새로 임베딩한 청크 %d개, 그대로 둔 청크 %d개\n"
      % (len(store.chunks) - len(keep), len(new_chunks), len(keep)))

for q, b in zip(questions, before):
    a, hits = answer(updated, q)
    print("질문 : %s" % q)
    print("   %s %s" % (pad("업데이트 전 :", 14), b))
    print("   %s %s" % (pad("업데이트 후 :", 14), a))
    print("   출처 : %s\n" % sources(hits[:2]))

if "--save" in sys.argv:
    updated.save()
    print("저장 : index/ 를 업데이트된 인덱스로 바꿨습니다 (되돌리려면 step1 → step2를 다시)")
else:
    print("원래 index/ 는 그대로입니다 (--save 를 붙이면 바뀐 인덱스를 저장)")
print("LLM의 파라미터는 하나도 바뀌지 않았다 — 바뀐 것은 검색할 문서뿐\n")
print(llm.cost_report())
print("다음 : python step7_web.py   (보너스 : python chat.py)")
