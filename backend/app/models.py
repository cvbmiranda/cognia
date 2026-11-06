import enum
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, CheckConstraint, UniqueConstraint, ForeignKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

# Nossos Enums em Python (refletidos como VARCHAR no banco)
class FormatoDocumento(str, enum.Enum):
    SOAP = "SOAP"
    DAP = "DAP"
    LIVRE = "LIVRE"

class StatusDocumento(str, enum.Enum):
    RASCUNHO = "Rascunho"
    FINALIZADO = "Finalizado"

class StatusAgendamento(str, enum.Enum):
    AGENDADO = "Agendado"
    CONCLUIDO = "Concluido"
    CANCELADO = "Cancelado"
    FALTA = "Falta"

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    pacientes = relationship("Paciente", back_populates="usuario")

class Paciente(Base):
    __tablename__ = "pacientes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, index=True)
    nome_completo = Column(String, nullable=False, index=True)
    telefone = Column(String, nullable=True)
    queixa_principal = Column(Text, nullable=True) # Criptografado
    objetivos_terapeuticos = Column(Text, nullable=True) # Criptografado
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    usuario = relationship("Usuario", back_populates="pacientes")
    
    # Exigência do PostgreSQL: Para a FK composta em Agendamentos funcionar, 
    # precisamos garantir que essa dupla seja única aqui.
    __table_args__ = (
        UniqueConstraint('id', 'usuario_id', name='uq_paciente_usuario'),
    )

class Agendamento(Base):
    __tablename__ = "agendamentos"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(UUID(as_uuid=True), nullable=False)
    usuario_id = Column(UUID(as_uuid=True), nullable=False)
    data_hora_inicio = Column(DateTime(timezone=True), nullable=False)
    data_hora_fim = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, nullable=False, default=StatusAgendamento.AGENDADO.value)
    observacoes = Column(Text, nullable=True) # Criptografado
    
    __table_args__ = (
        # FK Composta
        ForeignKeyConstraint(
            ['paciente_id', 'usuario_id'],
            ['pacientes.id', 'pacientes.usuario_id'],
            name='fk_agendamento_paciente_usuario'
        ),
        # Trava 1: Valida o status
        CheckConstraint(
            f"status IN ('{StatusAgendamento.AGENDADO.value}', '{StatusAgendamento.CONCLUIDO.value}', '{StatusAgendamento.CANCELADO.value}', '{StatusAgendamento.FALTA.value}')", 
            name='chk_status_agendamento'
        ),
        # Trava 2: Impede consulta de 0 minutos ou tempo negativo
        CheckConstraint(
            "data_hora_fim > data_hora_inicio", 
            name="chk_horario_valido"
        ),
    )

class EvolucaoClinica(Base):
    __tablename__ = "evolucoes_clinicas"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False, index=True)
    agendamento_id = Column(UUID(as_uuid=True), ForeignKey("agendamentos.id"), nullable=True, unique=True)
    evolucao_retificada_id = Column(UUID(as_uuid=True), ForeignKey("evolucoes_clinicas.id"), nullable=True)
    
    anotacoes_brutas = Column(Text, nullable=False) # Criptografado
    rascunho_ia = Column(Text, nullable=True) # Criptografado
    texto_final = Column(Text, nullable=True) # Criptografado
    
    formato_documento = Column(String, nullable=False)
    status_documento = Column(String, nullable=False, default=StatusDocumento.RASCUNHO.value)
    modelo_ia = Column(String, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    finalizado_em = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        CheckConstraint(
            f"formato_documento IN ('{FormatoDocumento.SOAP.value}', '{FormatoDocumento.DAP.value}', '{FormatoDocumento.LIVRE.value}')", 
            name='chk_formato_documento'
        ),
        CheckConstraint(
            f"status_documento IN ('{StatusDocumento.RASCUNHO.value}', '{StatusDocumento.FINALIZADO.value}')", 
            name='chk_status_documento'
        ),
    )