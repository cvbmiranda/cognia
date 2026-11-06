from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from sqlalchemy.exc import OperationalError
import logging

SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://admin:adminpassword@localhost:5433/cognia_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tenta conectar ao banco até 5 vezes, esperando 3 segundos entre cada tentativa
@retry(
    stop=stop_after_attempt(5),
    wait=wait_fixed(3),
    retry=retry_if_exception_type(OperationalError),
    before_sleep=lambda retry_state: logger.warning("Tentando conectar ao banco de dados novamente...")
)
def test_connection():
    try:
        # Tenta abrir uma conexão real para forçar o erro se o banco não estiver pronto
        with engine.connect() as conn:
            logger.info("Conexão com o banco de dados estabelecida com sucesso!")
    except Exception as e:
        logger.error(f"Falha na conexão: {e}")
        raise e