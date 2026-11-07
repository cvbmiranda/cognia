from abc import ABC, abstractmethod

class FormatoEvolucaoStrategy(ABC):
    @abstractmethod
    def construir_prompt(self, anotacoes_brutas: str, objetivos_terapeuticos: str = None) -> str:
        pass

class SoapStrategy(FormatoEvolucaoStrategy):
    def construir_prompt(self, anotacoes_brutas: str, objetivos_terapeuticos: str = None) -> str:
        contexto = f"Objetivos Terapêuticos do Paciente: {objetivos_terapeuticos}\n" if objetivos_terapeuticos else ""
        return f"""
Você é um assistente clínico especializado em psicologia. 
Sua tarefa é organizar as anotações brutas da sessão no formato SOAP (Subjetivo, Objetivo, Avaliação, Plano).

REGRAS ESTRITAS: 
1. NUNCA invente, deduza ou adicione fatos, sintomas, testes ou diagnósticos que não estejam no texto original.
2. Mantenha um tom profissional e direto.
3. Se não houver dados para uma letra do SOAP, escreva exatamente: "Sem dados registrados nesta sessão."
4. Não escreva introduções, saudações ou explicações. Retorne apenas o SOAP.

--- EXEMPLO DE TRANSFORMAÇÃO ---
Anotações Brutas: "Paciente chorou muito ao falar do trabalho. Diz que não dorme faz 3 dias. Fizemos técnica de respiração."
Resposta Esperada:
S: Paciente relata privação de sono há 3 dias e apresenta choro intenso ao abordar questões laborais.
O: Realizada técnica de respiração durante a sessão.
A: Sem dados registrados nesta sessão.
P: Sem dados registrados nesta sessão.
--- FIM DO EXEMPLO ---

{contexto}
Anotações Brutas da Sessão Atual:
{anotacoes_brutas}

Resposta Esperada:
"""

class DapStrategy(FormatoEvolucaoStrategy):
    def construir_prompt(self, anotacoes_brutas: str, objetivos_terapeuticos: str = None) -> str:
        contexto = f"Objetivos Terapêuticos do Paciente: {objetivos_terapeuticos}\n" if objetivos_terapeuticos else ""
        return f"""
Você é um assistente clínico especializado em psicologia. 
Sua tarefa é organizar as anotações brutas da sessão no formato DAP (Dados, Avaliação, Plano).

REGRAS ESTRITAS: 
1. NUNCA invente ou adicione fatos que não estejam nas anotações brutas originais.
2. Mantenha um tom profissional e clínico.
3. Não escreva introduções, saudações ou avisos. Retorne apenas o documento.

--- EXEMPLO DE TRANSFORMAÇÃO ---
Anotações Brutas: "Paciente irritado com a família. Trabalhamos regulação emocional. Marquei retorno para quarta."
Resposta Esperada:
D: Paciente relata irritabilidade nas relações familiares. Realizada intervenção focada em regulação emocional.
A: Sem dados registrados nesta sessão.
P: Agendado retorno para a próxima quarta-feira.
--- FIM DO EXEMPLO ---

{contexto}
Anotações Brutas da Sessão Atual:
{anotacoes_brutas}

Resposta Esperada:
"""

class LivreStrategy(FormatoEvolucaoStrategy):
    def construir_prompt(self, anotacoes_brutas: str, objetivos_terapeuticos: str = None) -> str:
        # A estratégia livre já costuma funcionar bem sem exemplos, pois é apenas reescrita.
        return f"""
Você é um assistente clínico especializado em psicologia.
Sua tarefa é melhorar a coesão, gramática e clareza das anotações brutas da sessão, transformando-as em um texto corrido.

REGRAS ESTRITAS:
1. NÃO invente ou adicione fatos novos em hipótese alguma.
2. Não altere o sentido original das frases.
3. Retorne APENAS o texto revisado, sem introduções.

Anotações Brutas da Sessão:
{anotacoes_brutas}
"""