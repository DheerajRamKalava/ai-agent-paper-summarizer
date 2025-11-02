"""
Summarization model wrapper
Uses Phi-2 base model for generating summaries
"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import warnings
warnings.filterwarnings('ignore')

class SummarizerModel:
    """Wrapper for the Phi-2 model used for summarization"""
    
    def __init__(self):
        """Initialize the model and tokenizer"""
        print("Loading Phi-2 model...")
        
        model_name = "microsoft/phi-2"
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name, 
            trust_remote_code=True
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Detect device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        device_map = "auto" if torch.cuda.is_available() else "cpu"
        
        print(f"Using device: {self.device}")
        
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map=device_map,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        self.model.eval()
        
        print("Model loaded successfully!")
    
    def summarize(self, text: str, max_new_tokens: int = 250) -> str:
        """
        Generate a summary for the given text
        
        Args:
            text: Input text to summarize
            max_new_tokens: Maximum tokens to generate
            
        Returns:
            Generated summary as string
        """
        # Create structured prompt
        prompt = f"""You are an academic paper summarizer. Provide a concise, single-paragraph summary of the following abstract.

Abstract:
{text[:2000]}

Summary:"""
        
        # Tokenize input
        inputs = self.tokenizer(
            prompt, 
            return_tensors="pt", 
            truncation=True, 
            max_length=1024
        )
        
        # Move to device if using GPU
        if self.device == "cuda":
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Generate summary
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode output
        full_output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the summary part
        if "Summary:" in full_output:
            summary = full_output.split("Summary:", 1)[-1].strip()
        else:
            # Fallback: remove the prompt
            summary = full_output.replace(prompt, "").strip()
        
        # Remove common hallucinations (EXPANDED LIST)
        stop_phrases = [
            "Question:", "Questions:", "[QUESTION", "[Q:", "Q:",
            "References:", "Reference:", "Bibliography:",
            "\n\n##", "##", 
            "Introduction:", "Conclusion:",
            "Note:", "Notes:",
            "Acknowledgment", "Acknowledgement",
            "Appendix", "Figure", "Table"
        ]
        
        for phrase in stop_phrases:
            if phrase in summary:
                summary = summary.split(phrase)[0].strip()
        
        # Remove any remaining newlines and extra spaces
        summary = " ".join(summary.split())
        
        # Limit length
        return summary[:800] if len(summary) > 800 else summary

if __name__ == "__main__":
    model = SummarizerModel()
    test_text = "This paper presents a novel approach to machine learning..."
    print("Generating test summary...")
    summary = model.summarize(test_text)
    print(f"Summary: {summary}")

print("File updated: src/model_simple.py (with expanded hallucination filtering)")
