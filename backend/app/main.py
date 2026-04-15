from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .database import get_db
from .models import DocumentModel
from .ai import get_embedding, generate_answer, anonymize_document, refine_query, chunk_text

app = FastAPI(
    title="RAG Assistant API",
    description="API do Assistente RAG Corporativo com buscas semânticas (pgvector + Gemini)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DocumentCreate(BaseModel):
    title: str
    content: str

@app.get("/")
def read_root():
    return {"message": "Hello World! A API do Assistente RAG está no ar."}

@app.post("/documents/")
def add_document(doc: DocumentCreate, db: Session = Depends(get_db)):
    """Endpoint para ingestão e vetorização de documentos com Chunking."""
    try:
        safe_content = anonymize_document(doc.content)
        chunks = chunk_text(safe_content)
        
        db_docs = []
        for index, chunk in enumerate(chunks):
            vetor = get_embedding(chunk)
            db_doc = DocumentModel(
                title=f"{doc.title} (Parte {index+1})" if len(chunks) > 1 else doc.title,
                content=chunk,
                embedding=vetor
            )
            db.add(db_doc)
            db_docs.append(db_doc)
            
        db.commit()
        return {"message": f"Documento '{doc.title}' fatiado em {len(chunks)} chunks e vetorizado com sucesso!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro na IA/Processamento: {str(e)}")

@app.get("/ask/")
def ask_assistant(query: str, db: Session = Depends(get_db)):
    """Endpoint para busca semântica e geração de resposta aumentada (RAG)."""
    
    try:
        refined_query = refine_query(query)
        query_embedding = get_embedding(refined_query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar embedding da pergunta: {str(e)}")
        
    resultados = db.query(DocumentModel).order_by(
        DocumentModel.embedding.cosine_distance(query_embedding)
    ).limit(3).all()
    
    if not resultados:
        return {"answer": "Ainda não tenho nenhum documento na minha base para analisar."}
        
    context = "\n\n---\n\n".join([f"Título: {r.title}\n{r.content}" for r in resultados])
    
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
