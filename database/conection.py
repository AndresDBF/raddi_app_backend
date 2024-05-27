from sqlalchemy import create_engine, MetaData

engine = create_engine("postgresql+psycopg2://postgres:1234@localhost:5432/raddiapp")

meta_data = MetaData()

