import requests
import logging

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO_ATUAL = "qwen2.5:3b"

def gerar_rascunho_evolucao(anotacoes_brutas: str, formato_documento: str = "LIVRE") -> str:
    """
    Comunica com o Ollama local para transformar anotações em texto estruturado.
    """
    if not anotacoes_brutas or anotacoes_brutas.strip() == "":
        raise ValueError("As anotações brutas não podem estar vazias.")

    # Prompt do Sistema (Regras Rígidas)
    system_prompt = (
        "Você é um assistente de redação clínica em psicologia. Sua única função é transformar tópicos curtos "
        "em um texto estruturado, profissional e coeso de evolução clínica.\n"
        "REGRAS ABSOLUTAS:\n"
        "1. NUNCA invente sintomas, diagnósticos, sentimentos ou fatos que não estejam explícitos nas anotações originais.\n"
        "2. Use a terceira pessoa.\n"
        "3. Mantenha um tom neutro e objetivo.\n"
        "4. Se a anotação for muito curta, apenas melhore a gramática, sem adicionar contexto.\n"
    )

    # Injeção dinâmica do formato exigido pela clínica/profissional
    formato_upper = formato_documento.upper()
    if formato_upper == "SOAP":
        system_prompt += (
            "5. Estruture o texto obrigatoriamente em 4 seções com os seguintes subtítulos exatos: "
            "Subjetivo, Objetivo, Avaliação e Plano."
        )
    elif formato_upper == "DAP":
        system_prompt += (
            "5. Estruture o texto obrigatoriamente em 3 seções com os seguintes subtítulos exatos: "
            "Dados, Avaliação e Plano."
        )
    else: # LIVRE
        system_prompt += (
            "5. Escreva um texto narrativo, em parágrafos contínuos, mantendo coesão e ordem cronológica "
            "dos fatos, sem utilizar subtítulos."
        )

    payload = {
        "model": MODELO_ATUAL,
        "prompt": anotacoes_brutas,
        "system": system_prompt,
        "stream": False
    }

    try:
        # Timeout de 300 segundos porque a geração de IA local pode demorar um pouco
        resposta = requests.post(OLLAMA_URL, json=payload, timeout=300)
        resposta.raise_for_status()
        dados = resposta.json()
        return dados.get("response", "").strip()
    except requests.exceptions.RequestException as e:
        logger.error(f"Falha na comunicação com o Ollama: {e}")
        raise RuntimeError(f"Erro ao gerar rascunho com IA: {str(e)}")