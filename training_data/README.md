# Sistema de Treinamento de IA Local para Jarvis

Este diretório contém todos os recursos para treinar sua própria IA local usando o Ollama.

## 📁 Estrutura:

```
training_data/
├── conversational_data.jsonl      # Dados de conversação para treinar personalidade
├── knowledge_base.txt             # Base de conhecimento específica
├── fine_tuning_examples.jsonl     # Exemplos para fine-tuning
└── personality_prompts.txt        # Prompts de personalidade do Jarvis
```

## 🚀 Como Usar:

### 1. Preparar Dados de Treinamento
```bash
# Edite os arquivos acima com:
# - Suas conversas preferidas
# - Conhecimento específico sobre você/projetos
# - Estilo de resposta que você gosta
```

### 2. Executar Treinamento
```bash
# Usar o Jupyter Notebook incluído
# Acessar: http://localhost:8888 (token: jarvis2025)
```

### 3. Criar Modelo Personalizado
```bash
# Via Ollama API ou Modelfile
docker exec -it Ollama_IA_LOCAL ollama create jarvis-personal -f /training_data/Modelfile
```

## 📋 Tipos de Treinamento Disponíveis:

1. **Fine-tuning de Personalidade** - Treinar como o Jarvis responde
2. **Knowledge Base Injection** - Adicionar conhecimento específico  
3. **Conversational Style** - Treinar estilo de conversa
4. **Task-Specific Training** - Treinar para tarefas específicas

## 🔧 Ferramentas Incluídas:

- **Jupyter Notebook** - Para experimentos e visualização
- **Ollama API** - Para criar e gerenciar modelos
- **Data Processing Scripts** - Para preparar dados
- **Model Evaluation Tools** - Para testar performance
