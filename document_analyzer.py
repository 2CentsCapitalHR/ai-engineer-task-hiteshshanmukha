# document_analyzer.py
import os
import re
import json
from utils.document_types import DOCUMENT_SIGNATURES

class DocumentAnalyzer:
    """Analyzes documents for compliance with ADGM regulations using RAG"""
    
    def __init__(self, rag_engine):
        self.rag_engine = rag_engine
        # Only keep basic signatures for initial identification
        self.document_signatures = DOCUMENT_SIGNATURES
    
    def identify_document_type(self, doc_info):
        """Identify the type of document using RAG and basic signatures"""
        filename = doc_info.get("filename", "")
        content = doc_info.get("content", "")
        
        if not content:
            return {"type": "Unknown", "confidence": 0.0}
        
        # Convert to lowercase for better matching
        content_lower = content.lower()
        filename_lower = filename.lower()
        
        # First check for exact signatures that strongly indicate document type
        for signature, doc_type in self.document_signatures.items():
            if signature.lower() in content_lower:
                return {"type": doc_type, "confidence": 0.9, "signature_match": signature}
        
        # If no direct signature, use RAG to identify document type
        try:
            # Use only first 1000 chars to avoid token limits
            content_sample = content[:1000] + "..." if len(content) > 1000 else content
            query = f"""What type of ADGM legal document is this? 
            Provide only the document type from the following list: 
            - Articles of Association
            - Memorandum of Association
            - Board Resolution
            - Shareholder Resolution
            - Employment Contract
            - UBO Declaration
            - Data Protection Policy
            - Register of Members
            - Register of Directors
            
            Content sample: {content_sample}"""
            
            rag_response = self.rag_engine.query(query)
            
            # Extract document type from RAG response
            doc_type = self._extract_doc_type_from_rag(rag_response)
            if doc_type:
                return {"type": doc_type, "confidence": 0.8, "rag_identification": True}
            
        except Exception as e:
            print(f"Error querying RAG for document type: {str(e)}")
        
        # Fallback to heuristics if RAG fails
        if "article" in filename_lower or "article" in content_lower:
            return {"type": "Articles of Association", "confidence": 0.6}
        elif "memorandum" in filename_lower or "memorandum" in content_lower:
            return {"type": "Memorandum of Association", "confidence": 0.6}
        elif "board" in filename_lower and "resolution" in filename_lower:
            return {"type": "Board Resolution", "confidence": 0.6}
        elif "shareholder" in filename_lower and "resolution" in filename_lower:
            return {"type": "Shareholder Resolution", "confidence": 0.6}
        elif "employment" in filename_lower or "contract" in filename_lower:
            return {"type": "Employment Contract", "confidence": 0.6}
        elif "ubo" in filename_lower or "beneficial owner" in content_lower:
            return {"type": "UBO Declaration", "confidence": 0.6}
        elif "data protection" in filename_lower or "data protection" in content_lower:
            return {"type": "Data Protection Policy", "confidence": 0.6}
        
        return {"type": "Unknown", "confidence": 0.0}
    
    def _extract_doc_type_from_rag(self, rag_response):
        """Extract document type from RAG response"""
        if not rag_response:
            return None
            
        # List of document types to check for
        doc_types = [
            "Articles of Association",
            "Memorandum of Association",
            "Board Resolution",
            "Shareholder Resolution",
            "Employment Contract",
            "UBO Declaration", 
            "Data Protection Policy",
            "Register of Members",
            "Register of Directors"
        ]
        
        # Check for exact document type mentions
        for doc_type in doc_types:
            if doc_type.lower() in rag_response.lower():
                return doc_type
        
        # Check for partial matches
        for doc_type in doc_types:
            parts = doc_type.lower().split()
            if len(parts) > 1:
                # Check if most parts are in the response
                matches = 0
                for part in parts:
                    if len(part) > 3 and part in rag_response.lower():
                        matches += 1
                if matches >= len(parts) - 1:
                    return doc_type
                
        return None
    
    def analyze_document(self, doc_info, doc_type_info):
        """Analyze document for issues using RAG"""
        doc_type = doc_type_info.get("type", "Unknown")
        content = doc_info.get("content", "")
        
        if not content or doc_type == "Unknown":
            return [{"section": "General", "issue": "Unable to identify document type", "severity": "High"}]
        
        # Get section locations for targeting comments
        sections = doc_info.get("sections", [])
        section_names = [s.get("title", "") for s in sections]
        
        # Use RAG to analyze the document for issues
        issues = self._analyze_with_rag(content, doc_type, section_names)
        
        # If RAG doesn't find issues, add a fallback issue
        if not issues:
            issues.append({
                "section": "General",
                "issue": "Document analysis completed but no specific issues were identified. Recommend manual review.",
                "severity": "Low"
            })
        
        return issues
    
    def _analyze_with_rag(self, content, doc_type, section_names):
        """Use RAG to analyze document based on ADGM regulations"""
        try:
            # Create content sample to avoid token limits
            content_sample = content[:3000] + "..." if len(content) > 3000 else content
            
            # Create specific query based on document type
            query = f"""Analyze this {doc_type} for compliance with ADGM regulations. 
            
            Look SPECIFICALLY for:
            1. Invalid or missing clauses that should be in a {doc_type}
            2. Incorrect jurisdiction references (e.g., UAE Federal Courts instead of ADGM)
            3. Ambiguous or non-binding language (e.g., "may or may not", "as applicable")
            4. Missing signatory sections or improper formatting
            5. Non-compliance with ADGM-specific templates
            
            Document content: {content_sample}
            
            For each issue found, return in this EXACT format:
            {{
                "section": "Section name where issue is found",
                "issue": "Detailed description of the specific issue",
                "severity": "High/Medium/Low",
                "suggestion": "Specific suggestion for correction",
                "regulation": "Relevant ADGM regulation"
            }}
            
            Include a list of sections found in the document: {', '.join(section_names) if section_names else 'No sections identified'}
            """
            
            # Get analysis from RAG
            rag_response = self.rag_engine.query(query)
            
            if rag_response:
                # Extract potential issues from RAG response
                return self._extract_issues_from_rag(rag_response, doc_type, section_names)
            
            return []
        except Exception as e:
            print(f"Error analyzing document with RAG: {str(e)}")
            return []
    
    def _extract_issues_from_rag(self, rag_response, doc_type, section_names):
        """Extract issues from RAG response"""
        issues = []
        
        # Try to extract JSON objects first
        json_pattern = r"\{[\s\S]*?\}"
        json_matches = re.findall(json_pattern, rag_response)
        
        for json_str in json_matches:
            try:
                issue = json.loads(json_str)
                # Check if it has the required fields
                if "section" in issue and "issue" in issue:
                    # Ensure severity field
                    if "severity" not in issue:
                        issue["severity"] = "Medium"
                    issues.append(issue)
            except json.JSONDecodeError:
                pass
        
        # If JSON extraction didn't work, try pattern-based extraction
        if not issues:
            # Look for issue patterns
            issue_pattern = r"(?:Issue|Problem|Missing|Incorrect):\s*([^\n]+)"
            issue_matches = re.findall(issue_pattern, rag_response, re.IGNORECASE)
            
            section_pattern = r"(?:Section|Part|Clause):\s*([^\n]+)"
            severity_pattern = r"(?:Severity|Priority):\s*(High|Medium|Low)"
            suggestion_pattern = r"(?:Suggestion|Recommendation|Fix):\s*([^\n]+)"
            regulation_pattern = r"(?:Regulation|Compliance|Reference):\s*([^\n]+)"
            
            for issue_text in issue_matches:
                # Find a nearby section
                section_search = re.search(section_pattern, rag_response, re.IGNORECASE)
                section = section_search.group(1) if section_search else "General"
                
                # Find severity
                severity_search = re.search(severity_pattern, rag_response, re.IGNORECASE)
                severity = severity_search.group(1) if severity_search else "Medium"
                
                # Find suggestion
                suggestion_search = re.search(suggestion_pattern, rag_response, re.IGNORECASE)
                suggestion = suggestion_search.group(1) if suggestion_search else None
                
                # Find regulation
                regulation_search = re.search(regulation_pattern, rag_response, re.IGNORECASE)
                regulation = regulation_search.group(1) if regulation_search else "ADGM Regulations"
                
                issues.append({
                    "section": section,
                    "issue": issue_text.strip(),
                    "severity": severity,
                    "suggestion": suggestion,
                    "regulation": regulation
                })
        
        # If we still don't have issues, try one more approach - looking for sentence-based issues
        if not issues:
            sentences = re.split(r'(?<=[.!?])\s+', rag_response)
            current_section = None
            current_issue = None
            
            for sentence in sentences:
                # Check if this defines a section
                if re.match(r'^(in|the|section|regarding|part)', sentence.lower()):
                    for section in section_names:
                        if section.lower() in sentence.lower():
                            current_section = section
                            break
                
                # Check if this describes an issue
                if any(keyword in sentence.lower() for keyword in ["missing", "should", "required", "must", "incorrect", "issue"]):
                    current_issue = sentence
                    
                    # Try to determine severity
                    severity = "Medium"
                    if any(high in sentence.lower() for high in ["critical", "serious", "major", "high"]):
                        severity = "High"
                    elif any(low in sentence.lower() for low in ["minor", "small", "low"]):
                        severity = "Low"
                    
                    issues.append({
                        "section": current_section if current_section else "General",
                        "issue": current_issue.strip(),
                        "severity": severity,
                        "suggestion": None,
                        "regulation": "ADGM Regulations"
                    })
        
        return issues