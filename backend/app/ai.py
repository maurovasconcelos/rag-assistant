import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from .guardrails import refine_and_anonymize_text, mask_cpf

load_dotenv()

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("A variável GEMINI_API_KEY não está configurada no arquivo .env")
    # O SDK google-genai busca automaticamente em GEMINI_API_KEY ou podemos passar explicitamente
    return genai.Client(api_key=api_key)

def get_embedding(text: str) -> list[float]:
    """Converte um texto em uma lista de números (embedding) usando o Gemini"""
    client = get_gemini_client()
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=768)
    )
    # Acessamos o vetor do primeiro embedding gerado
    return response.embeddings[0].values

def anonymize_document(text: str) -> str:
    """Passa o texto pelas camadas de segurança LGPD"""
    client = get_gemini_client()
    # 1. Mascara CPFs nativamente com Regex
    text_masked = mask_cpf(text)
    # 2. IA especializada oculta os demais dados LGPD
    return refine_and_anonymize_text(client, text_masked)

def refine_query(query: str) -> str:
    """
    Refiner: Passa a pergunta do usuário pelo modelo para deixá-la 
    mais clara para a busca vetorial.
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
