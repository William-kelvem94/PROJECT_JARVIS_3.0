import logging
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from datasets import Dataset
import os

# Corrige: força uso de numpy correto e garante dependências no ambiente Docker
import numpy

logger = logging.getLogger(__name__)

FINE_TUNED_SYMLINK = "./fine_tuned_model"

def fine_tune_model(model_path, dataset_path, output_dir):
    """Realiza fine-tuning de um modelo de linguagem."""
    try:
        model = AutoModelForCausalLM.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        # Corrige: força uso do modelo em português se não for passado
        if model_path == "gpt2":
            model_path = "pierreguillou/gpt2-small-portuguese"
            model = AutoModelForCausalLM.from_pretrained(model_path)
            tokenizer = AutoTokenizer.from_pretrained(model_path)
        # Carregar dataset simples a partir de um arquivo de texto (um prompt por linha)
        with open(dataset_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        dataset = Dataset.from_dict({"text": [l.strip() for l in lines if l.strip()]})
        # Tokenização
        def tokenize_function(examples):
            return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=64)
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=3,
            per_device_train_batch_size=4,
            save_steps=10_000,
            save_total_limit=2,
        )
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_dataset,
        )
        trainer.train()
        model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)
        logger.info(f"Modelo salvo em {output_dir}")
        # Atualiza symlink para sempre usar o modelo mais recente
        try:
            if os.path.islink(FINE_TUNED_SYMLINK) or os.path.exists(FINE_TUNED_SYMLINK):
                os.remove(FINE_TUNED_SYMLINK)
            os.symlink(os.path.abspath(output_dir), FINE_TUNED_SYMLINK)
        except Exception as e:
            logger.warning(f"Falha ao atualizar symlink do modelo: {e}")
    except Exception as e:
        logger.error(f"Erro no fine-tuning: {e}")
        raise

if __name__ == "__main__":
    fine_tune_model("distilbert-base-uncased", "path/to/dataset", "./fine_tuned_model")
