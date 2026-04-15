from google import genai
from google.genai import types
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .guardrails import refine_and_anonymize_text, mask_cpf
from .config import settings

def get_gemini_client():
    if not settings.GEMINI_API_KEY:
        raise ValueError("A variável GEMINI_API_KEY não está configurada.")
    return genai.Client(api_key=settings.GEMINI_API_KEY)

def chunk_text(text: str) -> list[str]:
    """Fatia textos longos sem quebrar o sentido semântico das frases."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", "!", "?", " ", ""]
    )
    return text_splitter.split_text(text)

def get_embedding(text: str) -> list[float]:
    """Gera embeddings vetoriais a partir do texto fornecido."""
    client = get_gemini_client()
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=768)
    )
    return response.embeddings[0].values

def anonymize_document(text: str) -> str:
    """Retorna o documento após sanitização de PII (LGPD)."""
    client = get_gemini_client()
    text_masked = mask_cpf(text)
    return refine_and_anonymize_text(client, text_masked)

def refine_query(query: str) -> str:
    """
    Otimiza a query do usuário para aumentar a precisão da busca semântica.
    """
    client = get_gemini_client()
    prompt = f"Reformule esta pergunta para ser a mais clara e objetiva possível para uma busca em banco de dados: '{query}'. Retorne apenas a pergunta reformulada."
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

def generate_answer(query: str, context: str) -> str:
    """Gera uma resposta baseada no contexto provido"""
    client = get_gemini_client()
    
    prompt = f"""Você é um Assistente Corporativo prestativo.
        Use EXCLUSIVAMENTE o contexto abaixo para responder à pergunta do usuário.
        Se você não souber a resposta baseado no contexto, diga simplesmente que não encontrou informações suficientes nos documentos.

        Contexto Recuperado dos Documentos:
        {context}

        Pergunta do Usuário: {query}
        """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text
