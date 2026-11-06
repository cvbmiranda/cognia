"use client";

import { useState } from "react";
import { gerarNovaEvolucao } from "@/services/evolucao";

export default function TelaAtendimento() {
  const [pacienteId, setPacienteId] = useState("");
  const [anotacoes, setAnotacoes] = useState("");
  const [formato, setFormato] = useState("SOAP");
  
  const [rascunho, setRascunho] = useState("");
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState("");

  async function handleGerarEvolucao(e: React.FormEvent) {
    e.preventDefault();
    setErro("");
    setRascunho("");
    setCarregando(true);

    try {
      // Chama o nosso serviço que se comunica com o FastAPI
      const evolucao = await gerarNovaEvolucao(pacienteId, anotacoes, formato);
      setRascunho(evolucao.rascunho_ia);
    } catch (err: any) {
      setErro(err.message || "Erro ao gerar a evolução.");
    } finally {
      setCarregando(false);
    }
  }

  return (
    <main className="min-h-screen bg-gray-50 p-8 text-gray-900">
      <div className="max-w-3xl mx-auto space-y-8">
        <header>
          <h1 className="text-3xl font-bold">Atendimento - CognIA</h1>
          <p className="text-gray-600">Geração de evolução com IA local</p>
        </header>

        <form onSubmit={handleGerarEvolucao} className="bg-white p-6 rounded-lg shadow-sm border space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">ID do Paciente (UUID válido)</label>
            <input
              type="text"
              required
              value={pacienteId}
              onChange={(e) => setPacienteId(e.target.value)}
              className="w-full border rounded p-2"
              placeholder="Ex: b1354a38-af54-44a3-b889-520980868799"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Formato do Documento</label>
            <select
              value={formato}
              onChange={(e) => setFormato(e.target.value)}
              className="w-full border rounded p-2"
            >
              <option value="SOAP">SOAP</option>
              <option value="DAP">DAP</option>
              <option value="LIVRE">Livre / Narrativa</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Anotações Brutas da Sessão</label>
            <textarea
              required
              rows={4}
              value={anotacoes}
              onChange={(e) => setAnotacoes(e.target.value)}
              className="w-full border rounded p-2"
              placeholder="Digite os tópicos soltos falados na sessão..."
            />
          </div>

          <button
            type="submit"
            disabled={carregando}
            className="w-full bg-blue-600 text-white font-semibold py-2 px-4 rounded hover:bg-blue-700 disabled:bg-blue-300 transition-colors"
          >
            {carregando ? "Processando no Ollama (isso pode levar uns 3-4 minutos)..." : "Gerar Rascunho com IA"}
          </button>

          {erro && <p className="text-red-600 text-sm mt-2">{erro}</p>}
        </form>

        {rascunho && (
          <div className="bg-white p-6 rounded-lg shadow-sm border border-green-200">
            <h2 className="text-xl font-bold mb-4 text-green-800">Rascunho Gerado para Revisão</h2>
            <div className="whitespace-pre-wrap text-gray-800 bg-gray-50 p-4 rounded border">
              {rascunho}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}