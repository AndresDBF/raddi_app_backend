from sqlalchemy import Column, Table
from sqlalchemy.sql.sqltypes import String, Integer, CHAR
from database.conection import engine, meta_data

roles = Table("roles", meta_data,
              Column("id", Integer, primary_key=True),
              Column("cod_rol", CHAR(1), nullable=False),
              Column("nom_rol", String(30), nullable=False),
              schema="seguridad"
)

meta_data.create_all(engine, checkfirst=True)