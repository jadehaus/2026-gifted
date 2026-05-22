const messagesEl = document.querySelector("#messages");
const form = document.querySelector("#chat-form");
const input = document.querySelector("#user-input");
const sendButton = document.querySelector("#send-button");
const resetButton = document.querySelector("#reset-button");
const apiStatus = document.querySelector("#api-status");
const quickActionsEl = document.querySelector("#quick-actions");

let messages = [];
let busy = false;

const CHAR_NAMES = { sia: "시아", harin: "하린", mook: "묵" };

// 교육용: 각 tool이 무슨 행동인지 사람이 읽을 수 있게 라벨/아이콘을 붙인다.
const TOOL_INFO = {
  inspect_area: { icon: "🔍", label: "주변을 살핀다" },
  examine: { icon: "🕯️", label: "자세히 살펴본다" },
  move: { icon: "🚶", label: "이동한다" },
  take_item: { icon: "🎒", label: "아이템을 줍는다" },
  use_item: { icon: "✨", label: "아이템을 사용한다" },
  present_enemy_choice: { icon: "⚠️", label: "적 출현 선택지를 띄운다" },
  talk_to: { icon: "💬", label: "대화한다" },
  say: { icon: "🗣️", label: "캐릭터가 말한다" },
  change_affection: { icon: "💗", label: "마음이 움직인다" },
  solve_puzzle: { icon: "🧩", label: "퍼즐에 도전한다" },
  battle_action: { icon: "⚔️", label: "전투 행동을 한다" },
  add_journal: { icon: "📜", label: "기록을 남긴다" },
  reset_game: { icon: "🔄", label: "새 게임을 연다" },
};

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderInlineMarkdown(text) {
  return escapeHtml(text)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/_([^_]+)_/g, "<em>$1</em>");
}

function renderMarkdown(text) {
  const lines = String(text || "").split(/\r?\n/);
  const blocks = [];
  let paragraph = [];
  let list = [];

  function flushParagraph() {
    if (paragraph.length) {
      blocks.push(`<p>${renderInlineMarkdown(paragraph.join(" "))}</p>`);
      paragraph = [];
    }
  }

  function flushList() {
    if (list.length) {
      blocks.push(`<ul>${list.map((item) => `<li>${renderInlineMarkdown(item)}</li>`).join("")}</ul>`);
      list = [];
    }
  }

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) {
      flushParagraph();
      flushList();
      continue;
    }

    if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
      flushParagraph();
      list.push(trimmed.slice(2).trim());
      continue;
    }

    if (trimmed.startsWith("> ")) {
      flushParagraph();
      flushList();
      blocks.push(`<blockquote>${renderInlineMarkdown(trimmed.slice(2).trim())}</blockquote>`);
      continue;
    }

    const heading = trimmed.match(/^(#{1,3})\s+(.+)$/);
    if (heading) {
      flushParagraph();
      flushList();
      const level = heading[1].length + 2;
      blocks.push(`<h${level}>${renderInlineMarkdown(heading[2])}</h${level}>`);
      continue;
    }

    paragraph.push(trimmed);
  }

  flushParagraph();
  flushList();
  return blocks.join("");
}

function scrollMessages() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function addMessage(role, text) {
  const bubble = document.createElement("article");
  bubble.className = `bubble ${role}`;
  if (role.includes("assistant") && !role.includes("loading")) {
    bubble.innerHTML = renderMarkdown(text);
  } else {
    bubble.textContent = text;
  }
  messagesEl.appendChild(bubble);
  scrollMessages();
  return bubble;
}

