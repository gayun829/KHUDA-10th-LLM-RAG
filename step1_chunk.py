"""Step 1. Chunking — 문서 6개를 청크로 자른다.   TODO 1 : rag/chunking.py 의 chunk_text
실행 : python step1_chunk.py               (청크 크기 200자, 겹침 40자 — config.py)
       python step1_chunk.py 100 20        (크기를 바꿔 보기 → Step 2부터 다시)"""
import json
import sys

import config
from rag.chunking import chunk_text, load_docs, make_chunks, split_sections
from rag.util import mark, pad, short

size = int(sys.argv[1]) if len(sys.argv) > 1 else config.CHUNK_SIZE
overlap = int(sys.argv[2]) if len(sys.argv) > 2 else config.OVERLAP

# ---------------- Check ----------------
got = chunk_text("가나다라마바사아자차", size=4, overlap=1)
print("Check : chunk_text('가나다라마바사아자차', size=4, overlap=1)")
print("        → %s" % got)
print("        ['가나다라', '라마바사', '사아자차'] 이어야 함  %s\n" % mark(got == ["가나다라", "라마바사", "사아자차"]))

# ---------------- 문서 → 청크 ----------------
docs = load_docs(config.DOCS_DIR)
chunks = make_chunks(docs, size, overlap)
n_sections = sum(len(split_sections(d["text"])) for d in docs)
print("문서 %d개 (총 %s자) → 소제목 %d개 → 청크 %d개   (크기 %d자, 겹침 %d자)"
      % (len(docs), format(sum(len(d["text"]) for d in docs), ","), n_sections, len(chunks), size, overlap))
print("청크 길이 : 평균 %d자, 가장 긴 것 %d자\n" % (sum(len(c["text"]) for c in chunks) / len(chunks),
                                         max(len(c["text"]) for c in chunks)))

print("%s %s %s" % (pad("문서", 16), pad("제목", 36), "청크 수"))
for d in docs:
    print("%s %s %4d" % (pad(d["doc_id"], 16), pad(short(d["title"], 34), 36), sum(c["doc_id"] == d["doc_id"] for c in chunks)))

lost = [s for d in docs for s, body in split_sections(d["text"]) if len(body) > size
        and not any(c["doc_id"] == d["doc_id"] and c["section"] == s for c in chunks)]
if lost:
    print("\n※ %d자보다 긴 소제목 %d개가 청크로 하나도 안 만들어졌습니다 → TODO 1을 확인하세요" % (size, len(lost)))

example = next((c for c in chunks if c["doc_id"] == "rules" and "제20조" in c["section"]), chunks[0])
print("\n예시 청크 (id %d) ─────────────────────────" % example["id"])
print(example["text"])
print("────────────────────────────────────────────")

config.INDEX_DIR.mkdir(exist_ok=True)
(config.INDEX_DIR / "chunks.json").write_text(json.dumps(chunks, ensure_ascii=False, indent=1), encoding="utf-8")
print("저장 : index/chunks.json   →   다음 : python step2_embed.py")
