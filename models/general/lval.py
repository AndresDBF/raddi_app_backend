from sqlalchemy import Column, Table
from sqlalchemy.sql.sqltypes import String, Integer
from sqlalchemy.sql.functions import func
from database.conection import engine, meta_data

lval = Table("lval", meta_data,
              Column("id", Integer, primary_key=True),
              Column("tip_val", String(6), nullable=False),
              Column("des_val", String(80), nullable=False),
              schema="general"
)

meta_data.create_all(engine, checkfirst=True)