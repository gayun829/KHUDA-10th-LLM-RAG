"""문서 읽기 → 섹션('## 제목')으로 나누기 → 청크로 자르기."""
from pathlib import Path


def load_docs(folder):
    """폴더 안의 .md 파일을 모두 읽는다 → [{"doc_id", "title", "text"}]"""
    docs = []
    for path in sorted(Path(folder).glob("*.md")):
        text = path.read_text(encoding="utf-8")
        title = text.splitlines()[0].lstrip("#").strip()          # 첫 줄 '# 제목'
        docs.append({"doc_id": path.stem, "title": title, "text": text})
    return docs


def split_sections(text):
    """'## 소제목' 줄을 기준으로 나눈다 → [(소제목, 본문), ...]. 첫 소제목 전의 글은 '개요'."""
    sections, name, buf = [], "개요", []
    for line in text.splitlines():
        if line.startswith("# "):                 # 문서 제목 줄은 건너뛴다
            continue
        if line.startswith("## "):
            if "\n".join(buf).strip():
                sections.append((name, "\n".join(buf).strip()))
            name, buf = line[3:].strip(), []
        else:
            buf.append(line)
    if "\n".join(buf).strip():
        sections.append((name, "\n".join(buf).strip()))
    return sections


def chunk_text(text, size=200, overlap=40):
    """글자 수 기준으로 자른다 (sliding window). 이웃한 청크끼리 overlap 글자만큼 겹친다."""
    if len(text) <= size:
        return [text]
    chunks = []
    step = size - overlap                         # 다음 청크는 step 글자 뒤에서 시작
    for start in range(0, len(text), step):
        # ---------------- TODO 1 ----------------
        chunks.append(text[start:start + size])
        # ----------------------------------------
        if start + size >= len(text):             # 마지막 조각까지 담았으면 끝
            break
    return chunks


def make_chunks(docs, size=200, overlap=40):
    """모든 문서 → 청크 리스트. 청크 맨 앞에 '[문서 제목 > 소제목]'을 붙인다 (어디서 온 조각인지 알도록)."""
    chunks = []
    for d in docs:
        for section, body in split_sections(d["text"]):
            for piece in chunk_text(body, size, overlap):
                chunks.append({
                    "id": len(chunks),
                    "doc_id": d["doc_id"],
                    "section": section,
                    "text": "[%s > %s]\n%s" % (d["title"], section, piece),
                })
    return chunks
