from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer, BigInteger, Boolean, TIMESTAMP, DOUBLE_PRECISION, Float
from sqlalchemy.sql.functions import func
from database.conection import engine, meta_data

rutas = Table("rutas", meta_data,
              Column("id", Integer, primary_key=True),
              Column("fk_use_id", Integer, ForeignKey("usuarios.id"), nullable=False),
              Column("fk_use2_id", Integer, ForeignKey("usuarios.id"), nullable=True),
              Column("alt_1", DOUBLE_PRECISION(2,18), nullable=False),
              Column("log_1", DOUBLE_PRECISION(2,18), nullable=False),
              Column("alt_2", DOUBLE_PRECISION(2,18), nullable=False),
              Column("log_2", DOUBLE_PRECISION(2,18), nullable=False),
              Column("created_at", TIMESTAMP, nullable=False, server_default=func.now()),
              Column("updated_at", TIMESTAMP, nullable=True),
              schema="translados"
)

meta_data.create_all(engine, checkfirst=True)
