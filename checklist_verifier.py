# checklist_verifier.py
import re

class ChecklistVerifier:
    """Verifies document checklist compliance for ADGM processes"""
    
    def __init__(self, rag_engine):
        self.rag_engine = rag_engine
    
    def identify_process(self, document_types):
        """Identify which ADGM process the user is attempting using RAG"""
        if not document_types or len(document_types) == 0:
            return {"process": "Unknown", "confidence": 0.0}
        
        # Use RAG to identify the process
        try:
            # Convert document types to a string
            doc_types_str = ", ".join(document_types)
            
            # Query RAG to identify the process
            query = f"""Based on these document types: {doc_types_str}, what ADGM legal process is the user likely trying to complete? 
            
            Choose from these processes:
            - Company Incorporation
            - Employment Setup
            - Annual Compliance
            - Corporate Governance Update
            - Branch Establishment
            - Data Protection Compliance
            
            Also list what documents are typically required for this process according to ADGM regulations.
            """
            
            rag_response = self.rag_engine.query(query)
            
            # Extract process name and required documents from RAG response
            process_info = self._extract_process_info_from_rag(rag_response, document_types)
            
            if process_info and process_info.get("process") != "Unknown":
                return process_info
            
        except Exception as e:
            print(f"Error querying RAG for process identification: {str(e)}")
        
        # Fallback using heuristics if RAG fails
        return self._fallback_process_identification(document_types)
    
    def _extract_process_info_from_rag(self, rag_response, document_types):
        """Extract process information from RAG response"""
        if not rag_response:
            return None
        
        # List of possible processes
        processes = [
            "Company Incorporation",
            "Employment Setup",
            "Annual Compliance", 
            "Corporate Governance Update",
            "Branch Establishment",
            "Data Protection Compliance"
        ]
        
        # Identify the process
        identified_process = None
        for process in processes:
            if process.lower() in rag_response.lower():
                identified_process = process
                break
        
        if not identified_process:
            return None
        
        # Extract required documents
        required_docs = []
        
        # Look for sections mentioning required documents
        doc_sections = re.findall(r"(?:required|necessary|essential|must have|needed)\s+documents?[:\s]+(.*?)(?:\n\n|\.\s+[A-Z])", rag_response, re.DOTALL | re.IGNORECASE)
        
        if doc_sections:
            # Extract document names from these sections
            for section in doc_sections:
                # Split by lines, commas, or bullets
                items = re.split(r'[\n,•-]+', section)
                for item in items:
                    item = item.strip()
                    if item and len(item) > 5:  # Avoid tiny fragments
                        required_docs.append(item)
        
        # If we couldn't extract required docs, use some fallbacks
        if not required_docs:
            if "Company Incorporation" == identified_process:
                required_docs = ["Articles of Association", "Memorandum of Association", "Board Resolution"]
            elif "Employment Setup" == identified_process:
                required_docs = ["Employment Contract"]
            elif "Annual Compliance" == identified_process:
                required_docs = ["Annual Accounts", "Board Resolution"]
        
        # Calculate a confidence score
        matched_docs = sum(1 for doc_type in document_types if any(req.lower() in doc_type.lower() or doc_type.lower() in req.lower() for req in required_docs))
        confidence = matched_docs / len(required_docs) if required_docs else 0.5
        
        return {
            "process": identified_process,
            "confidence": min(0.9, confidence + 0.3),  # Add a bonus for RAG identification
            "required_docs": required_docs,
            "optional_docs": [],  # We can't reliably extract optional docs
            "rag_response": rag_response
        }
    
    def _fallback_process_identification(self, document_types):
        """Fallback identification using simple heuristics"""
        # Create a simple mapping from document types to likely processes
        process_indicators = {
            "Company Incorporation": ["Articles of Association", "Memorandum of Association", "incorporation"],
            "Employment Setup": ["Employment Contract", "employment"],
            "Annual Compliance": ["Annual Accounts", "annual"],
            "Corporate Governance Update": ["Board Resolution", "Shareholder Resolution", "governance"],
            "Branch Establishment": ["Branch", "branch"],
            "Data Protection Compliance": ["Data Protection", "data protection"]
        }
        
        # Score each process
        scores = {}
        for process, indicators in process_indicators.items():
            score = 0
            for doc_type in document_types:
                for indicator in indicators:
                    if indicator.lower() in doc_type.lower():
                        score += 1
                        break
            scores[process] = score
        
        # Find process with highest score
        best_process = max(scores.items(), key=lambda x: x[1])
        
        if best_process[1] == 0:
            return {"process": "Unknown", "confidence": 0.0}
        
        # Basic required documents for each process
        required_docs = {
            "Company Incorporation": ["Articles of Association", "Memorandum of Association", "Board Resolution"],
            "Employment Setup": ["Employment Contract"],
            "Annual Compliance": ["Annual Accounts", "Board Resolution"],
            "Corporate Governance Update": ["Board Resolution", "Shareholder Resolution"],
            "Branch Establishment": ["Board Resolution"],
            "Data Protection Compliance": ["Data Protection Policy"]
        }
        
        return {
            "process": best_process[0],
            "confidence": min(0.7, best_process[1] / len(document_types)),
            "required_docs": required_docs.get(best_process[0], []),
            "optional_docs": []
        }
    
    def check_missing_documents(self, document_types, process_info):
        """Check for missing required documents for a specific process"""
        if not process_info or process_info.get("process") == "Unknown":
            return []
        
        process_name = process_info.get("process")
        required_docs = process_info.get("required_docs", [])
        
        # Check which required documents are missing
        missing_docs = []
        for req_doc in required_docs:
            req_doc_lower = req_doc.lower()
            found = False
            for doc_type in document_types:
                doc_type_lower = doc_type.lower()
                if req_doc_lower in doc_type_lower or doc_type_lower in req_doc_lower:
                    found = True
                    break
            
            if not found:
                missing_docs.append(req_doc)
        
        return missing_docs
    
    def generate_process_summary(self, document_types, issues_found):
        """Generate a summary of the process and document compliance"""
        # Identify the process
        process_info = self.identify_process(document_types)
        process_name = process_info.get("process")
        
        # Check for missing documents
        missing_docs = self.check_missing_documents(document_types, process_info)
        
        # Create process summary
        summary = {
            "process": process_name,
            "process_description": self._get_process_description(process_name),
            "documents_uploaded": len(document_types),
            "required_documents": len(process_info.get("required_docs", [])),
            "missing_documents": missing_docs if missing_docs else None,
            "issues_count": len(issues_found),
            "critical_issues_count": sum(1 for issue in issues_found if issue.get("severity") == "High"),
            "compliance_percentage": self._calculate_compliance_percentage(document_types, missing_docs, issues_found)
        }
        
        return summary
    
    def _get_process_description(self, process_name):
        """Get description for a process using RAG"""
        try:
            query = f"What is the {process_name} process in ADGM? Provide a brief description."
            response = self.rag_engine.query(query)
            
            # Extract first paragraph or sentence as description
            if response:
                sentences = response.split('.')
                if sentences and len(sentences) > 0:
                    return sentences[0].strip() + '.'
                
                return response[:100] + "..." if len(response) > 100 else response
            
        except Exception as e:
            print(f"Error getting process description: {str(e)}")
        
        # Fallback descriptions
        descriptions = {
            "Company Incorporation": "The process of incorporating a new company in ADGM.",
            "Employment Setup": "Setting up employment documentation for ADGM companies.",
            "Annual Compliance": "Annual filing and compliance requirements for ADGM companies.",
            "Corporate Governance Update": "Updating corporate governance documentation.",
            "Branch Establishment": "Establishing a branch office in ADGM.",
            "Data Protection Compliance": "Ensuring compliance with ADGM Data Protection Regulations."
        }
        
        return descriptions.get(process_name, "ADGM regulatory process.")
    
    def _calculate_compliance_percentage(self, document_types, missing_docs, issues_found):
        """Calculate an overall compliance percentage"""
        # Start with 100% and deduct for various issues
        compliance = 100.0
        
        # Deduct for missing documents (major impact)
        if missing_docs:
            compliance -= len(missing_docs) * 15  # Each missing document reduces compliance by 15%
        
        # Deduct for document issues based on severity
        high_severity_issues = sum(1 for issue in issues_found if issue.get("severity") == "High")
        medium_severity_issues = sum(1 for issue in issues_found if issue.get("severity") == "Medium")
        low_severity_issues = sum(1 for issue in issues_found if issue.get("severity") == "Low")
        
        compliance -= high_severity_issues * 5  # Each high severity issue reduces by 5%
        compliance -= medium_severity_issues * 2  # Each medium severity issue reduces by 2%
        compliance -= low_severity_issues * 1  # Each low severity issue reduces by 1%
        
        # Ensure compliance is between 0 and 100
        return max(0, min(100, compliance))