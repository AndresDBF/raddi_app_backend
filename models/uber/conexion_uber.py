from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer, BigInteger, Boolean, TIMESTAMP, DOUBLE_PRECISION
from sqlalchemy.sql.functions import func
from database.conection import engine, meta_data

conexion_uber = Table("conexion_uber", meta_data,
              Column("id", Integer, primary_key=True),
              Column("fk_per_ube_id", Integer, ForeignKey("perfil_uber.id"), nullable=False),
              Column("con_ube", Boolean, nullable=False),
              Column("cor_alt", DOUBLE_PRECISION, nullable=False),
              Column("cor_lon",DOUBLE_PRECISION, nullable=False),
              Column("created_at", TIMESTAMP, nullable=False, server_default=func.now()),
              Column("updated_at", TIMESTAMP, nullable=True),
              schema="uber"
)

meta_data.create_all(engine, checkfirst=True)
