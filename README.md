# Week 8 - RAG from Scratch

**AI Reverse Engineering**

**KHUDA** (경희대학교 데이터분석 AI 동아리)의 회칙 · 홈페이지 안내 문서 6개로, 동아리 문의에 답하는 RAG를 처음부터 만들고
마지막에 **웹 챗봇 화면** (HTML · CSS · JS)을 붙입니다.
OpenAI API는 **embedding**과 **chat** 두 가지만 쓰고, 나머지(청크 자르기 · 벡터 검색 · 평가 · 웹 서버 · 채팅 화면)는 직접 짭니다.

```
[미리 한 번]  문서 ──▶ Step 1 Chunking ──▶ Step 2 Embedding ──▶ index/ (작은 Vector DB)
[질문마다]    질문 ──▶ Embedding ──▶ Step 3 Search (top-k) ──▶ Step 4 Prompt + LLM ──▶ 답 + 출처
[확인 · 업데이트]  Step 5 평가 (Recall@k · 답 채점)  ·  Step 6 문서 업데이트
[웹 챗봇]      노트북 브라우저 ──POST /api/chat──▶ Step 7 서버 (EC2 :8001) ──▶ RAG ──▶ 말풍선 · 출처
```

**TODO는 7개, 모두 1 ~ 2줄이고 바로 위 주석에 거의 정답인 힌트가 있습니다. 약 60분.**
문서는 2026년 11월 KHUDA 회칙과 홈페이지 글을 그대로 옮긴 것입니다. 동아리 내부 규정은 LLM이 미리 알 수 없는 내용이라 RAG의 효과가 잘 보입니다.

## 학습 목표

1. **RAG를 처음부터 만든다** — 문서를 청크로 잘라 임베딩해 두고, 질문과 가까운 청크를 찾아 프롬프트에 넣어 답하게 한다 (Step 1 ~ 4)
2. **LLM만 vs RAG** — 같은 질문에 LLM만 쓴 답과 RAG의 답을 비교하고, 문서에 없는 질문 (q19 · q20)에는 "찾을 수 없습니다"라고 답하는지 확인한다 (Step 4 · 5)
3. **검색과 답을 따로 평가한다** — Recall@k · MRR과 정답률로 틀린 곳이 검색인지 생성인지 가려내고, 청크 크기를 바꿔 (`python step1_chunk.py 100 20`) 점수를 비교한다 (Step 5)
4. **다시 학습하지 않고 지식을 바꾼다** — 바뀐 문서의 청크만 바꿔 끼워 답을 바꾼다. 논문의 index hot-swapping (Step 6)
5. **웹 챗봇을 붙인다** — FastAPI 서버와 fetch로 RAG에 채팅 화면을 붙여 노트북 브라우저에서 대화한다 (Step 7)

---

## 0. EC2 접속

강사에게 받은 **키 파일(`.pem`)** 과 **IP 주소**를 씁니다. 사용자 이름은 `ubuntu`입니다.

**Mac / Linux** (터미널)

```bash
chmod 400 ~/Downloads/rag-key.pem                 # 키 권한 (처음 한 번)
ssh -i ~/Downloads/rag-key.pem -L 8001:localhost:8001 ubuntu@<IP 주소>     # 처음 접속 때 나오는 질문에는 yes
```

**Windows** (PowerShell)

```powershell
icacls.exe .\rag-key.pem /reset
icacls.exe .\rag-key.pem /grant:r "$($env:USERNAME):(R)"
icacls.exe .\rag-key.pem /inheritance:r
ssh -i .\rag-key.pem -L 8001:localhost:8001 ubuntu@<IP 주소>
```

`-L 8001:localhost:8001` 은 노트북의 8001번을 EC2의 8001번으로 잇는 통로(SSH 터널)입니다. Step 7에서 만든 웹 챗봇을 노트북 브라우저로 볼 때 씁니다.
이미 열린 SSH(22번) 연결 안으로 보내기 때문에 보안 그룹에서 8001번을 따로 열지 않아도 됩니다.

* 접속할 때 `Could not request local forwarding.` 이 보이면 : 접속은 됐지만 **통로는 안 열린 것** (노트북에서 이미 8001번을 쓰는 중).
  `exit` 후 `-L 8002:localhost:8001` 로 다시 접속하고, Step 7에서는 `http://localhost:8002` 를 엽니다.
* 통로는 그 SSH 창이 열려 있는 동안만 이어집니다. 창을 닫으면 Step 7 화면도 끊깁니다.

