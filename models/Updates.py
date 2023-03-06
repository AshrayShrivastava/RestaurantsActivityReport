from sqlalchemy import Column, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

base_update = declarative_base()

class Update(base_update):
    __tablename__ = 'updates'
    store_id = Column(String, primary_key=True)
    timestamp_utc = Column(TIMESTAMP(timezone=True), primary_key=True)
    status = Column(String)