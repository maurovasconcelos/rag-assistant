from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .database import get_db
from .models import DocumentModel
from .ai import get_embedding, generate_answer, anonymize_document, refine_query

app = FastAPI(
    title="RAG Assistant API",
    description="API do Assistente RAG Corporativo com buscas semânticas (pgvector + Gemini)",
    version="1.0.0"
)

# Configurar CORS para o Frontend (Next.js) em localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Esquema para recebermos o documento via JSON
class DocumentCreate(BaseModel):
    title: str
    content: str

@app.get("/")
def read_root():
    return {"message": "Hello World! A API do Assistente RAG está no ar."}

@app.post("/documents/")
def add_document(doc: DocumentCreate, db: Session = Depends(get_db)):
    """Endpoint para ingestão e vetorização de documentos."""
    try:
        # Sanitização de dados sensíveis (LGPD)
        safe_content = anonymize_document(doc.content)
        
        # Geração de embeddings para o conteúdo sanitizado
        vetor = get_embedding(safe_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na IA: {str(e)}")
        
    # Salvar documento e embeddings no Postgres
    db_doc = DocumentModel(
        title=doc.title,
        content=safe_content,
        embedding=vetor
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    
    return {"message": "Documento adicionado e vetorizado com sucesso!", "id": db_doc.id}

@app.get("/ask/")
def ask_assistant(query: str, db: Session = Depends(get_db)):
    """Endpoint para busca semântica e geração de resposta aumentada (RAG)."""
    
    try:
        # Otimização da query do usuário
        refined_query = refine_query(query)
        
        # Vetorização da query
        query_embedding = get_embedding(refined_query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar embedding da pergunta: {str(e)}")
        
    # Busca semântica baseada na query (cosine_distance via pgvector)
    resultados = db.query(DocumentModel).order_by(
        DocumentModel.embedding.cosine_distance(query_embedding)
    ).limit(3).all()
    
    if not resultados:
        return {"answer": "Ainda não tenho nenhum documento na minha base para analisar."}
        
    # Construção do contexto agrupando os documentos recuperados
    context = "\n\n---\n\n".join([f"Título: {r.title}\n{r.content}" for r in resultados])
    
    # Geração da resposta via LLM provendo o contexto
    try:
        resposta_final = generate_answer(query, context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar resposta final: {str(e)}")
        
    return {
        "original_query": query,
        "refined_query": refined_query,
        "answer": resposta_final,
        "sources": [r.title for r in resultados]
    }
