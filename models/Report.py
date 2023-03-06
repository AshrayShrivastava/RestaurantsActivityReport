from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

base_report = declarative_base()

class Report(base_report):
    __tablename__ = 'report'
    report_id = Column(String, primary_key=True)
    store_id = Column(String, primary_key=True)
    uptime_last_hour = Column(String)
    uptime_last_day = Column(String)
    uptime_last_week = Column(String)
    downtime_last_hour = Column(String)
    downtime_last_day = Column(String)
    downtime_last_week = Column(String)
