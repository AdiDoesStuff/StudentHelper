import fitz  # PyMuPDF

def extract_text(pdf_path):
    """
    Opens a PDF and extracts text page by page.
    Returns a list of dictionaries: [{"page": 1, "text": "..."}, ...]
    """
    doc = fitz.open(pdf_path)
    pages_data = []
    
    for i, page in enumerate(doc):
        text = page.get_text()
        pages_data.append({
            "page": i + 1,
            "text": text
        })
        
    doc.close()
    return pages_data
