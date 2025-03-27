import fitz
import pytesseract
from PIL import Image
import docx
import tempfile

def extract_text_from_pdf(file_bytes):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp.flush()
        doc = fitz.open(tmp.name)
        return "\n".join([page.get_text() for page in doc])

def extract_text_from_image(file_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(file_bytes)
        tmp.flush()
        img = Image.open(tmp.name)
        return pytesseract.image_to_string(img)

def extract_text_from_docx(file_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(file_bytes)
        tmp.flush()
        doc = docx.Document(tmp.name)
        return "\n".join(p.text for p in doc.paragraphs)
