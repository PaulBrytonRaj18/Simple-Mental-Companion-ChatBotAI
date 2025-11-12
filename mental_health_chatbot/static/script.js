const chatEl = document.getElementById('chat');
const formEl = document.getElementById('chat-form');
const inputEl = document.getElementById('message');

function appendMessage(role, text, isTyping = false) {
  const message = document.createElement('div');
  message.className = `message ${role}`;

  const bubble = document.createElement('div');
  bubble.className = 'bubble';

  const sender = document.createElement('div');
  sender.className = 'sender';
  sender.textContent = role === 'user' ? 'You' : 'Mira';

  bubble.appendChild(sender);

  if (isTyping) {
    const typing = document.createElement('div');
    typing.className = 'typing';
    typing.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
    bubble.appendChild(typing);
  } else {
    const textNode = document.createElement('div');
    textNode.textContent = text;
    bubble.appendChild(textNode);
  }

  message.appendChild(bubble);
  chatEl.appendChild(message);
  chatEl.scrollTop = chatEl.scrollHeight;

  return message; // so we can replace typing indicator later
}

async function sendMessage(message) {
  // append user message
  appendMessage('user', message);

  // append assistant typing indicator
  const typingNode = appendMessage('assistant', '', true);

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    const data = await res.json();
    const reply = data.reply || "I'm here with you. Tell me more about how you're feeling.";

    // replace typing node content
    typingNode.querySelector('.bubble').innerHTML = '';
    const sender = document.createElement('div');
    sender.className = 'sender';
    sender.textContent = 'Mira';
    const textNode = document.createElement('div');
    textNode.textContent = reply;
    typingNode.querySelector('.bubble').appendChild(sender);
    typingNode.querySelector('.bubble').appendChild(textNode);

    chatEl.scrollTop = chatEl.scrollHeight;
  } catch (err) {
    typingNode.querySelector('.bubble').innerHTML = '';
    const sender = document.createElement('div');
    sender.className = 'sender';
    sender.textContent = 'Mira';
    const textNode = document.createElement('div');
    textNode.textContent = 'I had trouble responding just now. Could we try again?';
    typingNode.querySelector('.bubble').appendChild(sender);
    typingNode.querySelector('.bubble').appendChild(textNode);
  }
}

formEl.addEventListener('submit', (e) => {
  e.preventDefault();
  const text = (inputEl.value || '').trim();
  if (!text) return;
  inputEl.value = '';
  sendMessage(text);
});

inputEl.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    formEl.dispatchEvent(new Event('submit'));
  }
});

// Welcome message on load
window.addEventListener('load', () => {
  appendMessage('assistant', "Hello! I'm Mira, your mental health companion. How are you feeling today?");
});

const themeToggleBtn = document.getElementById('theme-toggle');
themeToggleBtn.addEventListener('click', () => {
  document.body.classList.toggle('dark-theme');
});

const theme = localStorage.getItem('theme');
if (theme === 'dark') {
  document.body.classList.add('dark-theme');
}

document.body.addEventListener('classchange', () => {
  if (document.body.classList.contains('dark-theme')) {
    localStorage.setItem('theme', 'dark');
  } else {
    localStorage.setItem('theme', 'light');
  }
});
const observer = new MutationObserver(() => {
  document.body.dispatchEvent(new Event('classchange'));
});
observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });  
