from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, database, security
from .database import engine, SessionLocal
from pydantic import BaseModel
from . import ai_service
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

app = FastAPI(title="CognIA API - Gestão Clínica")

# Permite que o frontend em Next.js (porta 3000) faça requisições para a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

database.test_connection()
# models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"mensagem": "API CognIA operacional."}

@app.post("/usuarios/", response_model=schemas.UsuarioResponse)
def criar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = models.Usuario(
        nome=usuario.nome, 
        email=usuario.email, 
        senha_hash=usuario.senha
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

@app.post("/pacientes/", response_model=schemas.PacienteResponse)
def criar_paciente(paciente: schemas.PacienteCreate, db: Session = Depends(get_db)):
    # 1. Criptografa os campos sensíveis
    queixa_criptografada = security.encrypt_text(paciente.queixa_principal)
    objetivos_criptografados = security.encrypt_text(paciente.objetivos_terapeuticos)
    
    # 2. Prepara os dados para a base de dados
    db_paciente = models.Paciente(
        usuario_id=paciente.usuario_id,
        nome_completo=paciente.nome_completo,
        telefone=paciente.telefone,
        queixa_principal=queixa_criptografada,
        objetivos_terapeuticos=objetivos_criptografados
    )
    
    # 3. Guarda na base de dados
    db.add(db_paciente)
    db.commit()
    db.refresh(db_paciente)
    
    # 4. Descriptografa antes de devolver na resposta da API
    db_paciente.queixa_principal = security.decrypt_text(db_paciente.queixa_principal)
    db_paciente.objetivos_terapeuticos = security.decrypt_text(db_paciente.objetivos_terapeuticos)
    
    return db_paciente

# Esquema provisório só para este teste
class TesteIARequest(BaseModel):
    anotacoes: str
    formato: str = "SOAP" # SOAP, DAP ou LIVRE

@app.post("/teste-ia/")
def testar_geracao_ia(requisicao: TesteIARequest):
    try:
        # Chama o serviço que configurámos
        rascunho = ai_service.gerar_rascunho_evolucao(
            anotacoes_brutas=requisicao.anotacoes,
            formato_documento=requisicao.formato
        )
        return {"rascunho_gerado": rascunho, "modelo_utilizado": ai_service.MODELO_ATUAL}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/evolucoes/", response_model=schemas.EvolucaoResponse)
def criar_evolucao(evolucao: schemas.EvolucaoCreate, db: Session = Depends(get_db)):
    # 1. Gera o rascunho estruturado com a IA (Isso vai levar os 3~4 minutos no ambiente local)
    try:
        rascunho_gerado = ai_service.gerar_rascunho_evolucao(
            anotacoes_brutas=evolucao.anotacoes_brutas,
            formato_documento=evolucao.formato_documento
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na IA: {str(e)}")

    # 2. Criptografa TUDO antes de tocar no banco de dados
    anotacoes_criptografadas = security.encrypt_text(evolucao.anotacoes_brutas)
    rascunho_criptografado = security.encrypt_text(rascunho_gerado)

    # 3. Prepara e salva o registro no banco (seguro e inlegível)
    db_evolucao = models.EvolucaoClinica(
        paciente_id=evolucao.paciente_id,
        agendamento_id=evolucao.agendamento_id,
        anotacoes_brutas=anotacoes_criptografadas,
        rascunho_ia=rascunho_criptografado,
        formato_documento=evolucao.formato_documento.upper(),
        status_documento="Rascunho",
        modelo_ia=ai_service.MODELO_ATUAL
    )
    
    db.add(db_evolucao)
    db.commit()
    db.refresh(db_evolucao)

    # 4. Descriptografa os textos na memória apenas para devolver ao frontend
    db_evolucao.anotacoes_brutas = security.decrypt_text(db_evolucao.anotacoes_brutas)
    db_evolucao.rascunho_ia = security.decrypt_text(db_evolucao.rascunho_ia)

    return db_evolucao

@app.post("/agendamentos/", response_model=schemas.AgendamentoResponse, tags=["Agendamentos"])
def criar_agendamento(agendamento: schemas.AgendamentoCreate, db: Session = Depends(get_db)):
    # 1. Verifica se o paciente existe e pertence ao usuário (valida a FK composta)
    db_paciente = db.query(models.Paciente).filter(
        models.Paciente.id == agendamento.paciente_id,
        models.Paciente.usuario_id == agendamento.usuario_id
    ).first()
    
    if not db_paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado ou não pertence a este usuário.")

    # 2. Prepara o objeto para salvar
    novo_agendamento = models.Agendamento(**agendamento.model_dump())
    db.add(novo_agendamento)
    
    try:
        # Tenta salvar no banco. É aqui que o PostgreSQL vai validar a regra GIST
        db.commit()
        db.refresh(novo_agendamento)
        return novo_agendamento
    except IntegrityError as e:
        db.rollback() # Desfaz a transação que falhou
        
        # 3. Intercepta o erro específico da nossa trava de exclusão
        if "chk_horario_conflito" in str(e.orig):
            raise HTTPException(
                status_code=409, 
                detail="Conflito de horário: Já existe um agendamento ativo para este psicólogo neste intervalo."
            )
        
        # Se for qualquer outro erro de integridade
        raise HTTPException(status_code=400, detail=f"Erro de integridade no banco de dados: {str(e.orig)}")