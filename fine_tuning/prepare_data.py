"""
Data preparation for fine-tuning
Downloads and processes academic papers for training
"""
from datasets import load_dataset
import json
import os

def prepare_training_data():
    """Prepare dataset for fine-tuning"""
    print("="*60)
    print("DATA PREPARATION FOR FINE-TUNING")
    print("="*60)
    
    print("\n1. Loading dataset...")
    
    try:
        # Try primary dataset
        dataset = load_dataset("ccdv/arxiv-summarization", split="train")
        print(f"Loaded arxiv-summarization: {len(dataset)} papers")
    except Exception as e:
        print(f"⚠ Primary dataset failed: {e}")
        print("Trying alternative dataset...")
        try:
            dataset = load_dataset("EdinburghNLP/xsum", split="train[:1000]")
            print(f"Loaded xsum dataset: {len(dataset)} samples")
        except Exception as e2:
            print(f"All datasets failed: {e2}")
            return None, None
    
    print("\n2. Processing papers...")
    training_data = []
    
    for i, item in enumerate(dataset):
        if i >= 1000:  # Limit for reasonable training time
            break
        
        try:
            # Handle different dataset formats
            if 'article' in item and 'abstract' in item:
                article = item['article'][:3000]  # Truncate to fit context
                abstract = item['abstract']
            elif 'document' in item and 'summary' in item:
                article = item['document'][:3000]
                abstract = item['summary']
            else:
                continue
            
            # Format as training example
            training_example = {
                "text": f"""Summarize this academic paper concisely.

Paper:
{article}

Summary:
{abstract}"""
            }
            
            training_data.append(training_example)
            
            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1} papers...")
        
        except Exception as e:
            continue
    
    print(f"\n3. Splitting dataset...")
    # 90-10 train-validation split
    split_idx = int(0.9 * len(training_data))
    train_data = training_data[:split_idx]
    val_data = training_data[split_idx:]
    
    print(f"  Training: {len(train_data)} samples")
    print(f"  Validation: {len(val_data)} samples")
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # Save as JSONL
    print("\n4. Saving files...")
    with open('data/train.jsonl', 'w', encoding='utf-8') as f:
        for item in train_data:
            f.write(json.dumps(item) + '\n')
    print(f"  Saved: data/train.jsonl")
    
    with open('data/val.jsonl', 'w', encoding='utf-8') as f:
        for item in val_data:
            f.write(json.dumps(item) + '\n')
    print(f"  Saved: data/val.jsonl")
    
    print("\n" + "="*60)
    print("DATA PREPARATION COMPLETE")
    print("="*60)
    
    return train_data, val_data

if __name__ == "__main__":
    prepare_training_data()

print("File created: fine_tuning/prepare_data.py")
