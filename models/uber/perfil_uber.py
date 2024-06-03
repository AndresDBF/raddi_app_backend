from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer, BigInteger, Boolean, TIMESTAMP
from sqlalchemy.sql.functions import func
from database.conection import engine, meta_data

perfil_uber = Table("perfil_uber", meta_data,
              Column("id", Integer, primary_key=True),
              Column("fk_use_id", BigInteger, ForeignKey("usuarios.id"), nullable=False),
              Column("fk_tv_id", BigInteger, ForeignKey("tipo_vehiculo.id"), nullable=False),
              Column("fk_mod_veh_id", BigInteger, ForeignKey("modelo_vehiculo.id"), nullable=False),
              Column("pla_veh", String(8), nullable=False),
              Column("ano_veh", String(4), nullable=False),
              Column("air_aco", Boolean, nullable=False),
              Column("col_veh", String(30), nullable=False),
              Column("con_per", Boolean, nullable=False),
              Column("created_at", TIMESTAMP, nullable=False, server_default=func.now()),
              Column("updated_at", TIMESTAMP, nullable=True),
              schema="uber"
)

meta_data.create_all(engine, checkfirst=True)
