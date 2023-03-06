from sqlalchemy import Column, BigInteger, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

base_zone = declarative_base()

class Zones(base_zone):
    __tablename__ = 'zones'
    store_id = Column(String, primary_key=True)
    zone = Column(String)