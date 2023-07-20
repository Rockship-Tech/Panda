from pydantic import BaseModel, constr

class Job(BaseModel):
    title: constr(min_length=1)
    description: constr(min_length=1)
    responsibilities: constr(min_length=1)
    qualifications: constr(min_length=1)
    work_mode: constr(min_length=1)
    
    
class DisplayJob(BaseModel):
    id: int
    title: str
    description: str
    responsibilities: str
    qualifications: str
    work_mode: str
    
    class Config: 
        orm_mode = True
    