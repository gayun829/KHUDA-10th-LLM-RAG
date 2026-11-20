"""평가 — 검색을 잘했나 (Recall@k, MRR), 답을 잘했나 (키워드 자동 채점)."""
import json


def load_eval(path):
    """eval.jsonl → [{"id", "type", "question", "evidence", "keywords", "doc"}, ...]"""
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def recall_at_k(hit_texts, evidence, k):
    """검색한 청크 앞에서 k개 안에, 정답의 근거 문장(evidence)이 들어 있는 비율.
    근거가 1개면 0 또는 1, 근거가 2개(두 문서를 봐야 하는 질문)면 0, 0.5, 1."""
    top = "\n".join(hit_texts[:k])
    # ---------------- TODO 5 ----------------
    return sum(e in top for e in evidence) / len(evidence)
    # ----------------------------------------


def first_hit_rank(hit_texts, evidence):
    """근거가 처음 나온 순위 (1부터). 끝까지 없으면 None.  MRR = 평균(1 / 이 순위)"""
    for rank, text in enumerate(hit_texts, start=1):
        if any(e in text for e in evidence):
            return rank
    return None


def answer_ok(answer, item):
    """답 자동 채점 (공백과 쉼표는 무시).
    - 답이 있는 질문 : keywords의 각 묶음에서 하나 이상이 답에 들어 있어야 정답 ('찾을 수 없습니다'라고 하면 오답)
    - 답이 없는 질문 (evidence가 빈 리스트) : '찾을 수 없습니다'라고 해야 정답"""
    norm = lambda s: s.replace(" ", "").replace(",", "")
    a = norm(answer)
    refused = "찾을수없" in a
    if not item["evidence"]:
        return refused
    return (not refused) and all(any(norm(k) in a for k in group) for group in item["keywords"])
