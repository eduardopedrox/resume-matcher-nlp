import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///banco_talentos.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=args)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Candidato(Base):
    __tablename__ = "candidatos"

    id = Column(Integer, primary_key=True)
    nome = Column(String(120), nullable=False)
    email = Column(String(120), nullable=False)
    telefone = Column(String(30))
    cidade = Column(String(80))
    area = Column(String(80))
    texto_curriculo = Column(Text, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(engine)