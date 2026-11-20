"""OpenAI API를 부르는 곳 — embedding · chat, 그리고 쓴 토큰으로 비용 계산."""
import numpy as np
from openai import OpenAI

import config

_client = None
USAGE = {"embed": 0, "chat_in": 0, "chat_out": 0}      # 이번 실행에서 쓴 토큰 수 (비용 계산용)


def get_client():
    global _client
    if _client is None:
        _client = OpenAI()          # 환경변수 OPENAI_API_KEY (= .env 파일)에서 키를 읽는다
    return _client


def embed(texts, batch_size=64):
    """문자열 리스트 → (개수, 1536) 행렬. 각 행(벡터)의 길이는 1로 맞춘다."""
    client = get_client()
    vectors = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]            # 한 번에 64개씩 보낸다 (요청 한 번에 최대 2,048개)
        # ---------------- TODO 2 ----------------
        # 힌트 : resp = client.embeddings.create(model=config.EMBED_MODEL, input=batch)
        resp = None
        # ----------------------------------------
        if resp is None:                           # TODO 2를 아직 채우지 않았다
            return np.zeros((0, 0), dtype=np.float32)
        USAGE["embed"] += resp.usage.total_tokens
        vectors += [d.embedding for d in sorted(resp.data, key=lambda d: d.index)]
    X = np.array(vectors, dtype=np.float32)
    return X / np.linalg.norm(X, axis=1, keepdims=True)       # 길이를 1로 → 내적 = cosine similarity


def chat(messages, model=None):
    """messages = [{"role": "system" | "user" | "assistant", "content": "..."}, ...] → 답 (문자열)"""
    kwargs = {"model": model or config.CHAT_MODEL, "messages": messages}
    if config.REASONING_EFFORT:
        kwargs["reasoning_effort"] = config.REASONING_EFFORT
    resp = get_client().chat.completions.create(**kwargs)
    USAGE["chat_in"] += resp.usage.prompt_tokens
    USAGE["chat_out"] += resp.usage.completion_tokens
    return (resp.choices[0].message.content or "").strip()


def cost_report():
    """이번 실행에서 쓴 토큰과 대략의 비용"""
    e_in, _ = config.PRICE.get(config.EMBED_MODEL, (0.0, 0.0))
    c_in, c_out = config.PRICE.get(config.CHAT_MODEL, (0.0, 0.0))
    usd = (USAGE["embed"] * e_in + USAGE["chat_in"] * c_in + USAGE["chat_out"] * c_out) / 1e6
    return "[비용] 토큰 : embedding %d, chat 입력 %d / 출력 %d  →  $%.5f (약 %.1f원)" % (
        USAGE["embed"], USAGE["chat_in"], USAGE["chat_out"], usd, usd * config.USD_KRW)
