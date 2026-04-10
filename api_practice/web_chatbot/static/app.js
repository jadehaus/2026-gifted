const state = {
  messages: [],
  waiting: false,
};

const chatMessages = document.getElementById("chatMessages");
const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const resetButton = document.getElementById("resetButton");
const promptButtons = Array.from(document.querySelectorAll(".prompt-chip"));

function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function createMessageElement(role, content) {
  const row = document.createElement("div");
  row.className = `message-row ${role}`;

  const bubble = document.createElement("div");
  bubble.className = "message-bubble";

  const meta = document.createElement("div");
  meta.className = "message-meta";
  meta.textContent = role === "user" ? "YOU" : "CHATBOT";

  const body = document.createElement("div");
  body.textContent = content;

  bubble.append(meta, body);
  row.appendChild(bubble);
  return row;
}

function renderMessages() {
  chatMessages.innerHTML = "";
  for (const message of state.messages) {
    chatMessages.appendChild(createMessageElement(message.role, message.content));
  }
  scrollToBottom();
}

function addMessage(role, content) {
  state.messages.push({ role, content });
  renderMessages();
}

function addInitialMessages() {
  state.messages = [
    {
      role: "assistant",
      content:
        "안녕하세요. 저는 실습용 챗봇이에요.\n아직 완성 전이라서, 먼저 `web_chatbot/app.py` 의 `generate_bot_reply()` 를 구현해 주세요.\n구현 전에도 대화를 보내 보면 어디를 채워야 하는지 계속 알려드릴게요.",
    },
  ];
  renderMessages();
}

function showTypingIndicator() {
  const row = document.createElement("div");
  row.className = "message-row assistant";
  row.id = "typingIndicator";

  const bubble = document.createElement("div");
  bubble.className = "message-bubble";

  const meta = document.createElement("div");
  meta.className = "message-meta";
  meta.textContent = "CHATBOT";

  const typing = document.createElement("div");
  typing.className = "typing";
  typing.innerHTML = "<span></span><span></span><span></span>";

  bubble.append(meta, typing);
  row.appendChild(bubble);
  chatMessages.appendChild(row);
  scrollToBottom();
}

function hideTypingIndicator() {
  const indicator = document.getElementById("typingIndicator");
  if (indicator) {
    indicator.remove();
  }
}

async function sendChat() {
  if (state.waiting) {
    return;
  }

  const content = userInput.value.trim();
  if (!content) {
    return;
  }

  addMessage("user", content);
  userInput.value = "";
  state.waiting = true;
  showTypingIndicator();

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ messages: state.messages }),
    });

    const data = await response.json();
    hideTypingIndicator();
    addMessage("assistant", data.reply || "응답을 받지 못했습니다.");
  } catch (error) {
    hideTypingIndicator();
    addMessage("assistant", `서버와 통신 중 오류가 발생했어요: ${error}`);
  } finally {
    state.waiting = false;
  }
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  await sendChat();
});

userInput.addEventListener("keydown", async (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    await sendChat();
  }
});

resetButton.addEventListener("click", () => {
  addInitialMessages();
  userInput.focus();
});

for (const button of promptButtons) {
  button.addEventListener("click", () => {
    userInput.value = button.dataset.prompt || "";
    userInput.focus();
  });
}

addInitialMessages();
