"""
Main AI Agent for Paper Summarization
Implements a Planner-Executor architecture
"""
import argparse
from typing import Dict, List
import sys

# components (will work both locally and in Colab)
try:
    from extract import extract_text_from_pdf, chunk_text
    from model_simple import SummarizerModel
except ImportError:
    from src.extract import extract_text_from_pdf, chunk_text
    from src.model_simple import SummarizerModel

class PaperSummarizerAgent:
    """
    AI Agent that plans and executes paper summarization tasks
    Uses a 4-step workflow: Extract → Clean → Summarize → Format
    """
    
    def __init__(self):
        """Initialize the agent and load the model"""
        print("Initializing Paper Summarizer Agent...")
        self.model = SummarizerModel()
        self.plan = []
        print("Agent ready!\n")
    
    def create_plan(self, pdf_path: str) -> List[Dict]:
        """
        Create execution plan for summarization
        
        Args:
            pdf_path: Path to input PDF
            
        Returns:
            List of planned steps
        """
        plan = [
            {
                "step": 1, 
                "action": "extract_text", 
                "input": pdf_path,
                "description": "Extract all text from PDF"
            },
            {
                "step": 2, 
                "action": "clean_text", 
                "input": "extracted_text",
                "description": "Isolate relevant sections (abstract/introduction)"
            },
            {
                "step": 3, 
                "action": "summarize", 
                "input": "clean_text",
                "description": "Generate concise summary"
            },
            {
                "step": 4, 
                "action": "format_output", 
                "input": "summary",
                "description": "Format and finalize output"
            }
        ]
        
        print("Execution Plan:")
        for step in plan:
            print(f"  Step {step['step']}: {step['description']}")
        
        return plan
    
    def _find_abstract(self, text: str) -> str:
        """
        Intelligently extract abstract from paper text
        
        Args:
            text: Full paper text
            
        Returns:
            Cleaned abstract text
        """
        # Keywords that typically mark the start of abstract
        start_keywords = [
            "Abstract", 
            "ABSTRACT", 
            "Summary",
            "Introduction",
            "1. Introduction",
            "I. INTRODUCTION"
        ]
        
        # Keywords that typically mark the end of abstract
        end_keywords = [
            "Keywords:", 
            "Key words:",
            "1. Introduction",
            "1 Introduction",
            "I. INTRODUCTION",
            "Contents",
            "Introduction\n"
        ]
        
        extracted_text = text
        found_start = False
        
        # Find start
        for keyword in start_keywords:
            if keyword in text:
                print(f"  Found start marker: '{keyword}'")
                extracted_text = text.split(keyword, 1)[1]
                found_start = True
                break
        
        if not found_start:
            print("  No start marker found, using beginning of document")
            extracted_text = text[:3000]
        
        # Find end
        for keyword in end_keywords:
            if keyword in extracted_text:
                print(f"  Found end marker: '{keyword}'")
                extracted_text = extracted_text.split(keyword, 1)[0]
                break
        
        # Final cleanup
        cleaned = extracted_text.strip().replace("\n", " ")
        
        # Validate length
        if len(cleaned) < 50:
            print("  Extracted text too short, using fallback")
            cleaned = text[:2000].replace("\n", " ")
        
        return cleaned
    
    def execute_plan(self, plan: List[Dict]) -> Dict:
        """
        Execute the planned steps
        
        Args:
            plan: List of steps to execute
            
        Returns:
            Results dictionary
        """
        results = {}
        
        for step in plan:
            print(f"\n Step {step['step']}: {step['action']}")
            
            try:
                if step['action'] == 'extract_text':
                    results['extracted'] = extract_text_from_pdf(step['input'])
                    
                    if not results['extracted']['success']:
                        print(f"  Extraction failed: {results['extracted']['error']}")
                        return results
                    
                    text_len = len(results['extracted']['text'])
                    print(f"  Extracted {text_len:,} characters from PDF")
                
                elif step['action'] == 'clean_text':
                    print("  Isolating abstract/introduction...")
                    raw_text = results['extracted']['text']
                    results['clean_text'] = self._find_abstract(raw_text)
                    print(f"  Cleaned text: {len(results['clean_text'])} chars")
                
                elif step['action'] == 'summarize':
                    print("  Generating summary with AI model...")
                    summary = self.model.summarize(results['clean_text'])
                    results['summary'] = summary
                    print(f"  Generated summary ({len(summary)} chars)")
                
                elif step['action'] == 'format_output':
                    results['final_summary'] = results['summary']
                    print("  Output formatted")
            
            except Exception as e:
                print(f"  Error in step {step['step']}: {str(e)}")
                results['error'] = str(e)
                return results
        
        return results
    
    def run(self, pdf_path: str) -> str:
        """
        Main execution method
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Generated summary
        """
        print(f"\n{'='*80}")
        print(f"PAPER SUMMARIZER AGENT")
        print(f"{'='*80}")
        print(f"Input: {pdf_path}\n")
        
        # Plan
        plan = self.create_plan(pdf_path)
        
        # Execute
        print()
        results = self.execute_plan(plan)
        
        # Return result
        if 'final_summary' in results:
            print(f"\n{'='*80}")
            print("SUMMARIZATION COMPLETE")
            print(f"{'='*80}\n")
            return results['final_summary']
        else:
            error_msg = results.get('error', 'Unknown error occurred')
            print(f"\nSummarization failed: {error_msg}")
            return ""

def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description='AI Agent for Academic Paper Summarization',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--pdf', 
        type=str, 
        required=True, 
        help='Path to PDF file'
    )
    
    args = parser.parse_args()
    
    # Create and run agent
    agent = PaperSummarizerAgent()
    summary = agent.run(args.pdf)
    
    # Display result
    if summary:
        print("SUMMARY")
        print("-" * 80)
        print(summary)
        print("-" * 80)
        
        # Save to file
        with open('summary_output.txt', 'w', encoding='utf-8') as f:
            f.write(summary)
        print("\nSummary saved to: summary_output.txt")
    else:
        print("\nNo summary generated")
        sys.exit(1)

if __name__ == "__main__":
    main()

print("File created: src/agent.py")
