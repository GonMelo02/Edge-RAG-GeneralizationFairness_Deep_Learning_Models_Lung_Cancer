import os
import fitz
from dotenv import load_dotenv
from src.logger import log
import re

load_dotenv()

class PDFIngestor:
    def __init__(self):
        self.data_path = os.getenv("DATA_PATH", "docs")
        log.info(f"PDFIngestor initialized with directory: {self.data_path}")

    def extract_pages_from_pdf(self, file_path):
        """Reads a pdf file and returns a list of dicts with text and page numbers."""
        if not os.path.exists(file_path):
            log.error(f"File not found: {file_path}")
            return None
            
        pages_data = []
        try:
            doc = fitz.open(file_path)
            for num_page in range(doc.page_count):
                text = doc.load_page(num_page).get_text()
                text = re.sub(r'\s+', ' ', text).strip()
                if text.strip():
                    pages_data.append({
                        "texto": text,
                        "pagina": num_page + 1 
                    })
            log.info(f"Extracted {len(pages_data)} pages from: {os.path.basename(file_path)}")
            return pages_data
        except Exception as e:
            log.error(f"Error extracting text from PDF {file_path}: {e}")
            return None

    def load_all_pdfs(self):
        """Scans the directory and extracts text from all PDF files page by page."""
        if not os.path.exists(self.data_path):
            log.error(f"Directory not found: {self.data_path}")
            return []

        documentos = []
        
        for filename in os.listdir(self.data_path):
            if filename.lower().endswith(".pdf"):
                file_path = os.path.join(self.data_path, filename)
                paginas = self.extract_pages_from_pdf(file_path)
                
                if paginas:
                    for pagina in paginas:
                        documentos.append({
                            "texto": pagina["texto"],
                            "fonte": filename,
                            "pagina": pagina["pagina"] 
                        })
        
        log.info(f"Total de páginas processadas com sucesso: {len(documentos)}")
        return documentos