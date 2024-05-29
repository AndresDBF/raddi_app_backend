from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer, TIMESTAMP, CHAR
from sqlalchemy.sql.functions import func
from database.conection import engine, meta_data

marca_vehiculo = Table("marca_vehiculo", meta_data,
              Column("id", Integer, primary_key=True),
              Column("mar_veh", String(40), nullable=False),
              Column("est_mar", CHAR(1) , nullable=False),
              schema="automovil"
)

meta_data.create_all(engine, checkfirst=True)
