const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

// Tipos para o TypeScript saber o formato dos dados
    export interface EvolucaoCreate {
    paciente_id: string;
    agendamento_id?: string | null;
    anotacoes_brutas: string;
    formato_documento: string;
    }

    export interface EvolucaoResponse {
    id: string;
    paciente_id: string;
    agendamento_id: string | null;
    anotacoes_brutas: string;
    rascunho_ia: string;
    texto_final: string | null;
    formato_documento: string;
    status_documento: string;
    modelo_ia: string;
    created_at: string;
    finalizado_em: string | null;
    }

    export const evolucaoService = {
    // Dispara o POST para gerar o rascunho com a IA
    async criarEvolucao(dados: EvolucaoCreate): Promise<EvolucaoResponse> {
        const response = await fetch(`${API_URL}/evolucoes/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(dados),
        });

        if (!response.ok) {
        throw new Error("Falha ao comunicar com o backend para criar evolução");
        }

        return response.json();
    },

    // Dispara o PATCH para salvar a revisão final do psicólogo
    async finalizarEvolucao(id: string, textoFinal: string): Promise<EvolucaoResponse> {
        const response = await fetch(`${API_URL}/evolucoes/${id}/finalizar`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ texto_final: textoFinal }),
        });

        if (!response.ok) {
        throw new Error("Falha ao finalizar a evolução");
        }

        return response.json();
    }
    };