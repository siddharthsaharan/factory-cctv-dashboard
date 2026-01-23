from pydantic import BaseModel
from datetime import datetime

class EventSchema(BaseModel):
    timestamp: datetime
    worker_id: str
    workstation_id: str
    event_type: str
    confidence: float
    count: int
