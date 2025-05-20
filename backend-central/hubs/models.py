# dashboard/models.py
from pydantic import BaseModel, constr

 
class HubCreateRequest(BaseModel):
    name: constr(min_length=1, max_length=50)

    class Config:
        # Allow extra fields that aren't explicitly listed in the model
        # for cases where the request includes additional data
        extra = "forbid"

