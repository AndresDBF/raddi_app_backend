from sqlalchemy import Column, Table, TIMESTAMP
from sqlalchemy.sql.sqltypes import String, Integer, DateTime, CHAR, BigInteger, Boolean
from sqlalchemy.sql.functions import func
from database.conection import engine, meta_data

# Definir la tabla de usuarios
usuarios = Table("usuarios", meta_data,
              Column("id", Integer, primary_key=True),
              Column("use_nam", String(20), nullable=False, unique=True),
              Column("email", String(80), nullable=False, unique=True),
              Column("password", String(191), nullable=False),
              Column("nom_usu", String(80), nullable=False),
              Column("ape_usu", String(80), nullable=False),
              Column("gen_usu", CHAR(1), nullable=False),
              Column("tel_usu", String(30), nullable=False),
              Column("est_ema", Boolean, nullable=False),
              Column("created_at", TIMESTAMP, nullable=False, server_default=func.now()),
              Column("updated_at", TIMESTAMP, nullable=True),
              schema="seguridad"
)

meta_data.create_all(engine, checkfirst=True)
