"""Step 2. Embedding — 청크를 벡터로 바꿔 저장한다.   TODO 2 : rag/llm.py 의 embed
실행 : python step2_embed.py      (OpenAI API를 부릅니다, 몇 초)"""
import json
import sys
import time

import numpy as np

import config
from rag import llm
from rag.store import VectorStore

path = config.INDEX_DIR / "chunks.json"
if not path.exists():
    sys.exit("index/chunks.json이 없습니다 → 먼저 python step1_chunk.py 를 실행하세요")
chunks = json.loads(path.read_text(encoding="utf-8"))

t0 = time.time()
X = llm.embed([c["text"] for c in chunks])
if X.size == 0:
    sys.exit("임베딩 결과가 비어 있습니다 → TODO 2 (rag/llm.py 의 embed)를 채우세요")
VectorStore(chunks, X).save()

print("청크 %d개 → 임베딩 행렬 %s   (%.1f초)" % (len(chunks), X.shape, time.time() - t0))
print("첫 번째 벡터의 앞부분 : %s ..." % np.round(X[0, :5], 4))
print("벡터 길이 (norm)      : %.4f   ← 1로 맞춰 두었으므로 내적 = cosine similarity" % np.linalg.norm(X[0]))
print("저장 : index/embeddings.npy (%.0f KB)\n" % (X.nbytes / 1024))

# ---------------- 맛보기 : 문장끼리 얼마나 비슷한가 ----------------
S = ["졸업생도 지원할 수 있나요?", "학교를 마친 사람도 신청돼요?", "회비는 언제까지 내요?"]
V = llm.embed(S)
print("문장 사이 cosine similarity (1에 가까울수록 뜻이 비슷하다)")
for i in range(len(S)):
    for j in range(i + 1, len(S)):
        print("   %.3f   %s  ↔  %s" % (V[i] @ V[j], S[i], S[j]))

print("\n" + llm.cost_report())
print("다음 : python step3_search.py")
