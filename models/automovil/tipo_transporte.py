from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer, TIMESTAMP
from sqlalchemy.sql.functions import func
from database.conection import engine, meta_data

tipo_transporte = Table("tipo_transporte", meta_data,
              Column("id", Integer, primary_key=True),
              Column("fk_tv_id", String(191), nullable=False),
              Column("nom_veh", String(30), nullable=False),
              Column("num_pas", String(30), nullable=False),
              Column("val_mas", String(30), nullable=False),
              Column("created_at", TIMESTAMP, nullable=False, server_default=func.now()),
              schema="automovil"
)

meta_data.create_all(engine, checkfirst=True)
