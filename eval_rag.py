import time
import os
import psutil
from src.retriever import RAGRetriever


TEST_CASES = [
    {
        "pergunta": "What are the annually deaths of lung cancer?",
        "keywords_esperadas": ["1.76", "1,761", "million", "deaths", "1761"]
    },
    {
        "pergunta": "How can bias in AI models for lung nodules be mitigated?",
        "keywords_esperadas": ["day-to-day", "manual", "physician", "diverse", "dataset"]
    },
    {
        "pergunta": "What is the impact of daily paracetamol on stage IV lung cancer?",
        "keywords_esperadas": ["don't have enough information", "not in the context", "cannot answer", "does not directly mention"]
    }
]

def get_ram_mb():
    processo = psutil.Process(os.getpid())
    return processo.memory_info().rss / 1e6

def correr_avaliacao():
    print("INÍCIO DA AVALIAÇÃO DE QUALIDADE E PERFORMANCE (QA)")    
    ram_inicio = get_ram_mb()
    print(f"RAM base do processo: {ram_inicio:.0f} MB")

    print("A iniciar Motor RAG e carregar base de vetores...\n")
    retriever = RAGRetriever()
    
    resultados_tempo = []
    pontuacao_total = 0

    for i, teste in enumerate(TEST_CASES):
        pergunta = teste["pergunta"]
        keywords = teste["keywords_esperadas"]
        
        print(f"\n[Teste {i+1}] Query: '{pergunta}'")
        
        ram_antes = get_ram_mb()
        start_time = time.time()
        
        resposta_obj = retriever.perguntar(pergunta)
        
        elapsed_time = time.time() - start_time
        ram_depois = get_ram_mb()
        
        if resposta_obj and "result" in resposta_obj:
            resposta_texto = resposta_obj["result"]
            resposta_lower = resposta_texto.lower()
            
            
            print(f"  -> Resposta do LLM: {resposta_texto.strip()}")
            
            
            hits = sum(1 for kw in keywords if kw.lower() in resposta_lower)
            score = min(1.0, hits / 2) 
            pontuacao_total += score
            
            print(f"  -> Latência: {elapsed_time:.2f}s")
            print(f"  -> RAM Processo: {ram_depois:.0f} MB (+{ram_depois - ram_antes:.0f} MB)")
            print(f"  -> Score QA Estimado: {score*100:.0f}%\n")
            
            resultados_tempo.append(elapsed_time)
        else:
            print("  -> ERRO: O modelo não devolveu resposta.\n")

    
    latencia_media = sum(resultados_tempo) / len(resultados_tempo) if resultados_tempo else 0
    score_final = (pontuacao_total / len(TEST_CASES)) * 100
    print(f"Configuração:  k=5 | Chunk_size=400 | BGE Embeddings | Query Rewriting=OFF")
    print(f"Tempo médio:   {latencia_media:.2f}s")
    print(f"Tempo máximo:  {max(resultados_tempo):.2f}s" if resultados_tempo else "N/A")
    print(f"RAM máxima:    {get_ram_mb():.0f} MB (Motor RAG Python)")
    print(f"Accuracy (QA Estimado): {score_final:.1f}%")

if __name__ == "__main__":
    correr_avaliacao()