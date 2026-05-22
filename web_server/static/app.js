const messagesEl = document.querySelector("#messages");
const form = document.querySelector("#chat-form");
const input = document.querySelector("#user-input");
const sendButton = document.querySelector("#send-button");
const refreshButton = document.querySelector("#refresh-button");
const toolMenu = document.querySelector("#tool-menu");
const toolTrigger = document.querySelector("#tool-trigger");
const toolPopover = document.querySelector("#tool-popover");
const toolLabel = document.querySelector("#tool-label");
const toolCountEl = document.querySelector("#tool-count");
const toolSchemaEl = document.querySelector("#tool-schema");
const apiStatusEl = document.querySelector("#api-status");

let messages = [];

const escapeHtml = (value) =>
  String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

function inlineMarkdown(value) {
  return escapeHtml(value)
    .replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noreferrer">$1</a>')
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>");
}

function renderMarkdown(markdown) {
  const blocks = [];
  const parts = String(markdown || "").split(/```/);

  for (let index = 0; index < parts.length; index += 1) {
    const part = parts[index];
    if (index % 2 === 1) {
      const lines = part.replace(/^\n/, "").split("\n");
      const language = lines[0].trim().match(/^[\w#+.-]+$/) ? lines.shift().trim() : "";
      const code = lines.join("\n").replace(/\n$/, "");
      blocks.push(`
        <div class="code-block">
          <div class="code-toolbar">
            <span>${escapeHtml(language || "code")}</span>
            <button class="copy-button" type="button">Copy</button>
          </div>
          <pre><code>${escapeHtml(code)}</code></pre>
        </div>
      `);
      continue;
    }

    const lines = part.split(/\n{2,}/).map((block) => block.trim()).filter(Boolean);
    for (const block of lines) {
      if (/^#{1,3}\s/.test(block)) {
        const level = Math.min(block.match(/^#+/)[0].length, 3);
        blocks.push(`<h${level}>${inlineMarkdown(block.replace(/^#{1,3}\s/, ""))}</h${level}>`);
      } else if (/^[-*]\s/m.test(block)) {
        const items = block
          .split("\n")
          .filter((line) => /^[-*]\s/.test(line.trim()))
          .map((line) => `<li>${inlineMarkdown(line.trim().replace(/^[-*]\s/, ""))}</li>`)
          .join("");
        blocks.push(`<ul>${items}</ul>`);
      } else if (/^\d+\.\s/m.test(block)) {
        const items = block
          .split("\n")
          .filter((line) => /^\d+\.\s/.test(line.trim()))
          .map((line) => `<li>${inlineMarkdown(line.trim().replace(/^\d+\.\s/, ""))}</li>`)
          .join("");
        blocks.push(`<ol>${items}</ol>`);
      } else {
        blocks.push(`<p>${inlineMarkdown(block).replace(/\n/g, "<br>")}</p>`);
      }
    }
  }

  return blocks.join("");
}

function enhanceCodeCopies(container) {
  container.querySelectorAll(".copy-button").forEach((button) => {
    button.addEventListener("click", async () => {
      const code = button.closest(".code-block")?.querySelector("code")?.textContent || "";
      await navigator.clipboard.writeText(code);
      button.textContent = "Copied";
      setTimeout(() => {
        button.textContent = "Copy";
      }, 1200);
    });
  });
}

function scrollToBottom() {
  window.requestAnimationFrame(() => {
    window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
  });
}

function addMessage(role, content, options = {}) {
  const article = document.createElement("article");
  article.className = `message ${role}${options.loading ? " loading" : ""}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "나" : role === "tool" ? "T" : "AI";

  const body = document.createElement("div");
  body.className = "message-body markdown";
  body.innerHTML = options.rawHtml ? content : renderMarkdown(content);

  article.append(avatar, body);
  messagesEl.appendChild(article);
  enhanceCodeCopies(body);
  scrollToBottom();
  return article;
}

function addToolMessage(call) {
  const args = JSON.stringify(call.arguments || {}, null, 2);
  const result = JSON.stringify(call.result ?? null, null, 2);
  addMessage(
    "tool",
    `
      <div class="tool-call-card">
        <div class="tool-call-header">
          <span>Tool 사용</span>
          <strong>${escapeHtml(call.name || "unknown_tool")}</strong>
        </div>
        <details open>
          <summary>Arguments</summary>
          <pre>${escapeHtml(args)}</pre>
        </details>
        <details>
          <summary>Result</summary>
          <pre>${escapeHtml(result)}</pre>
        </details>
      </div>
    `,
    { rawHtml: true },
  );
}

function resetChat() {
  messages = [];
  messagesEl.innerHTML = "";
  addMessage("assistant greeting", "# 무엇을 도와드릴까요?\n\n새 대화를 시작합니다.");
  input.focus();
}

function autosizeInput() {
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 180)}px`;
}

function closeToolPopover() {
  toolPopover.classList.add("hidden");
  toolTrigger.setAttribute("aria-expanded", "false");
}

function updateToolUi(data) {
  toolLabel.textContent = data.selected || "my_tools.py";
  toolCountEl.textContent = `${(data.schemas || []).length} tools`;
  toolSchemaEl.textContent = data.pretty || "[]";
}

async function loadHealth() {
  const response = await fetch("/api/health");
  const data = await response.json();
  apiStatusEl.textContent = data.has_api_key ? "API key 준비됨" : "API key 없음";
}

async function loadToolFiles() {
  const response = await fetch("/api/tool-files");
  const data = await response.json();
  toolLabel.textContent = data.selected || "my_tools.py";
}

async function loadTools() {
  const response = await fetch("/api/tools");
  const data = await response.json();
  updateToolUi(data);
}

toolTrigger.addEventListener("click", () => {
  const willOpen = toolPopover.classList.contains("hidden");
  toolPopover.classList.toggle("hidden");
  toolTrigger.setAttribute("aria-expanded", String(willOpen));
});

document.addEventListener("click", (event) => {
  if (!toolMenu.contains(event.target)) closeToolPopover();
});

refreshButton.addEventListener("click", async () => {
  await fetch("/api/reset", { method: "POST" });
  resetChat();
});

input.addEventListener("input", autosizeInput);
input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const text = input.value.trim();
  if (!text) return;

  input.value = "";
  autosizeInput();
  addMessage("user", text);
  messages.push({ role: "user", content: text });

  sendButton.disabled = true;
  const loading = addMessage("assistant", "생각하는 중...", { loading: true });

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages }),
    });
    const data = await response.json();

    loading.remove();
    for (const call of data.tool_calls || []) addToolMessage(call);

    const answer = data.answer || data.error || "응답 내용을 읽지 못했어요.";
    addMessage("assistant", answer);
    messages.push({ role: "assistant", content: answer });
  } catch (error) {
    loading.remove();
    addMessage("assistant", `오류가 발생했어요: ${error}`);
  } finally {
    sendButton.disabled = false;
    input.focus();
  }
});

Promise.all([loadHealth(), loadToolFiles()]).then(loadTools);
autosizeInput();
input.focus();
