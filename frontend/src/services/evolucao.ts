import { api } from '@/lib/api';

export async function gerarNovaEvolucao(pacienteId: string, anotacoes: string, formato: string) {
    try {
        const evolucao = await api.post('/evolucoes/', {
        paciente_id: pacienteId,
        anotacoes_brutas: anotacoes,
        formato_documento: formato,
      // agendamento_id fica nulo até a tela de agenda estar pronta
    });
    
        return evolucao; 
    } catch (error) {
        console.error("Falha na comunicação com o backend:", error);
        throw error;
    }
}