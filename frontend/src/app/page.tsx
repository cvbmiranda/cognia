"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
// O Toaster requer configuração no layout, então vamos usar um alerta simples por agora para focar no fluxo
import { evolucaoService } from "@/services/evolucao"; // Vamos criar este serviço de seguida

export default function EvolucaoIA() {
  const [step, setStep] = useState<"input" | "review">("input");
  const [isLoading, setIsLoading] = useState(false);
  const [anotacoes, setAnotacoes] = useState("");
  const [formato, setFormato] = useState("SOAP");
  const [rascunhoIA, setRascunhoIA] = useState("");
  const [evolucaoId, setEvolucaoId] = useState("");

  const handleGerarEvolucao = async () => {
    if (!anotacoes.trim()) return alert("Por favor, insira as anotações brutas.");
    
    setIsLoading(true);
    try {
      // Usando um ID de paciente fixo para teste
      const pacienteIdTeste = "24ca04de-ca99-40b1-aaa9-f669517f2ee2"; 
      
      const response = await evolucaoService.criarEvolucao({
        paciente_id: pacienteIdTeste,
        agendamento_id: null,
        anotacoes_brutas: anotacoes,
        formato_documento: formato
      });

      setRascunhoIA(response.rascunho_ia);
      setEvolucaoId(response.id);
      setStep("review");
    } catch (error) {
      console.error(error);
      alert("Erro ao gerar evolução com a IA.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleFinalizar = async () => {
    setIsLoading(true);
    try {
      await evolucaoService.finalizarEvolucao(evolucaoId, rascunhoIA);
      alert("Evolução finalizada com sucesso!");
      // Resetar para o estado inicial
      setStep("input");
      setAnotacoes("");
      setRascunhoIA("");
    } catch (error) {
      console.error(error);
      alert("Erro ao finalizar a evolução.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-8 max-w-3xl">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">Assistente Clínico IA (CognIA)</CardTitle>
          <CardDescription>
            {step === "input" 
              ? "Insira as suas notas e deixe a IA estruturar o documento." 
              : "Faça a revisão final do documento gerado antes de assinar."}
          </CardDescription>
        </CardHeader>
        
        <CardContent>
          {step === "input" ? (
            <div className="space-y-6">
              <div className="space-y-2">
                <label className="text-sm font-medium">Formato do Documento</label>
                <Select value={formato} onValueChange={setFormato}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione o formato" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="SOAP">SOAP (Subjetivo, Objetivo, Avaliação, Plano)</SelectItem>
                    <SelectItem value="DAP">DAP (Dados, Avaliação, Plano)</SelectItem>
                    <SelectItem value="LIVRE">Texto Livre (Melhoria de coesão)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Anotações Brutas da Sessão</label>
                <Textarea 
                  placeholder="Escreva aqui tudo o que aconteceu na sessão de forma livre..."
                  className="min-h-[200px]"
                  value={anotacoes}
                  onChange={(e) => setAnotacoes(e.target.value)}
                />
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="rounded-md bg-muted p-4 text-sm text-muted-foreground mb-4">
                <strong>Anotações Originais:</strong> {anotacoes}
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-blue-600 flex items-center gap-2">
                  ✨ Rascunho estruturado pela IA (Editável)
                </label>
                <Textarea 
                  className="min-h-[300px] font-mono text-sm leading-relaxed"
                  value={rascunhoIA}
                  onChange={(e) => setRascunhoIA(e.target.value)}
                />
              </div>
            </div>
          )}
        </CardContent>

        <CardFooter className="flex justify-between border-t pt-6">
          {step === "review" && (
            <Button variant="outline" onClick={() => setStep("input")} disabled={isLoading}>
              Voltar e Refazer
            </Button>
          )}
          
          <Button 
            className={step === "input" ? "w-full" : "ml-auto"}
            onClick={step === "input" ? handleGerarEvolucao : handleFinalizar}
            disabled={isLoading}
          >
            {isLoading 
              ? "A processar..." 
              : step === "input" 
                ? "Gerar Evolução com IA" 
                : "Assinar e Finalizar Documento"}
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}