from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer, BigInteger, Boolean, TIMESTAMP, DOUBLE_PRECISION
from sqlalchemy.sql.functions import func
from database.conection import engine, meta_data

datos_vehiculo = Table("datos_vehiculo", meta_data,
              Column("id", Integer, primary_key=True),
              Column("fk_per_ube_id", Integer, ForeignKey("perfil_uber.id"), nullable=False),
              Column("fk_id_tp", Integer, ForeignKey("tipo_transporte.id"), nullable=False),
              Column("created_at", TIMESTAMP, nullable=False, server_default=func.now()),
              Column("updated_at", TIMESTAMP, nullable=True),
              schema="uber"
)

meta_data.create_all(engine, checkfirst=True)
