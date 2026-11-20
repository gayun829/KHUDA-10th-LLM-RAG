// 쿠다봇 화면의 동작 : 질문 보내기 → 서버의 답 (JSON) 받기 → 말풍선 · 출처 그리기
const chat = document.getElementById("chat");
const form = document.getElementById("form");
const input = document.getElementById("input");
const send = document.getElementById("send");

// 서버에 질문을 보내고 답을 받는다 → {answer: "…", sources: [{n, title, text}, …], seconds: 1.6}
async function askServer(question) {
  // ---------------- TODO 7 ----------------
  const res = await fetch("/api/chat", {method: "POST",
  headers: {"Content-Type": "application/json"}, body: JSON.stringify({question: question})});
  return await res.json();
  // ----------------------------------------
}

// 말풍선 하나를 대화창 맨 아래에 붙인다 (who : "user" 또는 "bot")
function addMessage(who, text) {
  const msg = document.createElement("div");
  msg.className = "msg " + who;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;          // innerHTML이 아니라 textContent : 답에 HTML이 섞여 와도 글자로만 보인다
  msg.appendChild(bubble);
  chat.appendChild(msg);
  chat.scrollTop = chat.scrollHeight;
  return msg;
}

// 봇의 답 : 본문의 [1] [2]는 누를 수 있는 번호로, 아래에는 걸린 시간 · 출처 목록
function addAnswer(data) {
  const sources = data.sources || [];
  const msg = addMessage("bot", "");
  if (data.error) msg.classList.add("error");
  const bubble = msg.querySelector(".bubble");
  for (const part of String(data.answer ?? "").split(/(\[\d+\])/)) {
    const m = part.match(/^\[(\d+)\]$/);
    if (m && sources.some(s => s.n === Number(m[1]))) {
      const cite = document.createElement("span");
      cite.className = "cite";
      cite.textContent = m[1];
      cite.title = "출처 " + m[1] + " 보기";
      cite.onclick = () => openSource(msg, m[1]);
      bubble.appendChild(cite);
    } else {
      bubble.appendChild(document.createTextNode(part));
    }
  }
  if (sources.length) {
    const meta = document.createElement("div");
    meta.className = "meta";
    meta.textContent = data.seconds.toFixed(1) + "초 · 출처 " + sources.length + "개";
    msg.appendChild(meta);
  }
  if (sources.length) {
    const list = document.createElement("div");
    list.className = "sources";
    for (const s of sources) {
      const details = document.createElement("details");
      details.dataset.n = s.n;
      const summary = document.createElement("summary");
      summary.textContent = "[" + s.n + "] " + s.title;
      const text = document.createElement("pre");
      text.textContent = s.text;
      details.append(summary, text);
      list.appendChild(details);
    }
    msg.appendChild(list);
  }
  chat.scrollTop = chat.scrollHeight;
}

// [n]을 누르면 그 출처를 펼치고 잠깐 테두리를 칠한다
function openSource(msg, n) {
  const details = msg.querySelector('.sources details[data-n="' + n + '"]');
  if (!details) return;
  details.open = true;
  details.classList.add("flash");
  setTimeout(() => details.classList.remove("flash"), 1200);
  details.scrollIntoView({block: "nearest", behavior: "smooth"});
}

// 답을 기다리는 동안 : 점 세 개
function addTyping() {
  const msg = document.createElement("div");
  msg.className = "msg bot typing";
  msg.innerHTML = '<div class="bubble"><span></span><span></span><span></span></div>';
  chat.appendChild(msg);
  chat.scrollTop = chat.scrollHeight;
  return msg;
}

// 질문 하나 : 내 말풍선 → 점 세 개 → 서버에 묻기 → 봇 말풍선
async function ask(question) {
  question = question.trim();
  if (!question || send.disabled) return;
  document.getElementById("examples")?.remove();       // 첫 질문 뒤에는 예시 버튼을 치운다
  addMessage("user", question);
  input.value = "";
  resize();
  send.disabled = true;
  const typing = addTyping();
  try {
    addAnswer(await askServer(question));
  } catch (err) {
    addMessage("bot error", "서버에 연결하지 못했어요 (" + err.message + "). 서버 터미널이 켜져 있는지 확인하세요.");
  } finally {
    typing.remove();
    send.disabled = false;
    input.focus();
  }
}

// 입력창 : Enter = 보내기, Shift+Enter = 줄바꿈, 글이 길어지면 칸이 늘어난다
function resize() {
  input.style.height = "auto";
  input.style.height = input.scrollHeight + "px";
}
form.addEventListener("submit", e => { e.preventDefault(); ask(input.value); });
input.addEventListener("keydown", e => {
  // 한글을 조합하는 중의 Enter는 글자를 끝내는 Enter라서 보내지 않는다
  if (e.key === "Enter" && !e.shiftKey && !e.isComposing && e.keyCode !== 229) {
    e.preventDefault();
    ask(input.value);
  }
});
input.addEventListener("input", resize);
document.querySelectorAll("#examples button").forEach(b => b.addEventListener("click", () => ask(b.textContent)));

// 머리글 : 서버 상태 (검색 방식 · 청크 수 · 모델)
fetch("/api/info").then(r => r.json()).then(info => {
  document.getElementById("status").textContent =
      "청크 " + info.chunks + "개 · " + info.model;
}).catch(() => {
  document.getElementById("status").textContent = "서버에 연결하지 못했어요";
});

// 주소 뒤에 ?q=질문 을 붙이면 열자마자 그 질문을 보낸다 (예 : http://localhost:8001/?q=러닝메이트가 뭐야)
const first = new URLSearchParams(location.search).get("q");
if (first) ask(first);
