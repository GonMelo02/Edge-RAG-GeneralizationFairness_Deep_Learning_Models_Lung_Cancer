import os
from langchain_ollama import OllamaLLM as Ollama
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from src.logger import log
from src.ingest import PDFIngestor

class RAGRetriever:
    def __init__(self, persist_directory="./vectorstore"):
        self.persist_directory = persist_directory
        
        
        self.model_name = "BAAI/bge-small-en-v1.5"
        
        try:
            log.info(f"A carregar modelo de embeddings ({self.model_name})...")
            
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs={'device': 'cpu'} 
            )
            
            if self._db_exists():
                log.info(" Base de dados encontrada no disco. A carregar (rápido!)...")
                self.vector_db = Chroma(
                    persist_directory=self.persist_directory, 
                    embedding_function=self.embeddings 
                )
            else:
                log.info(" Base de dados vazia. A iniciar Ingestão em Massa...")
                self._build_and_persist_db()
            
            
            self.retriever = self.vector_db.as_retriever(search_kwargs={"k": 5})
            
            
            ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
            self.llm = Ollama(model="llama3.2", base_url=ollama_url, temperature=0.0)
            
            
        except Exception as e:
            log.error(f"Falha crítica ao montar o Retriever: {e}")

    def _db_exists(self):
        return os.path.exists(self.persist_directory) and len(os.listdir(self.persist_directory)) > 0

    def _build_and_persist_db(self):
        ingestor = PDFIngestor()
        artigos = ingestor.load_all_pdfs()
        
        if not artigos:
            raise ValueError("Nenhum PDF encontrado na pasta docs!")
            
        docs = []
        for artigo in artigos:
            doc = Document(
                page_content=artigo["texto"], 
                
                metadata={
                    "source": artigo["fonte"],
                    "page": artigo["pagina"]
                } 
            )
            docs.append(doc)
            
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
        splits = text_splitter.split_documents(docs)
        log.info(f"Textos divididos em {len(splits)} blocos. A gerar vetores matemáticos...")
        
        self.vector_db = Chroma.from_documents(
            documents=splits, 
            embedding=self.embeddings, 
            persist_directory=self.persist_directory
        )
        log.info("Base de dados vetorial gravada no disco com sucesso!")

    def _normalizar_query(self, pergunta):
        return pergunta.lower().strip()

    def perguntar(self, pergunta):
        try:
            pergunta_pesquisa = self._normalizar_query(pergunta)
            
            log.info(f"A pesquisar na base vetorial BGE por: '{pergunta_pesquisa}'")
            documentos_relevantes = self.retriever.invoke(pergunta_pesquisa)
            
            contexto_lista = []
            for doc in documentos_relevantes:
                nome_ficheiro = doc.metadata.get('source', 'Desconhecido')
                numero_pagina = doc.metadata.get('page', 'N/A')
                
                texto = f"[Fonte: {nome_ficheiro} | Página: {numero_pagina}]\n{doc.page_content}"
                contexto_lista.append(texto)
                
            contexto = "\n\n---\n\n".join(contexto_lista)
            
           
            prompt = f"""You are a senior bioinformatics AI assistant.
Answer the user's query based ONLY on the provided context.
Strict Rules:
1. Be concise, direct, and highly professional.
2. DO NOT repeat the authors' names or article titles multiple times.
3. If the context contains specific numbers or statistics, you MUST include them.
4. Cite the source elegantly in brackets at the end of the sentence (e.g., [Source: file.pdf | Page: 4]).
5. If the answer is not in the context, say "I don't have enough information to answer that."

CONTEXT:
{contexto}

USER QUERY:
{pergunta}

ANSWER:"""
            
            log.info("Contexto injetado. A pedir resposta ao LLM local...")
            resposta_texto = self.llm.invoke(prompt)
            
            return {
                "result": resposta_texto,
                "source_documents": documentos_relevantes
            }
            
        except Exception as e:
            log.error(f"Erro ao tentar gerar resposta: {e}")
            return None