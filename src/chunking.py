from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.logger import log

class TextChunker:
    def __init__(self, chunk_size=400, chunk_overlap=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        log.info(f"TextChunker initialized with size {chunk_size} and overlap {chunk_overlap}")

    def split_text(self, text):
        if not text:
            log.warning("No text provided to split.")
            return []
        
        log.info("Starting text splitting")
        try:
            chunks = self.splitter.split_text(text)
            log.info(f"Text split into {len(chunks)} chunks")
            return chunks
        except Exception as e:
            log.error(f"Error during text splitting: {e}")
            return []