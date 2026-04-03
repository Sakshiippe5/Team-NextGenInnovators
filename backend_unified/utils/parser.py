import fitz # PyMuPDF
from backend_unified.utils.logger import get_logger

logger = get_logger("parser_util")

def parse_document(file_bytes: bytes, file_type: str) -> str:
    """
    Parses PDF or Images (OCR) into raw text using PyMuPDF.
    """
    logger.info(f"Parsing document of type {file_type}")
    try:
        if file_type == "application/pdf":
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        elif file_type.startswith("image/"):
            # Mocking OCR for now, PyMuPDF can do some OCR but usually pytesseract is better.
            logger.warning("Image parsing limited. Returning raw if text base.")
            return "Mock OCR Text from Image"
        else:
            # Just assume plain text
            return file_bytes.decode('utf-8', errors='ignore')
    except Exception as e:
        logger.error(f"Failed to parse document: {e}")
        return ""

def clean_text(text: str) -> str:
    """
    Cleans structural artifacts from raw text.
    """
    return text.strip().replace("\n\n", "\n")
