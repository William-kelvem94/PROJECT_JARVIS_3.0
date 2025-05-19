let stream = null;
let mediaRecorder = null;
let chunks = [];

async function sendMessage() {
    const input = document.getElementById('user-input').value;
    if (!input) return;

    const chatBox = document.getElementById('chat-box');
    chatBox.innerHTML += `<p><strong>Você:</strong> ${input}</p>`;
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await fetch('/text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: input })
        });
        const data = await response.json();
        if (data.response) {
            chatBox.innerHTML += `<p><strong>Jarvis:</strong> ${data.response}</p>`;
        } else if (data.error) {
            chatBox.innerHTML += `<p><strong>Erro:</strong> ${data.error}</p>`;
        } else {
            chatBox.innerHTML += `<p><strong>Erro:</strong> Resposta inesperada do servidor.</p>`;
        }
        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (error) {
        chatBox.innerHTML += `<p><strong>Erro:</strong> ${error.message}</p>`;
    }

    document.getElementById('user-input').value = '';
}

async function toggleRecording() {
    const micButton = document.getElementById('mic-button');
    if (!stream) {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
            mediaRecorder.onstop = sendAudio;
            mediaRecorder.start();
            micButton.classList.add('recording');
        } catch (error) {
            alert('Erro ao acessar o microfone: ' + error.message);
        }
    } else {
        mediaRecorder.stop();
        stream.getTracks().forEach(track => track.stop());
        stream = null;
        micButton.classList.remove('recording');
    }
}

