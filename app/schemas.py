from pydantic import BaseModel

class FruitBase(BaseModel):
    name: str
    color: str
    description: str

class FruitCreate(FruitBase):
    pass

class FruitResponse(FruitBase):
    id: int

    class Config:
        from_attributes = True
