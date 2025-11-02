# System Architecture: Paper Summarizer Agent

## 1. Overview

This document describes the architecture of the Paper Summarizer AI Agent, a system designed to automate the extraction and summarization of academic papers.

---

## 2. Design Philosophy

### Simplicity Over Complexity
Rather than building a complex multi-agent system with sophisticated communication protocols, I chose a **simple Planner-Executor pattern**. Why?

1. **Easier to debug**: When something breaks, you know exactly where
2. **Lower latency**: No inter-agent communication overhead  
3. **Sufficient for task**: Paper summarization is sequential, not parallel
4. **Real-world focus**: Production systems favor reliability over sophistication

### Tools, Not Sub-Agents
Instead of separate "Extractor Agent" and "Summarizer Agent", I use **tools** that the main agent calls. This is inspired by Anthropic's agent design patterns:

> "Not every component needs to be an agent. Tools are often sufficient."

---

## 3. Core Components

### 3.1 Agent (Planner + Executor)
**File**: `src/agent.py`  
**Class**: `PaperSummarizerAgent`

This is the "brain" of the system. It has two responsibilities:

#### Planning Phase
```python
def create_plan(pdf_path):
    return [
        {"step": 1, "action": "extract_text"},
        {"step": 2, "action": "clean_text"},
        {"step": 3, "action": "summarize"},
        {"step": 4, "action": "format_output"}
    ]
```

The agent **reasons** about the task and creates a logical sequence.

#### Execution Phase
```python
def execute_plan(plan):
    for step in plan:
        if step['action'] == 'extract_text':
            # Call extraction tool
        elif step['action'] == 'clean_text':
            # Call cleaning logic
        # ... etc
```

The agent **executes** each step, handling errors at each stage.

---

### 3.2 Tool: PDF Extractor
**File**: `src/extract.py`  
**Function**: `extract_text_from_pdf()`

**Purpose**: Extract raw text from PDF files

**Implementation**:
- Uses PyPDF2 library
- Handles corrupted PDFs gracefully
- Returns structured response with success/failure status

**Why PyPDF2?**
- Lightweight (no external dependencies)
- Works on most academic PDFs
- Fast (~1-2 seconds per paper)

**Limitation**: Cannot handle scanned PDFs (would need OCR)

---

### 3.3 Tool: Text Cleaner
**File**: `src/agent.py`  
**Method**: `_find_abstract()`

**Purpose**: Isolate the abstract from the full paper text

**Challenge**: Academic papers have inconsistent formats. Some start with "Abstract", others with "Summary", some have none at all.

**Solution**: Pattern matching with fallbacks
```python
start_keywords = ["Abstract", "ABSTRACT", "Introduction", ...]
end_keywords = ["Keywords:", "1. Introduction", ...]

# Try to find abstract between these markers
# If not found, use first 2000 characters
```

This is the **"smart" part** of the agent. Without this, we'd get summaries of the cover page or references section.

---

### 3.4 Tool: AI Summarizer
**File**: `src/model_simple.py`  
**Class**: `SummarizerModel`

**Purpose**: Generate concise summaries using an LLM

**Model**: microsoft/phi-2 (2.7B parameters)

**Why Phi-2?**
1. **Small enough** to run on consumer hardware (RTX 3060, M1 Mac, etc.)
2. **Smart enough** for academic summarization
3. **Open source** and commercially usable (MIT license)
4. **Fast inference** (~5-10 seconds per summary)

**Prompt Design**:
```python
prompt = f"""You are an academic paper summarizer. 
Provide a concise, single-paragraph summary.

Abstract:
{text}

Summary:"""
```

This structured prompt reduces hallucinations by:
- Setting clear role expectations
- Specifying output format (single paragraph)
- Providing context (it's an abstract, not random text)

---

## 4. Data Flow

### Step-by-Step Execution
```
User uploads PDF
       ↓
┌─────────────────────────────────────┐
│ Agent creates plan (Planning)       │
│ [Extract → Clean → Summarize → Format] │
└───────────────┬─────────────────────┘
                ↓
┌───────────────────────────────────┐
│ Step 1: Extract Text               │
│ - Open PDF with PyPDF2             │
│ - Read all pages                   │
│ - Return raw text (15,000+ chars)  │
└───────────────┬───────────────────┘
                ↓
┌───────────────────────────────────┐
│ Step 2: Clean Text                 │
│ - Find "Abstract" keyword          │
│ - Extract text until "Keywords:"   │
│ - Return clean abstract (500 chars)│
└───────────────┬───────────────────┘
                ↓
┌───────────────────────────────────┐
│ Step 3: Summarize                  │
│ - Feed abstract to Phi-2 model     │
│ - Generate summary (200 chars)     │
│ - Remove hallucinated text         │
└───────────────┬───────────────────┘
                ↓
┌───────────────────────────────────┐
│ Step 4: Format Output              │
│ - Finalize summary                 │
│ - Return to user                   │
└───────────────────────────────────┘
```

---

## 5. Fine-Tuning Architecture

**File**: `fine_tuning/train.py`

### Why Fine-Tune?

Base Phi-2 is a general-purpose model. Fine-tuning specializes it for:
1. **Academic tone**: Papers use formal language
2. **Technical accuracy**: Must preserve domain-specific terms
3. **Consistent structure**: Always generate similar summary formats

### LoRA Configuration
```python
LoraConfig(
    r=8,                               # Rank (smaller = fewer params)
    lora_alpha=16,                     # Scaling factor
    target_modules=["q_proj", "v_proj"] # Only adapt attention layers
)
```

**Why LoRA instead of full fine-tuning?**
- **Memory**: 2GB vs 50GB of VRAM needed
- **Speed**: 1 hour vs 10+ hours training time
- **Quality**: 95% of full fine-tuning performance

### Training Pipeline
1. **Data**: 1,000 paper/abstract pairs from arXiv
2. **Method**: Supervised fine-tuning with `SFTTrainer`
3. **Hardware**: Attempted on T4 GPU (16GB)
4. **Result**: Failed due to memory constraints (documented in report)

---

## 6. Design Trade-offs

### What I Chose

| Decision | Alternative | Why I Chose This |
|----------|-------------|------------------|
| Single agent | Multi-agent | Simpler to debug |
| PyPDF2 | pdfplumber | Faster, lighter |
| Pattern matching | ML classifier | No training needed |
| Base Phi-2 | Fine-tuned | Hardware limits |
| Streamlit UI | React app | Faster to build |

### What I Would Change (Given More Time)

1. **RAG Integration**: Retrieve similar paper summaries for context
2. **Section-wise Summaries**: Summarize intro, methods, results separately
3. **Citation Extraction**: Identify and extract key citations
4. **Multi-modal**: Handle figures and tables
5. **Quantization**: Use 4-bit LoRA for successful training

---

## 7. Conclusion

This architecture prioritizes:
1. **Reliability**: Simple design = fewer failure modes
2. **Speed**: 8 seconds total (extraction + generation)
3. **Extensibility**: Easy to add new tools or models
4. **Practicality**: Runs on consumer hardware

It's not the most sophisticated agent, but it's **practical and it works**.
