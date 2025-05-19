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