// 캐릭터가 실제로 말한 것처럼 보이도록 캐릭터 전용 말풍선을 그린다.
function addCharacterMessage(character, line, emotion = "") {
  const wrap = document.createElement("article");
  wrap.className = "bubble character";
  const accent = character.accent || "#d8f3ff";
  wrap.style.setProperty("--char-accent", accent);
  const emotionTag = emotion
    ? `<span class="char-emotion">${escapeHtml(emotion)}</span>`
    : "";
  wrap.innerHTML = `
    <div class="char-avatar" style="--char-accent:${accent}">${escapeHtml(character.emoji || "🗣️")}</div>
    <div class="char-body">
      <div class="char-head">
        <span class="char-name">${escapeHtml(character.name)}</span>
        <span class="char-role">${escapeHtml(character.role || "")}</span>
        ${emotionTag}
      </div>
      <p class="char-line">${renderInlineMarkdown(line)}</p>
    </div>`;
  messagesEl.appendChild(wrap);
  scrollMessages();
}

// 교육용: 이번 턴에 게임 마스터가 어떤 tool을 호출했는지 채팅에 표시한다.
function addToolNotice(calls) {
  if (!calls || calls.length === 0) return;
  const note = document.createElement("div");
  note.className = "tool-notice";
  const pills = calls
    .map((call) => {
      const info = TOOL_INFO[call.name] || { icon: "🛠️", label: call.name };
      const arg = Object.values(call.arguments || {})[0];
      const detail = arg ? ` · ${escapeHtml(String(arg))}` : "";
      return `<span class="tool-pill"><span class="ti">${info.icon}</span><code>${escapeHtml(call.name)}</code><span class="tl">${info.label}${detail}</span></span>`;
    })
    .join("");
  note.innerHTML = `<span class="tool-notice-head">🧭 기록관이 도구를 사용했어요</span><div class="tool-notice-pills">${pills}</div>`;
  messagesEl.appendChild(note);
  scrollMessages();
}

function renderEnemyChoices(calls) {
  (calls || []).forEach((call) => {
    if (call.name !== "present_enemy_choice") return;
    const event = call.result?.ui_event;
    if (!event || event.type !== "enemy_choice") return;

    const enemy = event.enemy || {};
    const panel = document.createElement("article");
    panel.className = "enemy-encounter";
    panel.innerHTML = `
      <div class="enemy-flare" aria-hidden="true"></div>
      <div class="enemy-copy">
        <p>${escapeHtml(event.title || "적이 나타났다")}</p>
        <h3>${escapeHtml(enemy.name || "알 수 없는 적")}</h3>
        <div class="enemy-meta">
          <span>HP ${escapeHtml(enemy.hp ?? "-")}</span>
          <span>행동 선택 필요</span>
        </div>
      </div>
      <div class="enemy-actions"></div>`;

    const actions = panel.querySelector(".enemy-actions");
    (event.choices || []).forEach((choice) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = choice.label?.includes("도망") ? "enemy-action secondary" : "enemy-action";
      button.textContent = choice.label || choice.text || "행동";
      button.addEventListener("click", () => {
        if (busy) return;
        sendText(choice.text || choice.label);
      });
      actions.appendChild(button);
    });

    messagesEl.appendChild(panel);
    scrollMessages();
  });
}

function chip(text, tone = "") {
  const el = document.createElement("span");
  el.className = `chip ${tone}`;
  el.textContent = text;
  return el;
}

function renderChips(selector, values, emptyText) {
  const target = document.querySelector(selector);
  target.innerHTML = "";
  if (!values || values.length === 0) {
    target.appendChild(chip(emptyText, "muted"));
    return;
  }
  values.forEach((value) => target.appendChild(chip(value)));
}

function renderPresent(characters) {
  const el = document.querySelector("#present");
  el.innerHTML = "";
  const entries = Object.values(characters || {});
  if (entries.length === 0) {
    el.appendChild(chip("아무도 없다", "muted"));
    return;
  }
  entries.forEach((c) => {
    const card = document.createElement("div");
    card.className = "present-card";
    card.style.setProperty("--char-accent", c.accent || "#d8f3ff");
    card.innerHTML = `
      <span class="present-emoji">${escapeHtml(c.emoji || "🗣️")}</span>
      <span class="present-name">${escapeHtml(c.name)}</span>
      <span class="present-role">${escapeHtml(c.role || "")}</span>`;
    el.appendChild(card);
  });
}

function renderQuickActions(area) {
  quickActionsEl.innerHTML = "";
}

