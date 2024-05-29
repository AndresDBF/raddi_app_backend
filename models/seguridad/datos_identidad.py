from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer, TIMESTAMP, BigInteger
from sqlalchemy.sql.functions import func
from database.conection import engine, meta_data

datos_identidad = Table("datos_identidad", meta_data,
              Column("id", Integer, primary_key=True),
              Column("fk_use_id", BigInteger, ForeignKey("usuarios.id"), nullable=False),
              Column("img_sel_ori", String(191), nullable=False),
              Column("img_sel_enc", String(191), nullable=False, unique=True),
              Column("img_ced_ori", String(191), nullable=False),
              Column("img_ced_enc", String(191), nullable=False, unique=True),
              Column("created_at", TIMESTAMP, nullable=True, server_default=func.now()),
              schema="seguridad"
)

meta_data.create_all(engine, checkfirst=True)
