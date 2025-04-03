from PyPDF2 import PdfReader

SECTION_HEADINGS = [
    "PRASHANT ARYAL",
    "PERSONAL STATEMENT",
    "ACADEMIC QUALIFICATIONS",
    "INTERNSHIPS",
    "RESEARCH",
    "ACADEMIC PROJECTS",
    "TECHNICAL SKILLS",
    "COURSES & CERTIFICATION",
    "OTHER INFORMATION"
]

def extract_cv_sections(pdf_path):
    reader = PdfReader(pdf_path)
    sections = {heading: [] for heading in SECTION_HEADINGS}
    current_section = None
    
    for page in reader.pages:
        text = page.extract_text()
        for line in text.split('\n'):
            clean_line = line.strip()
            
            if clean_line.isupper() and clean_line in SECTION_HEADINGS:
                current_section = clean_line
            elif current_section:
                sections[current_section].append(clean_line)
    
    return {k: ' '.join(v) for k, v in sections.items() if v}
