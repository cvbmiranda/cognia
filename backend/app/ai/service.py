from .prompts import SoapStrategy, DapStrategy, LivreStrategy
from .ollama_client import gerar_texto_ia


def _fabricar_strategy(formato: str):
    # Factory simples para retornar a classe de estratégia correta.
    formato = formato.upper()
    if formato == "SOAP":
        return SoapStrategy()
    elif formato == "DAP":
        return DapStrategy()
    
    return LivreStrategy()

def processar_evolucao_clinica(anotacoes_brutas: str, formato: str, objetivos_terapeuticos: str = None, modelo: str = "qwen2.5:3b") -> str:
    
    # Orquestra o fluxo completo: escolhe o formato, monta o prompt e chama a IA.
    
    # 1. Pega o construtor correto (SOAP, DAP ou LIVRE)
    estrategia = _fabricar_strategy(formato)
    
    # 2. Constrói o prompt blindado
    prompt = estrategia.construir_prompt(anotacoes_brutas, objetivos_terapeuticos)
    
    # 3. Dispara para o Ollama processar
    texto_final = gerar_texto_ia(prompt=prompt, modelo=modelo)
    
    return texto_final