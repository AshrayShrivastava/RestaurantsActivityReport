from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_string='postgresql+psycopg2://postgres:postgres@localhost:5432/LoopKitchen'

db = create_engine(db_string)

Session = sessionmaker(db)  
session = Session()