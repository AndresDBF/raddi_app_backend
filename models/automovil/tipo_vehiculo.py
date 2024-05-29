from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer, TIMESTAMP
from sqlalchemy.sql.functions import func
from database.conection import engine, meta_data

tipo_vehiculo = Table("tipo_vehiculo", meta_data,
              Column("id", Integer, primary_key=True),
              Column("tip_veh", String(191), nullable=False),
              Column("nom_tip_veh", String(30), nullable=False),
              schema="automovil"
)

meta_data.create_all(engine, checkfirst=True)
