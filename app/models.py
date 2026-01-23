from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base

class Worker(Base):
    __tablename__ = "workers"
    worker_id = Column(String, primary_key=True)
    name = Column(String)

class Workstation(Base):
    __tablename__ = "workstations"
    station_id = Column(String, primary_key=True)
    name = Column(String)

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    worker_id = Column(String)
    workstation_id = Column(String)
    event_type = Column(String)
    confidence = Column(Float)
    count = Column(Integer)
