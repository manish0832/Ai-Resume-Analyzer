import os
from pdfminer.high_level import extract_text as pdf_extract_text
from docx import Document
import re

def extract_text_from_file(filepath):
    """Extract text from PDF, DOCX, or TXT files"""
    try:
        file_extension = os.path.splitext(filepath)[1].lower()
        
        if file_extension == '.pdf':
            return extract_text_from_pdf(filepath)
        elif file_extension == '.docx':
            return extract_text_from_docx(filepath)
        elif file_extension == '.txt':
            return extract_text_from_txt(filepath)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    except Exception as e:
        raise Exception(f"Error extracting text from file: {str(e)}")


def extract_text_from_pdf(filepath):
    """Extract text from PDF file"""
    try:
        text = pdf_extract_text(filepath)
        return clean_text(text)
    except Exception as e:
        raise Exception(f"Error reading PDF file: {str(e)}")


def extract_text_from_docx(filepath):
    """Extract text from DOCX file"""
    try:
        doc = Document(filepath)
        text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
        return clean_text(text)
    except Exception as e:
        raise Exception(f"Error reading DOCX file: {str(e)}")


def extract_text_from_txt(filepath):
    """Extract text from TXT file with fallback encodings"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        return clean_text(text)
    except:
        try:
            with open(filepath, "r", encoding="latin-1") as f:
                text = f.read()
            return clean_text(text)
        except Exception as e:
            raise Exception(f"Error reading TXT file: {str(e)}")


def clean_text(text):
    """Clean and normalize extracted text"""
    if not text:
        return ""

    # Normalize newlines
    text = text.replace("\r", "\n")

    # Remove multiple blank lines
    text = re.sub(r"\n+", "\n", text)

    # Remove multiple spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Remove unwanted characters (keep important symbols)
    text = re.sub(r"[^\w\s\.\,\;\:\-\@\#\+]", " ", text)

    return text.strip()
