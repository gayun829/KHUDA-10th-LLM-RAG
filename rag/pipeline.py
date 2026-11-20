"""질문 하나를 처음부터 끝까지 : 검색 → 프롬프트 → LLM 답."""
import config
from rag import llm
from rag.prompt import build_messages


def retrieve(store, question, k=config.TOP_K):
    """질문을 임베딩해서 가장 가까운 청크 k개 → [(점수, 청크), ...]"""
    return store.search(llm.embed([question])[0], k)


def answer(store, question, k=config.TOP_K):
    """RAG 한 번 : (답, 검색 결과)"""
    hits = retrieve(store, question, k)
    return llm.chat(build_messages(question, hits)), hits


def sources(hits):
    return ", ".join("[%d] %s > %s" % (i + 1, c["doc_id"], c["section"]) for i, (_, c) in enumerate(hits))
