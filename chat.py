"""보너스. 터미널 챗봇 '쿠다봇' — 대화 기록을 보고 질문을 다시 쓴 뒤 검색 (query rewriting)
실행 : python chat.py        끝내기 : q

이어지는 질문 ("그럼 지각은?")은 그대로 검색하면 '그거'가 무엇인지 몰라 엉뚱한 청크가 나온다.
→ 앞 대화를 보고 혼자서도 뜻이 통하는 질문으로 먼저 고쳐 쓴 뒤 검색한다.
예 : "무단 결석하면 어떻게 돼?" 다음에 "그럼 지각은?" → "세션에 무단으로 지각하면 어떻게 되나요?" """
from rag import llm
from rag.pipeline import answer, sources
from rag.store import VectorStore

REWRITE = """아래 대화를 보고, 마지막 질문을 앞 대화를 몰라도 뜻이 통하는 하나의 질문으로 다시 써라.
질문만 한 줄로 출력하라. 고칠 필요가 없으면 그대로 출력하라.

{history}

마지막 질문: {question}"""

store = VectorStore.load()
history = []
print("쿠다봇입니다. KHUDA 지원 · 활동 · 회칙에 대해 물어보세요. (끝내기 : q)")
while True:
    try:
        question = input("\n나 > ").strip()
    except (EOFError, KeyboardInterrupt):
        break
    if question.lower() in ("q", "quit", "exit"):
        break
    if not question:
        continue
    search_q = question
    if history:
        h = "\n".join("%s: %s" % ("질문자" if role == "user" else "쿠다봇", text) for role, text in history[-6:])
        search_q = llm.chat([{"role": "user", "content": REWRITE.format(history=h, question=question)}]) or question
    reply, hits = answer(store, search_q)
    print("쿠다봇 > %s" % reply)
    if search_q != question:
        print("   (다시 쓴 질문 : %s)" % search_q)
    print("   (출처 : %s)" % sources(hits))
    history += [("user", question), ("assistant", reply)]

print("\n" + llm.cost_report())
