import PyPDF2
import docx
from io import BytesIO
from typing import Union

class FileProcessor:
    @staticmethod
    def extract_text_from_pdf(content: bytes) -> str:
        """Extract text content from PDF bytes"""
        try:
            pdf_file = BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise ValueError(f"Error processing PDF: {str(e)}")
    
    @staticmethod
    def extract_text_from_docx(content: bytes) -> str:
        """Extract text content from DOCX bytes"""
        try:
            doc = docx.Document(BytesIO(content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise ValueError(f"Error processing DOCX: {str(e)}")
    
    @staticmethod
    def extract_text_from_txt(content: bytes) -> str:
        """Extract text content from TXT bytes"""
        try:
            return content.decode('utf-8').strip()
        except Exception as e:
            raise ValueError(f"Error processing TXT: {str(e)}")