from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

base_timing = declarative_base()

class Timings(base_timing):
    __tablename__ = 'timings'
    timing_id=Column(Integer, primary_key=True, autoincrement="auto")
    store_id = Column(String)
    day = Column(Integer)
    start = Column(String)
    end = Column(String)