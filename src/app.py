from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from src.retriever import RAGRetriever
from src.logger import log

class PerguntaInput(BaseModel):
    query: str

rag = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag
    log.info("A iniciar motor RAG...")
    rag = RAGRetriever()
    log.info("Motor RAG pronto.")
    yield
    log.info("A desligar...")

app = FastAPI(title="Edge RAG Bioinformática API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "online", "message": "Edge RAG API está pronta."}

@app.get("/health")
def health():
    return {"status": "ok", "model": "llama3.2", "embeddings": "BAAI/bge-small-en-v1.5"}

@app.post("/perguntar")
def api_perguntar(input_data: PerguntaInput):
    log.info(f"API recebeu pedido: {input_data.query}")
    
    resposta = rag.perguntar(input_data.query)
    
    if not resposta:
        raise HTTPException(status_code=500, detail="Erro ao processar a pergunta.")
    
    
    source_documents = []
    for doc in resposta["source_documents"]:
        source_documents.append({
            "page_content": doc.page_content,
            "metadata": {
                "source": doc.metadata.get("source", "Desconhecido"),
                "page": doc.metadata.get("page", "N/A")
            }
        })
    
    return {
        "result": resposta["result"],
        "source_documents": source_documents
    }