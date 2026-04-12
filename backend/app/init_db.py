from database import engine
from models import Base
from sqlalchemy import text

def init_db():
    print("Iniciando a criação das tabelas no banco de dados...")
    with engine.connect() as conn:
        print("Ativando a extensão pgvector (se não existir)...")
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    
    print("Criando tabelas baseadas nos modelos...")
    Base.metadata.create_all(bind=engine)
    print("Banco de dados pronto para o RAG!")

if __name__ == "__main__":
    init_db()
