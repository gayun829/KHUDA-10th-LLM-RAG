"""Step 7. 웹 챗봇 — 지금까지 만든 RAG에 채팅 화면 (HTML · CSS · JS)을 붙인다.
TODO 6 : rag/web.py   (서버가 RAG에 묻기)
TODO 7 : web/app.js   (화면이 서버에 묻기)          화면 꾸미기 : web/style.css 맨 위 변수

실행 : python step7_web.py   → 내 노트북 브라우저에서 http://localhost:8001
       EC2에 접속할 때 ssh 명령에 -L 8001:localhost:8001 을 붙여야 노트북의 8001번이 EC2의 8001번으로 이어진다
       (SSH 터널 : 이미 열린 22번 연결 안으로 보내므로 보안 그룹에서 8001번을 열지 않아도 된다)
       VS Code Remote-SSH는 자동으로 이어 준다 (아래 PORTS 탭 · 'Open in Browser')
끄기 : Ctrl+C  → 마지막 줄에 토큰 · 비용"""
import socket

import uvicorn

import config
from rag import llm
from rag.store import VectorStore
from rag.web import create_app

PORT = config.WEB_PORT

# 이미 켜 둔 서버가 있으면 같은 번호로 또 켤 수 없다 → 알아보기 쉬운 말로 알려 주고 끝낸다
with socket.socket() as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("0.0.0.0", PORT))
    except OSError:
        raise SystemExit("EC2의 %d번을 이미 쓰고 있습니다 (먼저 켠 서버가 아직 켜져 있다)\n"
                         "→ 그 터미널에서 Ctrl+C, 못 찾으면 : pkill -f step7_web  그다음 다시 python step7_web.py" % PORT)

store = VectorStore.load()
print("검색할 청크 %d개 · 답 모델 %s" % (len(store.chunks), config.CHAT_MODEL))
print("화면 : http://localhost:%d   ← 내 노트북 브라우저에서 (ssh에 -L %d:localhost:%d 을 붙여 접속했을 때)" % (PORT, PORT, PORT))
print("       (강사가 보안 그룹에서 %d번을 열어 둔 경우에만 : http://<EC2 공인 IP>:%d)" % (PORT, PORT))
print("끄기 : Ctrl+C\n")
uvicorn.run(create_app(store), host="0.0.0.0", port=PORT, log_level="warning")
print("\n" + llm.cost_report())
