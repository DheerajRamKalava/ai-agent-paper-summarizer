# Academic Paper Summarizer AI Agent

**Student:** Kalava Dheeraj Ram  
**University:** IIT Palakkad  
**Department:** Data Science  
**Email:** 142301015@smail.iitpkd.ac.in | dheerajramkalava@gmail.com

---

## Project Overview

This project implements an AI agent that automates the manual task of reading and summarizing academic research papers. As a student, I spend significant time reading papers. This agent streamlines that process by:

1. **Extracting** text from PDF papers
2. **Identifying** the abstract/introduction intelligently
3. **Generating** concise summaries using an AI model
4. **Providing** a web interface for easy interaction

### Why This Task?

Reading academic papers is time-consuming. A single paper can take 30-60 minutes to read thoroughly. This agent reduces that to 2-3 minutes only capturing the key ideas.

---

## Requirements Fulfilled

### Mandatory Features
- **AI Agent with Reasoning**: Planner-Executor architecture (`src/agent.py`)
- **Fine-tuned Model**: LoRA fine-tuning pipeline implemented (`fine_tuning/`)
- **Evaluation**: Qualitative evaluation on real papers (see `docs/report.md`)

### Optional Features  
- **Multi-agent**: Planner + Tool-using Executor pattern
- **User Interface**: Full Streamlit web application (`ui.py`)
- **Custom Tools**: PDF extraction, text cleaning modules

---

## How to View the Demo

### Recommended: Watch the Demo Video

A full video demonstration of the working agent and UI is available at the link below.

**[Click here to watch the Demo Video](https://youtu.be/qwDLpBbn1Zs)**

---

### Alternative: View the Demo Screenshots

For a static proof of concept, please see the screenshots of the working agent in the `/demo/` folder.

---

### Alternative: How to Run (Hardware Required)

#### Hardware Requirement: GPU is Necessary

This agent loads the `microsoft/phi-2` (2.7B) model. Running this on a local **CPU** is **not recommended** as it is extremely slow (can take **20-30+ minutes** for one summary).

The intended way to run this project is on a **GPU**, such as the free T4 GPU provided by Google Colab.

#### Running on Colab
To run this project, you would need to follow these steps in a new Colab notebook:

1.  **Set Runtime:**
    * Go to `Runtime` > `Change runtime type` and select `T4 GPU`.

2.  **Clone the Repository:**
    ```bash
    !git clone https://github.com/DheerajRamKalava/ai-agent-paper-summarizer.git
    ```

3.  **Move into Folder:**
    ```python
    %cd ai-agent-paper-summarizer
    ```

4.  **Install Dependencies:**
    ```bash
    !pip install -r requirements.txt
    ```

5.  **Authenticate `ngrok`:**
    * Get a free token from `https://dashboard.ngrok.com/get-started/your-authtoken`.
    ```bash
    !ngrok authtoken <YOUR_TOKEN_HERE>
    ```

6.  **Launch the UI:**
    * This command starts the server in the background and then prints the public link.
    ```python
    !streamlit run ui.py &>/dev/null&
    from pyngrok import ngrok
    import time
    time.sleep(5) 
    print("Click this link to see your UI:")
    print(ngrok.connect(8501))
    ```

7.  **View the App:**
    * Click the generated `ngrok` link and select "Visit Site." The app may take a minute to load the AI model. **If it continues to load for a long time, please refresh the page.** Once loaded, you can upload a PDF to see the summarization, just like in the demo.

Given this complex setup, **viewing the demo video or screenshots in the `/demo/` folder is the recommended way to verify the working UI.**

---

## Architecture
```
┌─────────────┐
│  PDF Input  │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│   Agent (Planner)   │  ← Creates 4-step plan
│  1. Extract Text    │
│  2. Clean Text      │
│  3. Summarize       │
│  4. Format Output   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Execution Loop     │
├─────────────────────┤
│ → PDF Extractor     │  (PyPDF2)
│ → Text Cleaner      │  (Pattern matching)
│ → AI Summarizer     │  (Phi-2 model)
│ → Output Formatter  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   Final Summary     │
└─────────────────────┘
```

For detailed architecture, see `docs/architecture.md`

---

## Project Structure
```
paper-summarizer-agent/
├── src/
│   ├── extract.py           # PDF text extraction
│   ├── model_simple.py      # AI model wrapper
│   └── agent.py             # Main agent logic
├── fine_tuning/
│   ├── prepare_data.py      # Dataset preparation
│   └── train.py             # LoRA fine-tuning
├── docs/
│   ├── architecture.md      # System design
│   └── report.md            # Data science report
├── interaction_logs/
│   └── logs.md              # AI assistance logs
├── evaluation/
│   └── results.json         # Evaluation metrics
├── demo/
│   └──                      # Screenshots of the working UI
├── ui.py                    # Streamlit web interface
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

---

## Key Technical Decisions

### 1. Base Model: microsoft/phi-2
- **Size**: 2.7B parameters (small enough for consumer hardware)
- **Performance**: Strong reasoning capabilities
- **License**: MIT (commercially usable)

### 2. Fine-tuning Method: LoRA
- **Efficiency**: Only 0.1% of parameters trained
- **Speed**: Fits on T4 GPU (though still challenging)
- **Quality**: Comparable to full fine-tuning

### 3. Agent Pattern: Planner-Executor
- **Reasoning**: Creates logical 4-step plan
- **Execution**: Runs each step with error handling
- **Simplicity**: Easy to debug and extend

---

## Evaluation

The agent was tested on 5 different academic papers across various domains:

| Paper | Abstract Found? | Summary Quality | Time |
|-------|----------------|-----------------|------|
| Attention Is All You Need | Yes | Excellent | 8s |
| BERT Paper | Yes | Good | 7s |
| ResNet Paper | Yes | Excellent | 9s |
| Economics Paper | Yes | Good | 8s |
| Physics Paper | Partial | Fair | 10s |

**Overall Success Rate**: 90%

See `docs/report.md` for detailed analysis.

---

## Known Limitations

1. **Scanned PDFs**: Cannot extract text from image-based PDFs
2. **Non-standard formats**: Some papers don't have clear "Abstract" sections
3. **Very long papers**: May miss content beyond first few pages
4. **Model hallucinations**: Base model occasionally adds irrelevant text

---

## What I Learned

1. **Hardware Constraints**: Fine-tuning large models needs serious GPU power
2. **Prompt Engineering**: Good prompts drastically reduce hallucinations
3. **Agent Design**: Simple plans are easier to debug than complex ones
4. **Real-world ML**: Production ML is 20% modeling, 80% engineering

---

## References

- [Building Effective Agents - Anthropic](https://www.anthropic.com/engineering/building-effective-agents)
- [LoRA Paper - Hu et al.](https://arxiv.org/abs/2106.09685)
- [Phi-2 Technical Report - Microsoft](https://huggingface.co/microsoft/phi-2)

---

## Contact

**Kalava Dheeraj Ram**  
IIT Palakkad | Data Science  
Email: 142301015@smail.iitpkd.ac.in | dheerajramkalava@gmail.com  
GitHub: https://github.com/DheerajRamKalava/ai-agent-paper-summarizer
