const pageText = document.querySelector("#page-text").dataset;
const messagesEl = document.querySelector("#messages");
const form = document.querySelector("#chat-form");
const input = document.querySelector("#user-input");
const sendButton = document.querySelector("#send-button");
const schemaEl = document.querySelector("#tool-schema");
const schemaBox = document.querySelector("#schema-box");
const schemaToggle = document.querySelector("#schema-toggle");
const toolCountEl = document.querySelector("#tool-count");
const callsEl = document.querySelector("#tool-calls");
const toolFileSelect = document.querySelector("#tool-file-select");
const toolFileButton = document.querySelector("#tool-file-button");
const toolRemoveButton = document.querySelector("#tool-remove-button");
const modal = document.querySelector("#confirm-modal");
const modalCancel = document.querySelector("#modal-cancel");
const modalConfirm = document.querySelector("#modal-confirm");

let messages = [];
let selectedToolFile = "";
let pendingToolFile = "";

document.title = pageText.title;
document.querySelector('[data-text="title"]').textContent = pageText.title;
document.querySelector('[data-text="subtitle"]').textContent = pageText.subtitle;
document.querySelector('[data-text="toolTitle"]').textContent = pageText.toolTitle;
document.querySelector('[data-text="callTitle"]').textContent = pageText.callTitle;
input.placeholder = pageText.inputPlaceholder;
sendButton.textContent = pageText.sendLabel;

function addMessage(role, content) {
  const bubble = document.createElement("div");
  bubble.className = `bubble ${role}`;
  bubble.textContent = content;
  messagesEl.appendChild(bubble);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function updateRemoveButton() {
  toolRemoveButton.disabled = selectedToolFile === "";
}

function resetChat() {
  messages = [];
  messagesEl.innerHTML = "";
  renderToolCalls([]);
}

function renderToolCalls(toolCalls) {
  callsEl.innerHTML = "";

  if (!toolCalls.length) {
    const empty = document.createElement("div");
    empty.className = "empty-call";
    empty.textContent = "이번에는 tool 없이 답변했어요.";
    callsEl.appendChild(empty);
    return;
  }

  for (const call of toolCalls) {
    const item = document.createElement("article");
    item.className = "call-card";
    item.innerHTML = `
      <div class="call-name">${call.name}</div>
      <pre>${JSON.stringify(call, null, 2)}</pre>
    `;
    callsEl.appendChild(item);
  }
}

async function loadTools() {
  const response = await fetch("/api/tools");
  const data = await response.json();
  selectedToolFile = data.selected || "";
  toolFileSelect.value = selectedToolFile;
  schemaEl.textContent = data.pretty;
  toolCountEl.textContent = `${data.schemas.length} tools`;
  updateRemoveButton();
}

async function loadToolFiles() {
  const response = await fetch("/api/tool-files");
  const data = await response.json();

  toolFileSelect.innerHTML = '<option value="">tool 없음</option>';
  for (const filename of data.files) {
    const option = document.createElement("option");
    option.value = filename;
    option.textContent = filename;
    toolFileSelect.appendChild(option);
  }

  selectedToolFile = data.selected || "";
  toolFileSelect.value = selectedToolFile;
  updateRemoveButton();
}

async function selectToolFile(filename) {
  const response = await fetch("/api/select-tool-file", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ filename }),
  });
  const data = await response.json();

  if (!response.ok) {
    addMessage("assistant", data.error || "tool 파일을 불러오지 못했어요.");
    toolFileSelect.value = selectedToolFile;
    return;
  }

  selectedToolFile = data.selected || "";
  toolFileSelect.value = selectedToolFile;
  schemaEl.textContent = data.pretty;
  toolCountEl.textContent = `${data.schemas.length} tools`;
  updateRemoveButton();
  resetChat();
}

function showModal(filename) {
  pendingToolFile = filename;
  modal.classList.remove("hidden");
}

function hideModal() {
  pendingToolFile = "";
  modal.classList.add("hidden");
}

schemaToggle.addEventListener("click", () => {
  const isClosed = schemaBox.classList.toggle("closed");
  schemaToggle.textContent = isClosed ? "펼치기" : "접기";
});

toolFileButton.addEventListener("click", () => {
  const filename = toolFileSelect.value;
  showModal(filename);
});

toolRemoveButton.addEventListener("click", () => {
  showModal("");
});

modalCancel.addEventListener("click", () => {
  toolFileSelect.value = selectedToolFile;
  hideModal();
});

modalConfirm.addEventListener("click", async () => {
  const filename = pendingToolFile;
  hideModal();
  await selectToolFile(filename);
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const text = input.value.trim();
  if (!text) return;

  input.value = "";
  addMessage("user", text);
  messages.push({ role: "user", content: text });

  sendButton.disabled = true;
  addMessage("assistant loading", "생각하는 중...");

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages }),
    });
    const data = await response.json();

    document.querySelector(".bubble.loading")?.remove();
    const answer = data.answer || data.error || "응답 내용을 읽지 못했어요.";
    addMessage("assistant", answer);
    messages.push({ role: "assistant", content: answer });
    renderToolCalls(data.tool_calls || []);
  } catch (error) {
    document.querySelector(".bubble.loading")?.remove();
    addMessage("assistant", `오류가 발생했어요: ${error}`);
  } finally {
    sendButton.disabled = false;
    input.focus();
  }
});

loadToolFiles().then(loadTools);
renderToolCalls([]);
input.focus();
