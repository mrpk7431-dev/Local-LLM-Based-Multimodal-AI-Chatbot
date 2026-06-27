import io
from pypdf import PdfReader
import docx

def extract_text_from_file(uploaded_file):
    """Extracts text from a Streamlit UploadedFile object."""
    filename = uploaded_file.name.lower()
    
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    elif filename.endswith((".txt", ".md", ".csv")):
        return str(uploaded_file.read(), "utf-8", errors="ignore")
    else:
        return f"[Unsupported file type: {filename}]"

def extract_text_from_pdf(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        return f"[Error reading PDF: {str(e)}]"

def extract_text_from_docx(uploaded_file):
    try:
        doc = docx.Document(uploaded_file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        return f"[Error reading DOCX: {str(e)}]"
