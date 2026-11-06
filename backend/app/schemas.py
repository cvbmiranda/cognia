from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime

# --- USUÁRIOS ---
class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    senha: str # Apenas para a criação, nunca retornamos isto

class UsuarioResponse(UsuarioBase):
    id: UUID
    ativo: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# --- PACIENTES ---
class PacienteBase(BaseModel):
    nome_completo: str
    telefone: Optional[str] = None
    queixa_principal: Optional[str] = None
    objetivos_terapeuticos: Optional[str] = None

class PacienteCreate(PacienteBase):
    usuario_id: UUID # Por enquanto passamos manual, depois virá do token JWT

class PacienteResponse(PacienteBase):
    id: UUID
    usuario_id: UUID
    ativo: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# --- AGENDAMENTOS ---

class AgendamentoBase(BaseModel):
    paciente_id: UUID
    usuario_id: UUID
    data_hora_inicio: datetime
    data_hora_fim: datetime
    status: str = "Agendado"
    observacoes: Optional[str] = None

class AgendamentoCreate(AgendamentoBase):
    pass

class AgendamentoResponse(AgendamentoBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)



# --- EVOLUÇÕES CLÍNICAS ---
class EvolucaoCreate(BaseModel):
    paciente_id: UUID
    agendamento_id: Optional[UUID] = None
    anotacoes_brutas: str
    formato_documento: str = "LIVRE" # SOAP, DAP ou LIVRE

class EvolucaoResponse(BaseModel):
    id: UUID
    paciente_id: UUID
    agendamento_id: Optional[UUID]
    
    # Textos que a API vai devolver descriptografados
    anotacoes_brutas: Optional[str]
    rascunho_ia: Optional[str]
    texto_final: Optional[str]
    
    formato_documento: str
    status_documento: str
    modelo_ia: Optional[str]
    
    created_at: datetime
    finalizado_em: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)