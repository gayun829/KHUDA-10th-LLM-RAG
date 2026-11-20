"""검색한 청크를 프롬프트에 넣는 곳 (Augment)."""

SYSTEM = """너는 경희대학교 데이터분석 AI 동아리 KHUDA(쿠다)의 문의 챗봇이다.
아래 [문서]에 적힌 내용만 근거로, 한국어로 짧고 정확하게 답하라.
근거로 쓴 문서의 번호를 문장 끝에 [1]처럼 붙여라.
[문서]에서 답을 찾을 수 없으면 지어내지 말고 정확히 "문서에서 찾을 수 없습니다."라고만 답하라."""


def build_messages(question, hits):
    """hits = [(점수, 청크), ...] → chat API에 보낼 messages.
    청크에 [1], [2], ... 번호를 붙여 질문 앞에 넣는다."""
    # ---------------- TODO 4 ----------------
    # 힌트 (두 줄 그대로) :
    #   context = "\n\n".join("[%d] %s" % (i + 1, c["text"]) for i, (_, c) in enumerate(hits))
    #   user = "[문서]\n%s\n\n[질문]\n%s" % (context, question)
    user = question                         # 지금은 문서 없이 질문만 보낸다
    # ----------------------------------------
    return [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": user}]
