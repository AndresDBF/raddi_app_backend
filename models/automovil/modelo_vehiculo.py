from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer, BigInteger, CHAR
from sqlalchemy.sql.functions import func
from database.conection import engine, meta_data

modelo_vehiculo = Table("modelo_vehiculo", meta_data,
              Column("id", Integer, primary_key=True),
              Column("fk_mv_id", BigInteger, ForeignKey("marca_vehiculo.id") , nullable=False),
              Column("mod_veh", String(100) , nullable=False),
              Column("est_mod_veh", CHAR(1) , nullable=False),
              schema="automovil"
)

meta_data.create_all(engine, checkfirst=True)
