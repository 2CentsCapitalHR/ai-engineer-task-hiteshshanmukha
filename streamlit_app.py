import streamlit as st
import os
import tempfile
import shutil
import json
from document_processor import DocumentProcessor
from document_analyzer import DocumentAnalyzer
from checklist_verifier import ChecklistVerifier
from rag_engine import RAGEngine

# Initialize components
@st.cache_resource
def load_components():
    # Show loading message
    with st.spinner("Loading ADGM knowledge base... This may take a minute..."):
        rag_engine = RAGEngine()
        doc_processor = DocumentProcessor()
        doc_analyzer = DocumentAnalyzer(rag_engine)
        checklist_verifier = ChecklistVerifier(rag_engine)
        return rag_engine, doc_processor, doc_analyzer, checklist_verifier

# Set up page config
st.set_page_config(
    page_title="ADGM Document Analyzer",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add sidebar with information
with st.sidebar:
    st.title("About")
    st.info(
        """
        This tool analyzes ADGM legal documents using RAG (Retrieval Augmented Generation) with 
        official ADGM sources. It checks documents for compliance with ADGM regulations and 
        highlights issues.
        
        **Features:**
        - Document type identification
        - Legal process detection
        - Missing document verification
        - Compliance analysis
        - Inline issue highlighting
        
        All analysis is based on official ADGM documents and templates.
        """
    )
    
    # Add a button to rebuild RAG if needed
    if st.button("Rebuild Knowledge Base"):
        st.session_state["rebuild_rag"] = True
        st.info("Knowledge base will be rebuilt on next page refresh")

# Check if we need to rebuild RAG
if "rebuild_rag" in st.session_state and st.session_state["rebuild_rag"]:
    # Clear the cached resources
    st.cache_resource.clear()
    st.session_state["rebuild_rag"] = False
    st.experimental_rerun()

# Load components
rag_engine, doc_processor, doc_analyzer, checklist_verifier = load_components()

# Set up the Streamlit UI
st.title("ADGM Corporate Document Analyzer")
st.markdown("""
This tool analyzes ADGM legal documents for compliance with regulations. Upload your documents 
to check for issues and get a detailed compliance report.

**The system will:**
- Identify document types
- Verify completeness against ADGM checklists
- Detect compliance issues
- Add comments to documents highlighting issues
- Generate a comprehensive report
""")

uploaded_files = st.file_uploader("Upload DOCX Documents", type=["docx"], accept_multiple_files=True)

analysis_options = st.expander("Analysis Options", expanded=False)
with analysis_options:
    issue_threshold = st.slider("Issue Detection Sensitivity", min_value=1, max_value=10, value=5, 
                            help="Higher values will detect more potential issues")
    col1, col2 = st.columns(2)
    with col1:
        highlight_issues = st.checkbox("Highlight Issues in Documents", value=True)
    with col2:
        detailed_analysis = st.checkbox("Perform Detailed Analysis", value=True)

# Initialize session state to store analysis results
if 'processed_docs' not in st.session_state:
    st.session_state.processed_docs = None
if 'all_issues' not in st.session_state:
    st.session_state.all_issues = None
if 'reviewed_files' not in st.session_state:
    st.session_state.reviewed_files = None
if 'report' not in st.session_state:
    st.session_state.report = None
if 'missing_docs' not in st.session_state:
    st.session_state.missing_docs = None
if 'process_info' not in st.session_state:
    st.session_state.process_info = None
if 'process_summary' not in st.session_state:
    st.session_state.process_summary = None
if 'temp_dir' not in st.session_state:
    st.session_state.temp_dir = None

if st.button("Analyze Documents", type="primary") and uploaded_files:
    with st.spinner("Processing documents..."):
        # Save uploaded files to temporary location
        temp_dir = tempfile.mkdtemp()
        st.session_state.temp_dir = temp_dir
        saved_files = []
        
        for uploaded_file in uploaded_files:
            # Save file to disk
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            saved_files.append(file_path)
        
        # Process documents
        processed_docs = []
        doc_types = {}
        
        # Create a status element to show progress
        status = st.status("Analyzing documents...", expanded=True)
        
        for file_path in saved_files:
            # Process document
            status.update(label=f"Processing {os.path.basename(file_path)}...")
            doc_info = doc_processor.process_document(file_path)
            if "error" in doc_info:
                status.update(label=f"Error processing {os.path.basename(file_path)}")
                st.error(f"Error processing {os.path.basename(file_path)}: {doc_info['error']}")
                continue
                
            processed_docs.append(doc_info)
            
            # Identify document type
            status.update(label=f"Identifying document type for {os.path.basename(file_path)}...")
            doc_type_info = doc_analyzer.identify_document_type(doc_info)
            doc_types[doc_info["filename"]] = doc_type_info["type"]
            
            status.write(f"Identified '{doc_info['filename']}' as '{doc_type_info['type']}' (confidence: {doc_type_info['confidence']:.2f})")
        
        # Identify process and check for missing documents
        status.update(label="Identifying legal process...")
        process_info = checklist_verifier.identify_process(list(doc_types.values()))
        status.write(f"Identified process: {process_info['process']} (confidence: {process_info['confidence']:.2f})")
        
        missing_docs = checklist_verifier.check_missing_documents(list(doc_types.values()), process_info)
        
        if missing_docs:
            status.write(f"Missing document(s): {', '.join(missing_docs)}")
        else:
            status.write("All required documents for this process have been uploaded.")
        
        # Analyze each document for issues
        all_issues = []
        
        for doc_info in processed_docs:
            doc_type_info = doc_analyzer.identify_document_type(doc_info)
            status.update(label=f"Analyzing {doc_info['filename']} for compliance issues...")
            issues = doc_analyzer.analyze_document(doc_info, doc_type_info)
            
            for issue in issues:
                issue["document"] = doc_info["filename"]
                all_issues.append(issue)
            
            status.write(f"Found {len(issues)} issues in {doc_info['filename']}")
        
        # Add comments to documents
        reviewed_files = []
        
        if highlight_issues:
            status.update(label="Adding comments to documents...")
            for doc_info in processed_docs:
                doc_issues = [i for i in all_issues if i["document"] == doc_info["filename"]]
                if doc_issues:
                    reviewed_file = doc_processor.add_comments(doc_info, doc_issues)
                    if reviewed_file:
                        reviewed_files.append(reviewed_file)
                        status.write(f"Added comments to {os.path.basename(reviewed_file)}")
        
        # Generate report
        status.update(label="Generating compliance report...")
        process_summary = checklist_verifier.generate_process_summary(list(doc_types.values()), all_issues)
        
        report = {
            "process": process_info["process"],
            "process_description": process_summary.get("process_description", ""),
            "documents_uploaded": len(processed_docs),
            "required_documents": len(process_info.get("required_docs", [])),
            "missing_documents": missing_docs if missing_docs else [],
            "issues_count": len(all_issues),
            "critical_issues_count": sum(1 for issue in all_issues if issue.get("severity") == "High"),
            "compliance_percentage": process_summary.get("compliance_percentage", 0)
        }
        
        # Save results to session state
        st.session_state.processed_docs = processed_docs
        st.session_state.all_issues = all_issues
        st.session_state.reviewed_files = reviewed_files
        st.session_state.report = report
        st.session_state.missing_docs = missing_docs
        st.session_state.process_info = process_info
        st.session_state.process_summary = process_summary
        
        # Create JSON file with issues
        issues_json_path = os.path.join(temp_dir, "document_issues.json")
        with open(issues_json_path, "w", encoding="utf-8") as f:
            json.dump(all_issues, f, indent=2)
        
        # Complete the status
        status.update(label="Analysis complete!", state="complete")

# Display results if available
if st.session_state.processed_docs and st.session_state.all_issues:
    st.subheader("Analysis Results")
    
    # Access results from session state
    all_issues = st.session_state.all_issues
    reviewed_files = st.session_state.reviewed_files
    report = st.session_state.report
    missing_docs = st.session_state.missing_docs
    process_info = st.session_state.process_info
    process_summary = st.session_state.process_summary
    temp_dir = st.session_state.temp_dir
    
    # Summary cards
    st.markdown("### Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Process:** {process_info['process']}")
    with col2:
        st.warning(f"**Missing Documents:** {len(missing_docs)}")
    with col3:
        st.error(f"**Issues Found:** {len(all_issues)}")
    
    # Display compliance score with appropriate color
    compliance_percentage = process_summary.get("compliance_percentage", 0)
    score_color = "green"
    if compliance_percentage < 70:
        score_color = "red"
    elif compliance_percentage < 90:
        score_color = "orange"
        
    st.markdown(f"### Compliance Score: <span style='color:{score_color};font-size:24px;'>{compliance_percentage:.0f}%</span>", unsafe_allow_html=True)
    
    # Display issue counts by severity in a horizontal bar
    st.markdown("### Issues by Severity")
    high_count = sum(1 for issue in all_issues if issue.get("severity") == "High")
    medium_count = sum(1 for issue in all_issues if issue.get("severity") == "Medium")
    low_count = sum(1 for issue in all_issues if issue.get("severity") == "Low")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("High Severity", high_count, delta=-high_count, delta_color="inverse")
    with col2:
        st.metric("Medium Severity", medium_count, delta=-medium_count, delta_color="inverse")
    with col3:
        st.metric("Low Severity", low_count, delta=-low_count, delta_color="inverse")
    
    # Display missing documents
    if missing_docs:
        st.markdown("### Missing Documents")
        for doc in missing_docs:
            st.markdown(f"- {doc}")
    
    # Display issues table
    if all_issues:
        st.markdown("### Identified Issues")
        
        # Convert issues to a format for display
        display_issues = []
        for issue in all_issues:
            display_issues.append({
                "Document": issue.get("document", ""),
                "Section": issue.get("section", ""),
                "Issue": issue.get("issue", ""),
                "Severity": issue.get("severity", "Medium"),
                "Suggestion": issue.get("suggestion", "")
            })
        
        # Display as dataframe
        st.dataframe(display_issues, use_container_width=True)
    
    # Provide download section for all files
    st.markdown("### Download Files")
    
    # Create tabs for different download options
    download_tab1, download_tab2 = st.tabs(["Reviewed Documents", "Issues JSON"])
    
    # Tab 1: Reviewed Documents
    with download_tab1:
        if reviewed_files:
            st.markdown("Download documents with inline comments and highlighting:")
            
            # Create columns for download buttons
            cols = st.columns(min(3, len(reviewed_files)))
            for i, file_path in enumerate(reviewed_files):
                col_idx = i % len(cols)
                with cols[col_idx]:
                    try:
                        with open(file_path, "rb") as file:
                            file_name = os.path.basename(file_path)
                            # Store file data in session state to prevent refresh issues
                            key = f"file_{i}"
                            if key not in st.session_state:
                                st.session_state[key] = file.read()
                            
                            st.download_button(
                                label=f"Download {file_name}",
                                data=st.session_state[key],
                                file_name=file_name,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key=f"download_{i}"
                            )
                    except Exception as e:
                        st.error(f"Error preparing download for {file_path}: {str(e)}")
        else:
            st.info("No reviewed documents available for download")
    
    # Tab 2: Issues JSON
    with download_tab2:
        if all_issues:
            # Create JSON file with issues
            issues_json = json.dumps(all_issues, indent=2)
            
            st.markdown("Download all identified issues as JSON:")
            st.download_button(
                label="Download Issues JSON",
                data=issues_json,
                file_name="document_issues.json",
                mime="application/json",
                key="download_json"
            )
            
            # Show preview of JSON
            with st.expander("Preview Issues JSON"):
                st.code(issues_json, language="json")
        else:
            st.info("No issues to download")
    
    # Display detailed report
    with st.expander("Detailed Report", expanded=False):
        # Format the report for display
        formatted_report = json.dumps(report, indent=2)
        st.code(formatted_report, language="json")
        
        # Download full report
        st.download_button(
            label="Download Full Report",
            data=formatted_report,
            file_name="compliance_report.json",
            mime="application/json",
            key="download_report"
        )