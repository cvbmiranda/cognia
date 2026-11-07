import requests

# Porta padrão do Ollama rodando localmente
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

def gerar_texto_ia(prompt: str, modelo: str = "qwen2.5:3b") -> str:
    """
    Envia o prompt montado para o Ollama e retorna o texto gerado.
    """
    payload = {
        "model": modelo,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1, # Quase zero criatividade = foco total nos dados reais
            "top_p": 0.9
        }
    }
    
    try:
        resposta = requests.post(OLLAMA_URL, json=payload, timeout=60)
        resposta.raise_for_status() # Dispara erro se não for 200 OK
        return resposta.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Não foi possível conectar ao Ollama. Verifique se o serviço está rodando no terminal.")
    except Exception as e:
        raise RuntimeError(f"Erro na comunicação com a IA: {str(e)}")