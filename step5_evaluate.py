"""Step 5. Evaluate — 평가 질문 20개로 '검색'과 '답'을 따로 채점한다.   TODO 5 : rag/metrics.py 의 recall_at_k
실행 : python step5_evaluate.py      (LLM을 20번 부릅니다, 30초쯤)"""
from collections import defaultdict

import config
from rag import llm
from rag.metrics import answer_ok, first_hit_rank, load_eval, recall_at_k
from rag.prompt import build_messages
from rag.store import VectorStore
from rag.util import mark, pad, short

# ---------------- Check ----------------
c1 = recall_at_k(["가나다", "라마바"], ["마바"], 1)
c2 = recall_at_k(["가나다", "라마바"], ["마바"], 2)
c3 = recall_at_k(["가나다", "라마바"], ["나다", "없음"], 2)
print("Check : recall_at_k(['가나다', '라마바'], ['마바'], k=1) = %.1f  (0.0이어야 함)" % c1)
print("        recall_at_k(['가나다', '라마바'], ['마바'], k=2) = %.1f  (1.0이어야 함)" % c2)
print("        recall_at_k(['가나다', '라마바'], ['나다', '없음'], k=2) = %.1f  (0.5이어야 함)  %s\n"
      % (c3, mark((c1, c2, c3) == (0.0, 1.0, 0.5))))

items = load_eval(config.EVAL_PATH)
store = VectorStore.load()
Q = llm.embed([it["question"] for it in items])            # 질문 20개를 한 번에 임베딩
K = config.TOP_K

# ---------------- (1) 검색 평가 : 정답의 근거가 top-k 안에 들어왔나 ----------------
print("(1) 검색 평가 — 근거 문장이 위에서 몇 번째 청크에 있었나 (dense 검색, 10등까지)")
print("%s %s %s %5s %5s %5s" % (pad("번호", 4), pad("유형", 9), pad("질문", 50), "R@1", "R@%d" % K, "순위"))
r1s, rks, rrs = [], [], []
for it, q in zip(items, Q):
    if not it["evidence"]:
        continue                                            # 답이 없는 질문은 검색 평가에서 뺀다
    texts = [c["text"] for _, c in store.search(q, k=10)]
    r1, rk = recall_at_k(texts, it["evidence"], 1), recall_at_k(texts, it["evidence"], K)
    rank = first_hit_rank(texts, it["evidence"])
    r1s.append(r1), rks.append(rk), rrs.append(1 / rank if rank else 0.0)
    print("%s %s %s %5.1f %5.1f %5s" % (pad(it["id"], 4), pad(it["type"], 9), pad(short(it["question"], 50), 50),
                                        r1, rk, rank or "-"))
print("평균 : Recall@1 %.2f   Recall@%d %.2f   MRR %.2f   (질문 %d개)\n"
      % (sum(r1s) / len(r1s), K, sum(rks) / len(rks), sum(rrs) / len(rrs), len(rks)))

# ---------------- (2) 답 평가 : RAG로 답하고 키워드로 자동 채점 ----------------
print("(2) 답 평가 — RAG 답 (top-%d 청크) 을 키워드로 자동 채점 (답이 없는 질문은 '찾을 수 없습니다'가 정답)" % K)
by_type = defaultdict(list)
for it, q in zip(items, Q):
    ans = llm.chat(build_messages(it["question"], store.search(q, k=K)))
    ok = answer_ok(ans, it)
    by_type[it["type"]].append(ok)
    print("%s %s %s  %s" % ("O" if ok else "X", pad(it["id"], 4), pad(short(it["question"], 34), 34), short(ans, 60)))
n_ok = sum(sum(v) for v in by_type.values())
print("정답 %d / %d   (%s)" % (n_ok, len(items), ",  ".join("%s %d/%d" % (t, sum(v), len(v)) for t, v in by_type.items())))

print("\n" + llm.cost_report())
print("다음 : python step6_update.py")
