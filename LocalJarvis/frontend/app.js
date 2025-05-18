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
        chatBox.innerHTML += `<p><strong>Jarvis:</strong> ${data.response}</p>`;
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
    const modelPath = document.getElementById('model-path').value || 'gpt2';
    const outputDir = document.getElementById('output-dir').value || './fine_tuned_model';
    const datasetInput = document.getElementById('dataset-file');
    const statusDiv = document.getElementById('train-status');
    if (!datasetInput.files.length) {
        statusDiv.innerText = 'Selecione um arquivo de dataset (.json, .txt, .csv)';
        return;
    }
    const file = datasetInput.files[0];
    const formData = new FormData();
    formData.append('dataset', file);
    formData.append('model_path', modelPath);
    formData.append('output_dir', outputDir);

    statusDiv.innerText = 'Enviando dataset e iniciando treinamento...';
    try {
        // Envia o arquivo para um endpoint temporário, depois chama /train
        // Aqui, para simplificação, espera-se que o backend aceite dataset_path como caminho já disponível
        // Em produção, seria necessário um endpoint para upload do arquivo
        const reader = new FileReader();
        reader.onload = async function(e) {
            const datasetContent = e.target.result;
            const response = await fetch('/train', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model_path: modelPath,
                    dataset_path: file.name, // O backend deve saber onde salvar
                    output_dir: outputDir,
                    dataset_content: datasetContent
                })
            });
            const data = await response.json();
            if (response.ok) {
                statusDiv.innerText = data.message;
            } else {
                statusDiv.innerText = data.error || 'Erro no treinamento';
            }
        };
        reader.readAsText(file);
    } catch (error) {
        statusDiv.innerText = 'Erro: ' + error.message;
    }
}

document.getElementById('theme-toggle').addEventListener('click', () => {
    document.body.classList.toggle('dark');
});
