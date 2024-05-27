from sqlalchemy import Column, Table, func, DateTime, Index
from sqlalchemy.sql.sqltypes import String, Integer, TIMESTAMP
from database.conection import engine, meta_data

blacklist_token = Table("blacklist_token",meta_data,
                   Column("id",Integer,primary_key=True,nullable=False),
                   Column("token",String(191), nullable=False),
                   Column("created_at", TIMESTAMP, nullable=False, server_default=func.now()),
                   schema="seguridad"
)

meta_data.create_all(engine, checkfirst=True)

# Crear índices solo si no existen
indexes = Index('idx_token', blacklist_token.c.token)


# Ejecutar la creación de índices
indexes.create(bind=engine, checkfirst=True)