from sqlalchemy import Column, Table, TIMESTAMP
from sqlalchemy.sql.sqltypes import String, Integer
from sqlalchemy.sql import func
from sqlalchemy.sql.functions import func
from database.conection import engine, meta_data

categorias = Table("categorias", meta_data,
              Column("id", Integer, primary_key=True),
              Column("nom_cat", String(30), nullable=False),
              Column("created_at", TIMESTAMP, nullable=False, server_default=func.now()),
              schema="general"
)

meta_data.create_all(engine, checkfirst=True)