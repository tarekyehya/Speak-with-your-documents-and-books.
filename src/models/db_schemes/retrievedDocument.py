from pydantic import BaseModel

# the data retrieved from searching in VectorDB 
class RetrievedDocument(BaseModel):
    text: str
    score: float
    
    