**(선택) VS Code로 접속** — 확장 `Remote - SSH` 설치 → `F1` → `Remote-SSH: Open SSH Configuration File...` 에 아래를 추가 →
`F1` → `Remote-SSH: Connect to Host...` → `rag` → 폴더 열기 `/home/ubuntu/rag-practice`

```
Host rag
    HostName <IP 주소>
    User ubuntu
    IdentityFile ~/Downloads/rag-key.pem
```

## 1. 설치 (5분)

```bash
git clone https://github.com/gaeng02/KHUDA-10th-LLM-RAG.git rag-practice    # ls ~ 에 READY.txt가 있으면 (강사가 준비함) 생략
cd rag-practice
bash setup.sh                       # 가상환경 .venv + 패키지 + .env 만들기 (READY.txt가 있으면 생략해도 됨)
source .venv/bin/activate           # 터미널을 새로 열 때마다 (프롬프트 앞에 (.venv)가 붙으면 OK)
nano .env                           # OPENAI_API_KEY=sk-... 입력 → 저장 Ctrl+O, Enter → 나가기 Ctrl+X
python step0_check.py               # embedding OK / chat OK 가 나오면 준비 끝
```

## 2. 실습 순서

| Step | 실행 | 채울 곳 (TODO) | 하는 일 |
|---|---|---|---|
| 1 | `python step1_chunk.py` | TODO 1 · `rag/chunking.py` `chunk_text` | 문서 → 청크 (200자, 40자 겹침) |
| 2 | `python step2_embed.py` | TODO 2 · `rag/llm.py` `embed` | 청크 → 벡터 (OpenAI embedding API) |
| 3 | `python step3_search.py "질문"` | TODO 3 · `rag/store.py` `search` | cosine similarity로 top-k 청크 찾기 |
| 4 | `python step4_generate.py "질문"` | TODO 4 · `rag/prompt.py` `build_messages` | 검색한 청크를 프롬프트에 넣어 답하기 (LLM만 vs RAG) |
| 5 | `python step5_evaluate.py` | TODO 5 · `rag/metrics.py` `recall_at_k` | 평가 질문 20개 : 검색 (Recall@k, MRR) + 답 (자동 채점) |
| 6 | `python step6_update.py` | 없음 | 모델은 그대로, 문서만 바꿔서 지식 업데이트 (논문의 index hot-swapping) |
| 7 | `python step7_web.py` → 노트북 브라우저 `http://localhost:8001` | TODO 6 · `rag/web.py`<br>TODO 7 · `web/app.js` | 웹 챗봇 : 서버가 RAG에 묻고, 화면이 서버에 묻는다 ([아래 6번](#6-step-7--웹-챗봇)) |
| 보너스 | `python chat.py` | 없음 | 터미널 챗봇 : 이어지는 질문을 혼자서도 통하는 질문으로 다시 써서 검색 |

* 각 스크립트는 맨 위에서 **Check** (작은 예제로 TODO 확인, ✓ / ✗)를 먼저 출력합니다.
* TODO를 아직 안 채워도 에러로 죽지 않고 "TODO n을 채우세요"라고 알려 줍니다.
* `python step1_chunk.py 100 20`처럼 청크 크기를 바꾼 뒤 Step 2, 5를 다시 돌려 비교해 보세요.

## 3. 파일 구조

```
rag-practice/
├── config.py            모델 이름 · 가격 · 청크 크기 · top-k
├── step0_check.py ~ step6_update.py, chat.py
├── step7_web.py         웹 챗봇 서버 실행 (FastAPI)
├── rag/
│   ├── chunking.py      문서 읽기 · 소제목으로 나누기 · 청크 자르기     ← TODO 1
│   ├── llm.py           OpenAI embedding · chat 호출, 비용 계산        ← TODO 2
│   ├── store.py         작은 Vector DB (numpy 행렬 + 저장/불러오기)    ← TODO 3
│   ├── prompt.py        system 프롬프트 · 청크를 넣은 messages         ← TODO 4
│   ├── metrics.py       Recall@k · MRR · 답 자동 채점                  ← TODO 5
│   ├── web.py           웹 서버 : 화면 보내기 · /api/chat (RAG에 묻기)   ← TODO 6
│   ├── pipeline.py      검색 → 프롬프트 → 답
│   └── util.py          출력 줄 맞추기
├── web/                 채팅 화면 : index.html (뼈대) · style.css (모양) · app.js (동작)  ← TODO 7
├── data/
│   ├── docs/            KHUDA 문서 6개 (.md) : 소개 · 활동 · 심화 트랙 · 모집 안내 · 자주 묻는 질문 · 회칙
│   ├── updates/         Step 6에서 쓰는 바뀐 문서 (FAQ에 '활동비' 문항 추가, 수료 조건 · OB 혜택 공지)
│   └── eval.jsonl       평가 질문 20개 (질문 · 근거 문장 · 정답 키워드 · 유형)
└── index/               Step 1 ~ 2가 만드는 청크와 임베딩 (자동 생성)
```

## 4. 모델과 비용

| 용도 | 모델 | 가격 (1M tokens당) |
|---|---|---|
| Embedding | `text-embedding-3-small` (1536차원) | $0.02 |
| 답 생성 | `gpt-6-luna` (`reasoning_effort="none"`으로 추론 없이 빠르게) | 입력 $0.10 / 출력 $0.50 |

청크 69개(약 10,700 토큰)를 모두 임베딩하는 데 약 0.3원, 질문 하나에 RAG로 답하는 데 약 0.1원이 듭니다.
스크립트마다 마지막 줄에 이번 실행의 토큰 수와 비용이 나옵니다. 처음부터 끝까지 다 해도 1인당 10원이 안 됩니다 (환율 1,350원 기준).
모델을 바꾸려면 `config.py`를 고치거나 `CHAT_MODEL=다른-모델 python step4_generate.py`처럼 환경변수로 줍니다.

## 5. 문제가 생기면

| 증상 | 해결 |
|---|---|
| `Permission denied (publickey)` | 사용자 이름이 `ubuntu`인지, `-i` 뒤의 키 파일 경로가 맞는지 확인 |
| `UNPROTECTED PRIVATE KEY FILE!` | Mac/Linux `chmod 400 키.pem`, Windows는 위의 `icacls` 세 줄 |
| `Connection timed out` | IP 주소 확인, 인스턴스가 켜져 있는지 강사에게 확인 |
| `ModuleNotFoundError: openai` | `source .venv/bin/activate` 를 안 했다 |
| `401` / `AuthenticationError` | `.env` 의 키가 틀렸거나 앞뒤에 공백 · 따옴표가 있다 |
| `429` / `RateLimitError` | 잠시 뒤 다시. 계속되면 강사에게 (크레딧 · 한도) |
| `404` / `model not found` | `config.py` 의 모델 이름 확인 |
| `index/...가 없습니다` | 앞 Step을 먼저 실행 (1 → 2 → 3 ...) |
| Step 7 `EC2의 8001번을 이미 쓰고 있습니다` | 먼저 켠 서버가 아직 켜져 있다 → 그 터미널에서 Ctrl+C (못 찾으면 `pkill -f step7_web`) |
| 브라우저 `ERR_CONNECTION_REFUSED` (연결을 거부했습니다) | 서버가 꺼져 있거나 ssh에 `-L 8001:localhost:8001` 없이 접속 → 6번 '안 열릴 때' |
| ssh 접속 때 `Could not request local forwarding.` | 노트북이 이미 8001번을 쓰는 중 → `exit` 후 `-L 8002:localhost:8001`, 브라우저는 `localhost:8002` |
| 화면에 `(TODO 6 …)` · `(TODO 7 …)` 말풍선 | 해당 TODO를 채운다. `rag/web.py`를 고쳤으면 서버를 Ctrl+C 후 다시 실행, `app.js`는 새로고침만 |
| 화면에 `서버 에러 : AuthenticationError` | `.env`의 키 확인 (자세한 내용은 서버 터미널에) |

## 6. Step 7 · 웹 챗봇

지금까지 만든 RAG에 **채팅 화면**을 붙입니다. EC2에서 웹 서버(FastAPI)가 화면 파일을 보내 주고,
화면에서 질문하면 서버가 `pipeline.answer()`로 답해서 말풍선 · 출처로 보여 줍니다.

```
노트북 브라우저 ── GET  /                  ──▶ web/index.html · style.css · app.js  (화면)
노트북 브라우저 ── POST /api/chat           ──▶ rag/web.py chat() ──▶ answer()      (TODO 6 : 서버가 RAG에 묻기)
     {"question": "OT도 꼭 가야 해?"}         ◀── {"answer": "…", "sources": [{"n", "title", "text"}, …], "seconds": 1.4}
app.js askServer()가 보내고 받는다 (TODO 7 : 화면이 서버에 묻기) → 말풍선 · [1] 번호 · 출처 목록으로 그린다
```

**1. 서버 켜기 (EC2)**

```bash
source .venv/bin/activate
python step7_web.py           # 켜 둔 채로 둔다. 끄기 Ctrl+C (마지막 줄에 토큰 · 비용)
```

**2. 내 노트북 브라우저에서 `http://localhost:8001`**

```
노트북 브라우저 → localhost:8001 ══ SSH (22번, 이미 열린 접속) ══▶ EC2 안의 localhost:8001 (step7_web.py)
                   └ 접속할 때 붙인 -L 8001:localhost:8001 이 이 통로를 만든다 → 보안 그룹에서 8001번을 열 필요 없음
```

* 접속할 때 ssh에 `-L 8001:localhost:8001` 을 붙였으면 바로 열립니다 (0번 참고).
* VS Code Remote-SSH는 서버가 켜지면 자동으로 이어 주고 오른쪽 아래에 **Open in Browser** 를 띄웁니다 (아래 **PORTS** 탭의 주소를 열어도 됩니다).
* 질문할 때마다 서버 터미널에 한 줄씩 찍힙니다. 답의 **[1]** 을 누르면 그 답이 나온 청크가 펼쳐집니다.

**안 열릴 때** — 위에서부터 차례로

| 보이는 것 | 원인 | 할 일 |
|---|---|---|
| 브라우저 `ERR_CONNECTION_REFUSED` (연결을 거부했습니다) | 서버가 꺼져 있다 | EC2 터미널에 `화면 : http://localhost:8001` 줄이 떠 있는지 → 없으면 `python step7_web.py` |
| 〃 (서버는 켜져 있는데) | `-L` 없이 접속했다 | 서버는 둔 채로 **새 터미널**에서 `ssh -i 키.pem -L 8001:localhost:8001 ubuntu@IP` 한 번 더 접속 |
| ssh 접속 때 `Could not request local forwarding.` | 노트북이 이미 8001번을 쓰는 중 (접속은 되지만 통로만 안 열림) | `-L 8002:localhost:8001` 로 접속 → 브라우저는 `http://localhost:8002` |
| EC2에서 `EC2의 8001번을 이미 쓰고 있습니다` | 먼저 켠 서버가 아직 켜져 있다 | 그 터미널에서 Ctrl+C, 못 찾으면 `pkill -f step7_web` |

* 서버가 정상인지만 따로 보려면 EC2의 다른 터미널에서 `curl -s localhost:8001/api/info` → `{"chunks":69, …}` 가 나오면 서버는 정상 (그러면 통로 문제).
* 통로는 서버를 켠 SSH 창이 아니어도 됩니다. `-L` 을 붙인 SSH 창이 **하나라도 열려 있으면** 이어집니다.

**3. TODO 6 · 7** — 안 채운 TODO는 화면에 `(TODO 6 …)` · `(TODO 7 …)` 말풍선으로 보입니다.

* TODO 6 (`rag/web.py`) : 서버가 받은 질문으로 `answer()` 를 부른다. 고친 뒤에는 서버를 **Ctrl+C 후 다시 실행**.
* TODO 7 (`web/app.js`) : `fetch` 로 `/api/chat` 에 질문을 보내고 JSON 답을 받는다. 고친 뒤에는 브라우저 **새로고침**만.

**화면 파일 세 개 (`web/`)**

| 파일 | 역할 | 해 볼 것 (선택) |
|---|---|---|
| `index.html` | 뼈대 : 머리글 · 대화창 · 예시 질문 버튼 · 입력창 | 봇 이름, 인사말, 예시 질문 바꾸기 |
| `style.css` | 모양 : 맨 위 `:root` 변수 (색 · 둥글기 · 글꼴) | `--accent` 색을 바꾸고 새로고침 |
| `app.js` | 동작 : 보내기 → 점 세 개 → `askServer()` → 말풍선 · [1] · 출처 | 도전 : `chat.py`의 질문 다시 쓰기를 붙여 이어지는 질문 받기 |

* 서버의 글은 `textContent` 로 넣습니다 (`innerHTML` 로 넣으면 답에 섞인 HTML이 그대로 실행될 수 있습니다).
* 주소 뒤에 `?q=질문` 을 붙이면 열자마자 그 질문을 보냅니다. 예 : `http://localhost:8001/?q=러닝메이트가 뭐야`
* 강사가 보안 그룹에서 8001번을 열어 둔 경우에만 `-L` 없이 `http://<EC2 공인 IP>:8001` 로도 열립니다 (휴대폰에서도). 켜 둔 동안 주소를 아는 누구나 질문할 수 있어 그만큼 API 비용이 듭니다.