function renderState(area) {
  const state = area.state || {};
  const player = state.player || {};
  const room = area.room || {};

  const hp = player.hp ?? 0;
  const maxHp = player.max_hp ?? 1;
  document.querySelector("#hp").textContent = `${player.hp ?? "-"} / ${player.max_hp ?? "-"}`;
  const fill = document.querySelector("#hp-fill");
  const ratio = Math.max(0, Math.min(1, hp / maxHp));
  fill.style.width = `${ratio * 100}%`;
  fill.classList.toggle("low", ratio <= 0.3);
  document.querySelector("#level").textContent = player.level ?? "-";
  document.querySelector("#xp").textContent = player.xp ?? "-";
  document.querySelector("#turn").textContent = state.turn ?? "-";
  document.querySelector("#objective").textContent = state.objective || "-";
  document.querySelector("#room-name").textContent = room.name || "-";
  document.querySelector("#room-desc").textContent = room.description || "-";

  const exitLabels = Object.entries(room.exits || {}).map(([dir, id]) => `${dir} → ${id}`);
  renderChips("#exits", exitLabels, "출구 없음");
  renderChips("#inventory", state.inventory || [], "비어 있음");
  renderPresent(area.characters);
  renderQuickActions(area);

  const affectionEl = document.querySelector("#affection");
  affectionEl.innerHTML = "";
  Object.entries(state.affection || {}).forEach(([id, value]) => {
    const row = document.createElement("div");
    row.className = "affection-row";
    row.innerHTML = `<span>${CHAR_NAMES[id] || id}</span><meter min="-3" max="5" low="0" high="3" optimum="5" value="${value}"></meter><strong>${value}</strong>`;
    affectionEl.appendChild(row);
  });

  const journal = document.querySelector("#journal");
  journal.innerHTML = "";
  (state.journal || []).slice().reverse().forEach((entry) => {
    const li = document.createElement("li");
    li.textContent = entry;
    journal.appendChild(li);
  });

  const battle = document.querySelector("#battle");
  if (state.battle) {
    const enemyName = state.battle.enemy_name || state.battle.enemy_id;
    battle.innerHTML = `
      <strong>⚔️ ${escapeHtml(enemyName)}</strong>
      <span>HP ${escapeHtml(state.battle.enemy_hp ?? "-")}</span>
      <span class="battle-choice">선택 대기</span>`;
    battle.classList.add("active");
  } else {
    battle.textContent = "주변에 적 없음";
    battle.classList.remove("active");
  }
}

function renderCharacterHistory(data) {
  const box = document.querySelector("#character-history");
  box.innerHTML = "";
  Object.values(data || {}).forEach((entry) => {
    const character = entry.character || {};
    const messages = entry.messages || [];
    const details = document.createElement("details");
    details.className = "history-card";
    details.style.setProperty("--char-accent", character.accent || "#d8f3ff");
    details.open = messages.length > 0;

    const rows = messages.length
      ? messages
          .map((message) => {
            const isCharacter = message.role === "character";
            const speaker = isCharacter ? character.name : "방문자";
            return `
              <li class="${isCharacter ? "character-line" : "player-line"}">
                <strong>${escapeHtml(speaker)}</strong>
                <span>${escapeHtml(message.content || "")}</span>
              </li>`;
          })
          .join("")
      : `<li class="empty-line">아직 대화 기록이 없습니다.</li>`;

    details.innerHTML = `
      <summary>
        <span>${escapeHtml(character.emoji || "💬")}</span>
        <strong>${escapeHtml(character.name || "-")}</strong>
        <small>${messages.length}개</small>
      </summary>
      <ol class="conversation-list">${rows}</ol>`;
    box.appendChild(details);
  });
}

