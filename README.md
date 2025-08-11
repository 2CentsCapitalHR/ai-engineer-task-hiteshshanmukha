[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/vgbm4cZ0)

# ADGM Corporate Document Analyzer

## Project Overview

The ADGM Corporate Document Analyzer is an AI-powered intelligent legal assistant that reviews, validates, and helps users prepare documentation for business incorporation and compliance within the Abu Dhabi Global Market (ADGM) jurisdiction. The application uses Retrieval Augmented Generation (RAG) to ensure all document analysis aligns with real-world ADGM laws, regulations, and processes.

This Corporate Agent assists users by:
- Automatically identifying document types
- Verifying document completeness based on ADGM checklists
- Detecting legal compliance issues
- Adding inline comments to documents for flagged content
- Generating comprehensive reports

## Features

### Document Processing
- Accepts `.docx` documents uploaded by users
- Parses and analyzes document content
- Identifies document types automatically using AI
- Extracts text, sections, and metadata for comprehensive analysis

### Intelligent Document Analysis
- Uses RAG to validate against official ADGM regulations
- Detects potential legal issues and non-compliance
- Categorizes issues by severity (High, Medium, Low)
- Provides specific references to relevant ADGM regulations

### Checklist Verification
- Automatically recognizes which legal process the user is attempting
- Compares uploaded documents against required ADGM checklists
- Notifies users of any missing mandatory documents
- Supports multiple process types including Company Incorporation, Employment Setup, and more

### Document Enhancement
- Inserts contextual comments directly into `.docx` files
- Highlights problematic sections
- Provides legally compliant clause suggestions
- Generates downloadable marked-up versions of documents

### Reporting
- Generates structured JSON report summarizing findings
- Calculates overall compliance percentage
- Provides comprehensive issue lists with severity ratings
- Offers document-specific recommendations

## Technical Architecture

The application uses a modular architecture with the following components:

1. **RAG Engine**: Connects to ADGM knowledge sources to provide regulatory context
2. **Document Processor**: Handles parsing and modification of documents
3. **Document Analyzer**: Performs detailed analysis of document content
4. **Checklist Verifier**: Validates document completeness against ADGM requirements
5. **Streamlit UI**: Provides a clean, intuitive interface for users

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- Virtual environment (recommended)

### Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-engineer-task-hiteshshanmukha.git
cd ai-engineer-task-hiteshshanmukha
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements-fixed.txt
```

4. Run the Streamlit application:
```bash
streamlit run streamlit_app.py
```

### Using Ollama (Optional)
This project can use Ollama for local LLM integration. If you want to use Ollama:

1. Install Ollama from https://ollama.ai/
2. Pull the required model:
```bash
ollama pull llama3:8b
```

## Usage Instructions

1. Launch the application using `streamlit run streamlit_app.py`
2. Upload one or more `.docx` documents using the file uploader
3. Adjust analysis options as needed
4. Click "Analyze Documents" to start the process
5. View the analysis results, including:
   - Overall compliance score
   - Document type identification
   - Missing document notifications
   - Detailed issue list with severity ratings
6. Download the marked-up documents with inline comments
7. Download the full report in JSON format

## Example Screenshots

Screenshots demonstrating the application functionality can be found in the photos directory.

## Directory Structure

```
ai-engineer-task-hiteshshanmukha/
├── rag_engine.py             # RAG implementation for ADGM knowledge
├── document_processor.py     # Document parsing and modification
├── document_analyzer.py      # Issue detection and analysis
├── checklist_verifier.py     # Document completeness verification
├── adgm_scraper.py           # ADGM website data collector
├── streamlit_app.py          # Main Streamlit application
├── requirements-fixed.txt    # Project dependencies
├── utils/                    # Utility modules
│   ├── adgm_regulations.py   # ADGM regulatory information
│   ├── document_types.py     # Document type definitions
│   └── process_requirements.py # Process requirement definitions
├── testfiles/                # Example test files
│   ├── before/               # Original documents
│   └── after/                # Reviewed documents with comments
├── photos/                   # Screenshots of the application
└── README.md                 # Project documentation
```

## Technologies Used

- **Python 3.8+**: Core programming language
- **Streamlit**: Web interface
- **LangChain**: Framework for working with language models
- **FAISS**: Vector database for efficient similarity search
- **Ollama**: Local LLM integration (optional)
- **HuggingFace Embeddings**: For document embedding
- **python-docx**: For manipulating Word documents
- **PyPDF2**: For PDF extraction
- **BeautifulSoup4**: For web scraping ADGM sources


