import re
from docx import Document

def load_docx_text(doc_path):
    doc = Document(doc_path)
    return "\n".join([para.text for para in doc.paragraphs])

def run_validation(doc_path):
    text = load_docx_text(doc_path)

    checks = {
        "No Oxford comma": not re.search(r",\s+and\b", text),
        "Bullet points lowercase": not re.search(r"\n•\s+[A-Z]", text),
        "No punctuation at bullet end": not re.search(r"\n•.*[.,;]\s*$", text, re.MULTILINE),
        "No exclamation marks": "!" not in text,
        "No ampersands": "&" not in text,
        "No ALL CAPS for emphasis": not re.search(r"\b[A-Z]{2,}\b", text),
        "UK spelling - mobilisation": "mobilisation" in text,
        "No Latin words": not any(term in text for term in ["e.g.", "i.e.", "etc.", "per se", "via", "ad hoc"]),
        "Use 'use' not 'utilise'": "utilise" not in text,
        "Use 'help' not 'assist'": "assist" not in text,
        "Avoid abstract 'deliver'": not re.search(r"\bdeliver\b", text.lower()),
        "Time format 5:30pm": bool(re.search(r"\b\d{1,2}:\d{2}(am|pm)\b", text)),
        "No US spelling - 'mobilization'": "mobilization" not in text,
        "Spell out million/billion": not re.search(r"\b\d+(\.\d+)?\s?(m|bn|billion)\b", text.lower()),
        "Correct date format": not re.search(r"\b\d{1,2}(st|nd|rd|th)\s+\w+", text),
        "Use 'to' not dash in ranges": not re.search(r"\bto\b.*–.*\b", text),
    }

    scorecard = {rule: "✅ Passed" if passed else "❌ Failed" for rule, passed in checks.items()}
    return scorecard
