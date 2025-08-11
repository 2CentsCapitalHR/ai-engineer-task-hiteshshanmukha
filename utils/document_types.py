# utils/document_types.py
DOCUMENT_TYPES = {
    "Articles of Association": {
        "category": "Formation",
        "keywords": ["articles", "association", "objects", "share capital", "directors", "shareholders", "aoa"],
        "patterns": [
            r"articles\s+of\s+association",
            r"company\s+constitution",
            r"the\s+articles"
        ]
    },
    "Memorandum of Association": {
        "category": "Formation",
        "keywords": ["memorandum", "objects", "registered office", "liability", "subscriber", "moa"],
        "patterns": [
            r"memorandum\s+of\s+association",
            r"company\s+memorandum"
        ]
    },
    "Board Resolution": {
        "category": "Governance",
        "keywords": ["resolution", "board", "directors", "meeting", "approve", "resolved"],
        "patterns": [
            r"board\s+resolution",
            r"directors'\s+resolution",
            r"be\s+it\s+resolved",
            r"the\s+board\s+hereby\s+resolves"
        ]
    },
    "Shareholder Resolution": {
        "category": "Governance",
        "keywords": ["shareholder", "resolution", "vote", "meeting", "approve", "consent"],
        "patterns": [
            r"shareholder\s+resolution",
            r"resolution\s+of\s+shareholders",
            r"members'\s+resolution",
            r"special\s+resolution",
            r"ordinary\s+resolution",
            r"we,\s+being\s+the\s+shareholders"
        ]
    },
    "Employment Contract": {
        "category": "Employment",
        "keywords": ["employment", "contract", "salary", "working hours", "leave", "termination"],
        "patterns": [
            r"employment\s+contract",
            r"employment\s+agreement",
            r"contract\s+of\s+employment"
        ]
    },
    "UBO Declaration": {
        "category": "Compliance",
        "keywords": ["beneficial", "owner", "ubo", "control", "share", "interest"],
        "patterns": [
            r"beneficial\s+owner",
            r"ubo\s+declaration",
            r"ultimate\s+beneficial\s+owner"
        ]
    },
    "Company Incorporation": {
        "category": "Formation",
        "keywords": ["incorporation", "incorporate", "company formation", "register"],
        "patterns": [
            r"incorporation\s+of",
            r"company\s+formation",
            r"certificate\s+of\s+incorporation"
        ]
    },
    "Register of Members": {
        "category": "Compliance",
        "keywords": ["register", "members", "shareholders", "shares", "allotment"],
        "patterns": [
            r"register\s+of\s+members",
            r"shareholders'\s+register"
        ]
    },
    "Data Protection Policy": {
        "category": "Compliance",
        "keywords": ["data", "protection", "privacy", "personal", "information"],
        "patterns": [
            r"data\s+protection\s+policy",
            r"privacy\s+policy",
            r"appropriate\s+policy\s+document"
        ]
    },
    "Annual Accounts": {
        "category": "Compliance",
        "keywords": ["accounts", "financial", "statements", "audit", "annual"],
        "patterns": [
            r"annual\s+accounts",
            r"financial\s+statements",
            r"balance\s+sheet"
        ]
    },
    "Branch Registration": {
        "category": "Formation",
        "keywords": ["branch", "foreign", "registration", "establishment"],
        "patterns": [
            r"branch\s+registration",
            r"foreign\s+company\s+branch"
        ]
    },
    "Checklist": {
        "category": "Compliance",
        "keywords": ["checklist", "requirements", "steps", "company setup"],
        "patterns": [
            r"checklist",
            r"company\s+set-?up",
            r"step\s+by\s+step"
        ]
    }
}

# Improved signatures for document type detection
DOCUMENT_SIGNATURES = {
    "articles of association of": "Articles of Association",
    "memorandum of association": "Memorandum of Association",
    "we, the undersigned directors": "Board Resolution",
    "resolution of the board of directors": "Board Resolution",
    "resolution of the shareholders": "Shareholder Resolution",
    "we, being the shareholders": "Shareholder Resolution",
    "special resolution of the members": "Shareholder Resolution",
    "employment contract": "Employment Contract",
    "contract of employment": "Employment Contract",
    "declaration of beneficial ownership": "UBO Declaration",
    "ubo declaration form": "UBO Declaration",
    "certificate of incorporation": "Company Incorporation",
    "register of members of": "Register of Members",
    "data protection policy": "Data Protection Policy",
    "appropriate policy document": "Data Protection Policy",
    "annual accounts for the financial year": "Annual Accounts",
    "branch registration application": "Branch Registration",
    "checklist – company set-up": "Checklist"
}