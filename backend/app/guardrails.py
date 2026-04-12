import re

# Um Guardrail simples e "Hardcoded" para CPFs
def mask_cpf(text: str) -> str:
    """Busca padrões de CPF e mascara com '***.***.***-**'."""
    # Regex genérica para CPF no formato XXX.XXX.XXX-XX ou XXXXXXXXXXX
    cpf_pattern = r'\b(?:\d{3}[.\s]?\d{3}[.\s]?\d{3}[-\s]?\d{2})\b'
    return re.sub(cpf_pattern, '***.***.***-**', text)

# Guardrail com IA (Refiner) usando o Gemini local
def refine_and_anonymize_text(client, text: str) -> str:
    """
    Usa um prompt focado em LGPD para pedir que a IA remova 
    informações sensíveis antes de salvar no banco ou processar.
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
