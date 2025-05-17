import logging
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments

logger = logging.getLogger(__name__)

def fine_tune_model(model_path, dataset_path, output_dir):
    """Realiza fine-tuning de um modelo de linguagem."""
    try:
        model = AutoModelForCausalLM.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        # Carregar dataset (exemplo)
        # dataset = load_dataset(dataset_path)
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
            train_dataset=dataset,
        )
        trainer.train()
        model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)
        logger.info(f"Modelo salvo em {output_dir}")
    except Exception as e:
        logger.error(f"Erro no fine-tuning: {e}")
        raise

if __name__ == "__main__":
    fine_tune_model("distilbert-base-uncased", "path/to/dataset", "./fine_tuned_model")
