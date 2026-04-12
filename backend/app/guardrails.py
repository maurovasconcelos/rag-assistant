import re

def mask_cpf(text: str) -> str:
    """Busca padrões de CPF e mascara com '***.***.***-**'."""
    cpf_pattern = r'\b(?:\d{3}[.\s]?\d{3}[.\s]?\d{3}[-\s]?\d{2})\b'
    return re.sub(cpf_pattern, '***.***.***-**', text)

def refine_and_anonymize_text(client, text: str) -> str:
    """
    Utiliza um modelo generativo para identificar e remover 
    dados pessoais sensíveis antes do armazenamento ou processamento.
    """
    prompt = f"""Como um agente estrito de segurança de dados (LGPD):
    Revise o texto abaixo e anonimize QUAISQUER dados pessoais sensíveis 
    (Nomes completos, CPFs, RGs, Endereços, Telefones, Emails).
    Substitua o dado removido por uma tag correspondente, ex: [NOME_OCULTADO], [CPF_OCULTADO].
    NÃO altere o sentido geral do documento narrativo. Devolva apenas o texto mascarado, nada mais.
    
    TEXTO ORIGINAL:
    {text}
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text
