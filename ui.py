import streamlit as st
import os
import sys
import tempfile

# Add src to path (works in Colab and locally)
current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else '/content'
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from agent import PaperSummarizerAgent
except ImportError:
    st.error("Cannot import agent module. Make sure src/agent.py exists.")
    st.stop()

# Page config
st.set_page_config(
    page_title="Paper Summarizer AI Agent",
    page_icon="📄",
    layout="wide"
)

# Title and description
st.title("📄 Academic Paper Summarizer")
st.markdown("""
This AI agent automatically extracts and summarizes academic papers using:
- **Intelligent text extraction** from PDFs
- **Abstract isolation** using pattern matching
- **AI-powered summarization** with Phi-2 model

Upload a research paper PDF to get started!
""")

# --- THIS IS THE FINAL FIX ---

# 1. Load the agent (cached resource)
@st.cache_resource
def load_agent():
    """Load the agent (cached to avoid reloading)"""
    try:
        with st.spinner("Loading AI model... (this may take 1-2 minutes)"):
            return PaperSummarizerAgent()
    except Exception as e:
        st.error(f"Failed to load agent: {e}")
        return None

# 2. Run the summarization (cached data)
# This function is now cached based on the file's *bytes*
@st.cache_data
def generate_summary_from_bytes(_agent, file_bytes: bytes) -> str:
    """
    Runs the agent on the file bytes.
    This is cached so it only runs ONCE per file.
    """
    # Create a temporary file *inside* the cached function
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(file_bytes)
        tmp_path = tmp_file.name
    
    print(f"--- CACHE MISS: Running agent on {tmp_path} ---") # You will see this in the Colab log ONCE
    
    summary = ""
    try:
        # Run the agent on the temp file
        summary = _agent.run(tmp_path)
    except Exception as e:
        print(f"Agent run failed: {e}")
        summary = f"Error: {e}" # Pass the error out
    finally:
        # Clean up the temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    
    return summary
# -----------------------------

# Load agent
agent = load_agent()

if agent is None:
    st.stop()

# File uploader
uploaded_file = st.file_uploader(
    "Choose a PDF file", 
    type="pdf",
    help="Upload an academic paper in PDF format"
)

if uploaded_file is not None:
    st.info(f"📄 Processing: {uploaded_file.name} ({uploaded_file.size:,} bytes)")
    
    # Get the bytes of the file ONCE. This is a stable input.
    pdf_bytes = uploaded_file.getbuffer().tobytes()
    
    with st.spinner("🤖 Agent is analyzing the paper... (This will run once)"):
        # Call the cached function with the STABLE bytes
        summary = generate_summary_from_bytes(agent, pdf_bytes)
    
    # From here on, clicking "Download" will be instant
    # because the cache will hit.
    
    if summary.startswith("Error:"):
        st.error(summary)
    elif summary:
        st.success("✅ Summary generated successfully!")
        st.subheader("📝 Summary")
        
        # Use custom HTML for visible text
        st.markdown(
            f"""
            <div style="background-color: #f0f2f6; color: #000000; padding: 15px; border-radius: 5px; border-left: 5px solid #4CAF50;">
                {summary}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Download button (clicking this will now be instant)
        st.download_button(
            label="📥 Download Summary",
            data=summary,
            file_name=f"{uploaded_file.name}_summary.txt",
            mime="text/plain"
        )
    else:
        st.error("❌ Failed to generate summary. Please try another PDF.")

# Sidebar with info
with st.sidebar:
    st.header("About")
    st.markdown("""
    **Paper Summarizer Agent**
    
    Built by: Kalava Dheeraj Ram  
    University: IIT Palakkad  
    Department: Data Science
    
    ---
    
    **How it works:**
    1. Extracts text from PDF
    2. Identifies abstract/introduction
    3. Generates AI summary
    4. Returns concise summary
    
    **Model:** microsoft/phi-2 (2.7B)
    """)

print("File created: ui.py (Fixed re-summarizing and invisible text bugs)")
