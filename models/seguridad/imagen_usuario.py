from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer, TIMESTAMP
from sqlalchemy.sql.functions import func
from database.conection import engine, meta_data

imagen_usuario = Table("imagen_usuario", meta_data,
              Column("id", Integer, primary_key=True),
              Column("fk_use_id", Integer, ForeignKey("usuarios.id"), nullable=False),
              Column("img_ori", String(191), nullable=False),
              Column("img_enc", String(191), nullable=False, unique=True),
              Column("created_at", TIMESTAMP, nullable=False, server_default=func.now()),
              Column("updated_at", TIMESTAMP, nullable=True),
              schema="seguridad"
)

meta_data.create_all(engine, checkfirst=True)