async function sendAudio() {
    const blob = new Blob(chunks, { type: 'audio/wav' });
    chunks = [];
    const chatBox = document.getElementById('chat-box');
    try {
        const response = await fetch('/audio', {
            method: 'POST',
            body: blob
        });
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        chatBox.innerHTML += `<p><strong>Jarvis:</strong> <audio controls src="${audioUrl}"></audio></p>`;
        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (error) {
        chatBox.innerHTML += `<p><strong>Erro:</strong> ${error.message}</p>`;
    }
}

async function trainModel() {
    // Agora o usuário deve digitar: treinar modelo <nome> com dataset <dados> no campo principal
    const input = document.getElementById('user-input').value;
    const statusDiv = document.getElementById('train-status');
    if (!input || !input.toLowerCase().includes('treinar')) {
        statusDiv.innerText = 'Digite o comando de treinamento no campo principal, exemplo: treinar modelo gpt2 com dataset <dados>';
        return;
    }
    const chatBox = document.getElementById('chat-box');
    chatBox.innerHTML += `<p><strong>Você:</strong> ${input}</p>`;
    chatBox.scrollTop = chatBox.scrollHeight;
    statusDiv.innerText = 'Treinamento iniciado. Aguarde resposta do Jarvis...';
    try {
        const response = await fetch('/text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: input })
        });
        const data = await response.json();
        if (data.response) {
            chatBox.innerHTML += `<p><strong>Jarvis:</strong> ${data.response}</p>`;
            statusDiv.innerText = 'Treinamento finalizado. Veja resposta acima.';
        } else if (data.error) {
            chatBox.innerHTML += `<p><strong>Erro:</strong> ${data.error}</p>`;
            statusDiv.innerText = data.error;
        } else {
            chatBox.innerHTML += `<p><strong>Erro:</strong> Resposta inesperada do servidor.</p>`;
            statusDiv.innerText = 'Resposta inesperada do servidor.';
        }
        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (error) {
        chatBox.innerHTML += `<p><strong>Erro:</strong> ${error.message}</p>`;
        statusDiv.innerText = 'Erro: ' + error.message;
    }
    document.getElementById('user-input').value = '';
}

async function runTests() {
    const outputBox = document.getElementById('test-output');
    outputBox.value = 'Executando testes... Aguarde.';
    try {
        const response = await fetch('/run_tests', { method: 'POST' });
        const data = await response.json();
        outputBox.value = data.output;
    } catch (error) {
        outputBox.value = 'Erro ao rodar testes: ' + error.message;
    }
}

// Tabs e navegação One UI
function showTab(tab) {
  ["chat","plugins","treino","testes"].forEach(t => {
    document.getElementById(`tab-content-${t}`).style.display = (t===tab)?'block':'none';
    document.getElementById(`tab-${t}`).classList.toggle('active', t===tab);
  });
}
function openConfigModal() {
  document.getElementById('config-modal').style.display = 'block';
}
function closeConfigModal() {
  document.getElementById('config-modal').style.display = 'none';
}
function toggleDarkMode() {
  document.body.classList.toggle('dark');
  document.getElementById('darkmode-toggle').checked = document.body.classList.contains('dark');
}

// Inicialização: mantém dark mode se já estava ativo
window.addEventListener('DOMContentLoaded', () => {
  if (localStorage.getItem('darkmode') === 'true') {
    document.body.classList.add('dark');
    document.getElementById('darkmode-toggle').checked = true;
  }
  document.getElementById('darkmode-toggle').addEventListener('change', (e) => {
    document.body.classList.toggle('dark', e.target.checked);
    localStorage.setItem('darkmode', e.target.checked);
  });
});

document.getElementById('theme-toggle').addEventListener('click', () => {
    document.body.classList.toggle('dark');
});

// Toast notification system
function showToast(message, type = 'info', duration = 3000) {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.classList.add('visible'), 10);
  setTimeout(() => {
    toast.classList.remove('visible');
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// Carregamento dinâmico de plugins
async function loadPlugins() {
  const response = await fetch('/api/plugins');
  const plugins = await response.json();
  const grid = document.querySelector('.plugin-grid');
  if (!grid) return;
  grid.innerHTML = '';
  plugins.forEach(plugin => {
    const card = `
      <div class="plugin-card" data-plugin="${plugin.name}">
        <div class="plugin-icon">
          ${plugin.icon ? `<img src='data:image/svg+xml;base64,${plugin.icon}' alt='${plugin.name}'>` : '<svg width="24" height="24"><circle cx="12" cy="12" r="10" fill="#7E57C2"/></svg>'}
        </div>
        <h3 class="text-body">${plugin.name}</h3>
        <div class="plugin-actions">
          ${(plugin.actions||[]).map(a => `<button class="pill-button">${a}</button>`).join('')}
        </div>
        <span class="plugin-status ${plugin.status}">${plugin.status}</span>
      </div>
    `;
    grid.insertAdjacentHTML('beforeend', card);
  });
}

// Chama loadPlugins ao abrir a aba de plugins
window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('tab-plugins')?.addEventListener('click', loadPlugins);
});

// Audio visualizer (opcional, não quebra SVG atual)
class AudioVisualizer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.analyser = null;
    this.dataArray = null;
    this.animationId = null;
  }
  start(stream) {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    this.analyser = audioCtx.createAnalyser();
    const source = audioCtx.createMediaStreamSource(stream);
    source.connect(this.analyser);
    this.analyser.fftSize = 256;
    const bufferLength = this.analyser.frequencyBinCount;
    this.dataArray = new Uint8Array(bufferLength);
    this.draw();
  }
  draw() {
    if (!this.analyser) return;
    this.animationId = requestAnimationFrame(() => this.draw());
    this.analyser.getByteFrequencyData(this.dataArray);
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this.ctx.fillStyle = '#7E57C2';
    const barWidth = (this.canvas.width / this.dataArray.length) * 2.5;
    let x = 0;
    for (let i = 0; i < this.dataArray.length; i++) {
      const barHeight = this.dataArray[i] / 2;
      this.ctx.fillRect(x, this.canvas.height - barHeight, barWidth, barHeight);
      x += barWidth + 1;
    }
  }
}

// ChatHistory (IndexedDB, não interfere no chat atual)
class ChatHistory {
  constructor() {
    this.db = null;
    this.initDB();
  }
  initDB() {
    const request = indexedDB.open('JarvisChatHistory', 1);
    request.onupgradeneeded = (e) => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains('chats')) {
        db.createObjectStore('chats', { keyPath: 'id', autoIncrement: true });
      }
    };
    request.onsuccess = (e) => {
      this.db = e.target.result;
      // this.loadHistory(); // opcional
    };
  }
  addMessage(message) {
    if (!this.db) return;
    const tx = this.db.transaction('chats', 'readwrite');
    tx.objectStore('chats').add({ timestamp: Date.now(), ...message });
  }
}
