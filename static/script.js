const form = document.getElementById("chat-form");
const input = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const clearBtn = document.getElementById("clear-btn");
const messagesEl = document.getElementById("messages");
const statusLine = document.getElementById("status-line");
const hitCounter = document.getElementById("hit-counter");
const modeToggle = document.getElementById("mode-toggle");

const history = [];
let mode = "1990";

const COPY = {
  "1990": {
    title: "CyberPal '95 — GeoCities Chat",
    toggle: "🚀 2030 Moduna Geç",
    placeholder: "Type a message and hit SEND (or Enter)...",
    assistant: "CYBERPAL '95 >",
    systemWho: "SYSOP >",
    errorWho: "SYSTEM ERROR >",
    busy: "Status: DIALING... screeeech brrr kssshhh (negotiating 56k)...",
    ready: "Status: CONNECTED — 48,000 bps. Ready.",
    errorStatus: "Status: NO CARRIER.",
    resetStatus: "Status: SESSION RESET — modem still humming.",
    emptyReply: "(no carrier)",
    errorFallback: "Connection dropped. Check your modem and GEMINI_API_KEY.",
    boot: "Welcome to CyberPal '95.\nI am an AI chatbot living in 1998.\nAsk me anything — just don't mention Y2K too loudly.",
  },
  "2030": {
    title: "NovaLink 2030 — Neural Companion",
    toggle: "💾 1990 Moduna Dön",
    placeholder: "Drop a thought into the mesh…",
    assistant: "NOVALINK 2030 >",
    systemWho: "MESH >",
    errorWho: "LINK FAULT >",
    busy: "Status: opening a quantum lane…",
    ready: "Status: overlay locked — 0.4ms mesh latency.",
    errorStatus: "Status: link dropped.",
    resetStatus: "Status: neural session cleared.",
    emptyReply: "(silence on the mesh)",
    errorFallback: "Link interrupted. Check GEMINI_API_KEY and try again.",
    boot: "NovaLink 2030 online.\nI am an AI companion living in 2030.\nAsk freely — the overlay is optional.",
  },
};

function padHits(n) {
  return String(n).padStart(7, "0");
}

if (hitCounter) {
  hitCounter.textContent = padHits(1337 + Math.floor(Math.random() * 90));
}

function addMessage(role, content) {
  const wrap = document.createElement("div");
  wrap.className = `msg ${role}`;
  const labels = COPY[mode];

  const who = document.createElement("span");
  who.className = "who";
  if (role === "user") {
    who.textContent = "YOU >";
  } else if (role === "assistant") {
    who.textContent = labels.assistant;
  } else if (role === "error") {
    who.textContent = labels.errorWho;
  } else {
    who.textContent = labels.systemWho;
  }

  const body = document.createElement("span");
  body.textContent = content;

  wrap.append(who, body);
  messagesEl.appendChild(wrap);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function setBusy(busy) {
  sendBtn.disabled = busy;
  input.disabled = busy;
  statusLine.textContent = busy ? COPY[mode].busy : COPY[mode].ready;
}

function bootBanner() {
  messagesEl.innerHTML = "";
  addMessage("system", COPY[mode].boot);
}

function applyMode(nextMode) {
  mode = nextMode;
  document.body.classList.toggle("theme-2030", mode === "2030");
  document.body.classList.toggle("theme-1990", mode === "1990");
  const labels = COPY[mode];
  document.title = labels.title;
  modeToggle.textContent = labels.toggle;
  input.placeholder = labels.placeholder;
  history.length = 0;
  bootBanner();
  statusLine.textContent = labels.ready;
}

bootBanner();

modeToggle.addEventListener("click", () => {
  applyMode(mode === "1990" ? "2030" : "1990");
  input.focus();
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) {
    return;
  }

  addMessage("user", text);
  history.push({ role: "user", content: text });
  input.value = "";
  setBusy(true);

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: history, mode }),
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = data.detail || `HTTP ${response.status}`;
      throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
    }

    const reply = data.reply || COPY[mode].emptyReply;
    history.push({ role: "assistant", content: reply });
    addMessage("assistant", reply);
    statusLine.textContent = COPY[mode].ready;
  } catch (err) {
    addMessage("error", err.message || COPY[mode].errorFallback);
    statusLine.textContent = COPY[mode].errorStatus;
    history.pop();
  } finally {
    sendBtn.disabled = false;
    input.disabled = false;
    input.focus();
  }
});

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

clearBtn.addEventListener("click", () => {
  history.length = 0;
  bootBanner();
  statusLine.textContent = COPY[mode].resetStatus;
  input.focus();
});
