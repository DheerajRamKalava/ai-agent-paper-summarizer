"""
PDF text extraction module
Handles reading and processing PDF files
"""
import PyPDF2
from typing import Dict, List

def extract_text_from_pdf(pdf_path: str) -> Dict[str, any]:
    """
    Extract text from a PDF file
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dictionary containing extracted text, metadata, and success status
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extracting metadata
            metadata = {
                'num_pages': len(pdf_reader.pages),
                'title': 'Unknown'
            }
            
            if pdf_reader.metadata:
                metadata['title'] = pdf_reader.metadata.get('/Title', 'Unknown')
            
            # Extracting text from all pages
            full_text = ""
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
            
            # Basic cleaning
            full_text = full_text.replace('\n\n', '\n').strip()
            
            return {
                'text': full_text,
                'metadata': metadata,
                'success': True
            }
            
    except FileNotFoundError:
        return {
            'text': '',
            'metadata': {},
            'success': False,
            'error': f'File not found: {pdf_path}'
        }
    except Exception as e:
        return {
            'text': '',
            'metadata': {},
            'success': False,
            'error': str(e)
        }

def chunk_text(text: str, max_length: int = 4000) -> List[str]:
    """
    Split text into manageable chunks
    
    Args:
        text: Text to split
        max_length: Maximum characters per chunk
        
    Returns:
        List of text chunks
    """
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        word_length = len(word) + 1  # +1 for space
        
        if current_length + word_length > max_length:
            if current_chunk:  # Avoid empty chunks
                chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = word_length
        else:
            current_chunk.append(word)
            current_length += word_length
    
    # Add remaining words
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks if chunks else [text[:max_length]]

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = extract_text_from_pdf(sys.argv[1])
        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Text length: {len(result['text'])} characters")
            print(f"First 200 chars: {result['text'][:200]}...")
        else:
            print(f"Error: {result['error']}")

print("File created: src/extract.py")
