// Garante que aponte para o backend correto
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    export const api = {
    async post(endpoint: string, data: any) {
        const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            // Aqui entrará o token JWT de autenticação mais pra frente
        },
        body: JSON.stringify(data),
        });

        if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro na requisição para a API');
        }

        return response.json();
    }
};