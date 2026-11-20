"""아주 작은 Vector DB — 청크와 임베딩 행렬을 파일로 저장하고, 질문과 가장 가까운 청크를 찾는다."""
import json

import numpy as np

import config


class VectorStore:
    def __init__(self, chunks, vectors):
        self.chunks = chunks          # [{"id", "doc_id", "section", "text"}, ...]
        self.vectors = vectors        # (청크 수, 차원) 행렬, 각 행의 길이 = 1

    def scores(self, query_vec):
        """질문 벡터와 모든 청크의 cosine similarity (길이가 1이므로 내적과 같다)"""
        return self.vectors @ query_vec

    def search(self, query_vec, k=4):
        """cosine similarity가 가장 큰 청크 k개 → [(점수, 청크), ...] (점수가 큰 순서)"""
        # ---------------- TODO 3 ----------------
        # 힌트 (두 줄 그대로) :
        #   scores = self.scores(query_vec)          # 청크마다 점수 하나
        #   top = np.argsort(-scores)[:k]             # 점수가 큰 순서대로 k개의 번호
        scores = np.zeros(len(self.chunks))
        top = np.arange(min(k, len(self.chunks)))
        # ----------------------------------------
        return [(float(scores[i]), self.chunks[i]) for i in top]

    # ---------------- 저장 · 불러오기 (읽지 않아도 됩니다) ----------------
    def save(self, folder=config.INDEX_DIR):
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "chunks.json").write_text(json.dumps(self.chunks, ensure_ascii=False, indent=1), encoding="utf-8")
        np.save(folder / "embeddings.npy", self.vectors)

    @classmethod
    def load(cls, folder=config.INDEX_DIR):
        if not (folder / "embeddings.npy").exists():
            raise SystemExit("index/embeddings.npy가 없습니다 → 먼저 python step2_embed.py 를 실행하세요")
        chunks = json.loads((folder / "chunks.json").read_text(encoding="utf-8"))
        return cls(chunks, np.load(folder / "embeddings.npy"))
