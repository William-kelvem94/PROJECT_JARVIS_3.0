import pytest
from language_model.local_inference import LocalInference

def test_local_inference_fallback():
    llm = LocalInference("invalid-model")
    response, action = llm.infer("abrir notepad", "")
    assert "abrir" in response.lower()
    assert action == "notepad"

def test_llama_integration(monkeypatch):
    # Simula a resposta do modelo LLaMA para testar integração
    def fake_llama_call(prompt, max_tokens):
        return [{"text": "LLaMA resposta"}]
    monkeypatch.setattr("language_model.local_inference.Llama", lambda *a, **kw: fake_llama_call)
    llm = LocalInference("llama-model")
    response, _ = llm.infer("teste LLaMA", "")
    assert "LLaMA resposta" in response
