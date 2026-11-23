import PyPDF2

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, "rb") as file:
            # strict=False allows reading corrupted/incomplete PDFs
            reader = PyPDF2.PdfReader(file, strict=False)
            for page in reader.pages:
                try:
                    text += page.extract_text() or ""
                except Exception:
                    # Skip pages that can't be read
                    continue
    except PyPDF2.errors.PdfReadError as e:
        raise ValueError(f"Invalid or corrupted PDF file: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error reading PDF file: {str(e)}")
    
    if not text.strip():
        raise ValueError("No readable text could be extracted from the PDF file. The file may be corrupted, encrypted, or contain only images.")
    
    return text