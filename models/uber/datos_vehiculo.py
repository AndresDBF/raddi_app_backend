from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer, TIMESTAMP, BigInteger
from sqlalchemy.sql.functions import func
from database.conection import engine, meta_data

tipo_vehiculo = Table("tipo_vehiculo", meta_data,
              Column("id", Integer, primary_key=True),
              Column("fk_per_ube_id", BigInteger, ForeignKey("perfil_uber.id"), nullable=False),
              Column("arc_lic_ori", String(191), nullable=False),
              Column("arc_lic_enc", String(191), nullable=False),
              Column("arc_pro_ori", String(191), nullable=False),
              Column("arc_pro_enc", String(191), nullable=False),
              Column("arc_rcv_ori", String(191), nullable=False),
              Column("arc_rcv_enc", String(191), nullable=False),
              Column("img_fre_ori", String(191), nullable=False),
              Column("img_fre_enc", String(191), nullable=False),
              Column("img_lat_ori", String(191), nullable=False),
              Column("img_lat_enc", String(191), nullable=False),
              Column("created_at", TIMESTAMP, nullable=False, server_default=func.now()),
              Column("updated_at", TIMESTAMP, nullable=True),
              schema="uber",
              
)

meta_data.create_all(engine, checkfirst=True)
