from pydantic import BaseModel, Field
from datetime import datetime

class UserRequest(BaseModel):
    message : str = Field(min_length=1, description="User Request")
    datetime: datetime
    