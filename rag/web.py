"""웹 챗봇 서버 (FastAPI) — 화면 파일 (web/)을 보내 주고, 질문이 오면 RAG로 답한다.

브라우저 ── GET  /                            ──▶ web/index.html  (+ /static/style.css · /static/app.js)
브라우저 ── POST /api/chat {"question": "…"}  ──▶ chat() ──▶ answer()  (Step 1 ~ 4에서 만든 RAG)
        ◀── {"answer": "…", "sources": [{"n": 1, "title": "…", "text": "…"}, …], "seconds": 1.6}"""
import time

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import config
from rag.pipeline import answer
from rag.util import short

WEB_DIR = config.ROOT / "web"


class Question(BaseModel):
    question: str


def source_list(hits):
    """검색 결과 [(점수, 청크), ...] → 화면에 보여 줄 출처 목록"""
    return [{"n": i + 1, "title": "%s > %s" % (c["doc_id"], c["section"]), "text": c["text"]}
            for i, (_, c) in enumerate(hits)]


def create_app(store):
    app = FastAPI(title="쿠다봇")
    app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

    @app.middleware("http")
    async def no_cache(request, call_next):
        """CSS · JS를 고친 뒤 새로고침하면 바로 보이도록 브라우저가 저장해 두지 않게 한다"""
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/")
    def home():
        return FileResponse(WEB_DIR / "index.html")

    @app.get("/api/info")
    def info():
        return {"chunks": len(store.chunks), "model": config.CHAT_MODEL}

    @app.post("/api/chat")
    def chat(q: Question):
        t0 = time.time()
        question, error = q.question.strip()[:500], False
        if not question:
            return {"answer": "질문을 입력해 주세요.", "sources": [], "seconds": 0}
        try:
            # ---------------- TODO 6 ----------------
            reply, hits = answer(store, question, config.TOP_K)
            # ----------------------------------------
        except Exception as e:                  # 에러도 화면에 보여 준다 (예 : 키가 틀리면 AuthenticationError)
            print("  [에러] %s : %s" % (type(e).__name__, e))
            reply, hits, error = "서버 에러 : %s — 서버 터미널을 확인하세요." % type(e).__name__, [], True
        sec = time.time() - t0
        print("[%s] %.1f초  %s → %s" % (time.strftime("%H:%M:%S"), sec, short(question, 28), short(reply, 44)))
        return {"answer": reply, "sources": source_list(hits), "seconds": round(sec, 2), "error": error}

    return app
