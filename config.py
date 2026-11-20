"""실습 설정 — 모델 이름 · 가격 · RAG 설정 · 경로를 한곳에 모아 둡니다."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")                      # .env 파일의 OPENAI_API_KEY를 환경변수로 읽어 온다
_key = os.getenv("OPENAI_API_KEY", "")
if _key != _key.strip(" \t\"'“”‘’"):            # 붙여넣다 섞인 앞뒤 공백 · 따옴표는 떼어 낸다
    os.environ["OPENAI_API_KEY"] = _key.strip(" \t\"'“”‘’")

DOCS_DIR = ROOT / "data" / "docs"               # 검색할 문서 (KHUDA 회칙 · 홈페이지 안내 6개)
UPDATES_DIR = ROOT / "data" / "updates"         # Step 6에서 쓰는 '바뀐 문서' (FAQ 문항 추가 · 수료 조건 공지)
EVAL_PATH = ROOT / "data" / "eval.jsonl"        # Step 5에서 쓰는 평가 질문 20개
INDEX_DIR = ROOT / "index"                      # Step 1 ~ 2가 만든 청크와 임베딩이 여기 저장된다

# ---------------- OpenAI 모델 (2026년 11월 기준, 가장 싼 축) ----------------
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")   # 1536차원
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-6-luna")
REASONING_EFFORT = os.getenv("REASONING_EFFORT", "none")            # none = 생각(추론) 없이 바로 답 → 빠르고 싸다
                                                                    # 추론 설정이 없는 모델로 바꾸면 빈 값("")으로
PRICE = {   # 1M tokens 당 달러 (입력, 출력)
    "text-embedding-3-small": (0.02, 0.0),
    "text-embedding-3-large": (0.13, 0.0),
    "gpt-6-luna": (0.10, 0.50),
}
USD_KRW = 1350                                  # 원화 환산용 (2026년 11월 대략)

# ---------------- RAG 설정 ----------------
CHUNK_SIZE = 200        # 청크 하나의 최대 글자 수 (소제목이 이보다 길면 잘라서 여러 청크로)
OVERLAP = 40            # 이웃한 청크끼리 겹치는 글자 수
TOP_K = 4               # 질문 하나에 가져올 청크 수

# ---------------- Step 7 웹 챗봇 ----------------
WEB_PORT = int(os.getenv("WEB_PORT", "8001"))       # 노트북 브라우저 → http://localhost:8001 (ssh -L 8001:localhost:8001)
