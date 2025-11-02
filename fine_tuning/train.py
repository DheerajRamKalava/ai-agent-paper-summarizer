"""
Fine-tuning script using LoRA
Attempts to fine-tune Phi-2 on academic summarization
"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, get_peft_model
from datasets import load_dataset
from trl import SFTTrainer
import os
import warnings
warnings.filterwarnings('ignore')

def train_model():
    """Fine-tune the model with LoRA"""
    print("="*70)
    print("FINE-TUNING WITH LoRA")
    print("="*70)
    
    # Disable W&B
    os.environ['WANDB_DISABLED'] = 'true'
    
    print("\n1. Loading base model...")
    model_name = "microsoft/phi-2"
    
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    print(f"  Tokenizer loaded")
    
    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
        )
        print(f"  Base model loaded (2.7B parameters)")
    except Exception as e:
        print(f"  Failed to load model: {e}")
        return
    
    print("\n2. Configuring LoRA...")
    lora_config = LoraConfig(
        r=8,  # Rank
        lora_alpha=16,  # Scaling
        target_modules=["q_proj", "v_proj"],  # Attention layers
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    print("\n3. Loading training data...")
    if not os.path.exists('data/train.jsonl'):
        print("  ⚠ Data not found. Running data preparation...")
        from prepare_data import prepare_training_data
        prepare_training_data()
    
    try:
        train_dataset = load_dataset('json', data_files='data/train.jsonl', split='train')
        print(f"  Loaded {len(train_dataset)} training examples")
    except Exception as e:
        print(f"  Failed to load data: {e}")
        return
    
    print("\n4. Configuring training...")
    training_args = TrainingArguments(
        output_dir="./fine_tuned_model",
        num_train_epochs=1,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        warmup_steps=10,
        logging_steps=10,
        save_steps=100,
        learning_rate=2e-4,
        fp16=True,
        optim="adamw_torch",
        report_to="none",
        save_total_limit=1,
    )
    
    trainer = SFTTrainer(
        model=model,
        train_dataset=train_dataset,
        dataset_text_field="text",
        max_seq_length=1024,
        tokenizer=tokenizer,
        args=training_args,
    )
    
    print("\n5. Starting training...")
    print("="*70)
    print("⚠ NOTE: Training on T4 GPU may fail due to memory constraints")
    print("   This is expected and documented in the report.")
    print("="*70)
    
    try:
        trainer.train()
        print("\nTraining completed successfully!")
        
        print("\n6. Saving model...")
        trainer.save_model("./fine_tuned_model")
        tokenizer.save_pretrained("./fine_tuned_model")
        print("  Model saved to: ./fine_tuned_model")
        
    except torch.cuda.OutOfMemoryError:
        print("\nCUDA Out of Memory!")
        print("   T4 GPU (16GB) is insufficient for this model size.")
        print("   This limitation is documented in docs/report.md")
        
    except Exception as e:
        print(f"\nTraining failed: {e}")
        print("   Failure documented in docs/report.md")
    
    print("\n" + "="*70)
    print("TRAINING ATTEMPT COMPLETE")
    print("="*70)

if __name__ == "__main__":
    # Prepare data first
    from prepare_data import prepare_training_data
    prepare_training_data()
    
    # Attempt training
    train_model()

print("File created: fine_tuning/train.py")