function renderToolCalls(calls) {
  const box = document.querySelector("#tool-calls");
  box.innerHTML = "";
  if (!calls || calls.length === 0) {
    const empty = document.createElement("div");
    empty.className = "empty";
    empty.textContent = "아직 이번 턴 tool 호출이 없습니다.";
    box.appendChild(empty);
    return;
  }
  calls.forEach((call) => {
    const info = TOOL_INFO[call.name] || { icon: "🛠️", label: call.name };
    const item = document.createElement("article");
    item.className = "tool-call";
    item.innerHTML = `<strong>${info.icon} ${call.name}</strong><span class="tool-call-label">${info.label}</span><pre>${escapeHtml(JSON.stringify(call.arguments, null, 2))}</pre>`;
    box.appendChild(item);
  });
}

// 도구 결과를 보고, 대화에 해당하는 캐릭터 말풍선을 채팅에 그린다.
// 캐릭터 대사는 talk_to / say 결과의 line으로 전달되므로, 그것을 캐릭터 말풍선으로 띄운다.
function renderCharacterTurns(calls) {
  (calls || []).forEach((call) => {
    const result = call.result || {};
    const speaks = call.name === "talk_to" || call.name === "say";
    if (speaks && result.ok && result.character && result.line) {
      addCharacterMessage(result.character, result.line, result.emotion);
    }
    if (call.name === "talk_to" && result.ok && result.character && result.reward) {
      addToolResultNote(`${result.character.name}이(가) '${result.reward}'을(를) 건넸다.`);
    }
  });
}

function addToolResultNote(text) {
  const note = document.createElement("div");
  note.className = "system-note";
  note.textContent = `🎁 ${text}`;
  messagesEl.appendChild(note);
  scrollMessages();
}

async function loadState() {
  const [stateResponse, historyResponse] = await Promise.all([
    fetch("/api/state"),
    fetch("/api/characters/history"),
  ]);
  const area = await stateResponse.json();
  renderState(area);
  if (historyResponse.ok) {
    renderCharacterHistory(await historyResponse.json());
  }
}

async function loadTools() {
  const response = await fetch("/api/tools");
  const data = await response.json();
  document.querySelector("#tool-schema").textContent = data.pretty;
}

async function loadHealth() {
  const response = await fetch("/api/health");
  const data = await response.json();
  apiStatus.textContent = data.has_api_key ? "● OpenAI 연결됨" : "● API 키 필요";
  apiStatus.classList.toggle("warn", !data.has_api_key);
}

async function sendText(text) {
  if (busy) return;
  const trimmed = String(text || "").trim();
  if (!trimmed) return;

  busy = true;
  input.value = "";
  addMessage("user", trimmed);
  messages.push({ role: "user", content: trimmed });
  sendButton.disabled = true;
  const loading = addMessage("assistant loading", "봉인된 색인을 펼치는 중...");

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages }),
    });
    const data = await response.json();
    loading.remove();

    const calls = data.tool_calls || [];
    addToolNotice(calls);
    renderCharacterTurns(calls);
    renderEnemyChoices(calls);

    const answer = String(data.answer || data.error || "").trim();
    if (answer) {
      addMessage("assistant", answer);
      messages.push({ role: "assistant", content: answer });
    }
    renderToolCalls(calls);
    await loadState();
  } catch (error) {
    loading.remove();
    addMessage("assistant", `오류가 발생했어요: ${error}`);
  } finally {
    busy = false;
    sendButton.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  sendText(input.value);
});

resetButton.addEventListener("click", async () => {
  await fetch("/api/reset", { method: "POST" });
  messages = [];
  messagesEl.innerHTML = "";
  renderToolCalls([]);
  await loadState();
  addMessage(
    "assistant",
    "**새 기록 개방**\n\n비 오는 밤, 당신은 _은빛 로비_에 서 있습니다. 멈춘 별자리 시계 아래에서 젖은 책 냄새가 올라옵니다."
  );
});

Promise.all([loadHealth(), loadTools(), loadState()]).then(() => {
  renderToolCalls([]);
  addMessage(
    "assistant",
    "**달빛 기록관 입장**\n\n비 오는 밤, 사라진 동생의 이름이 적힌 초대장이 당신을 이곳으로 이끌었습니다. 채팅에 행동을 입력하면 기록관은 그 행동의 결과만 돌려줍니다."
  );
  input.focus();
});
