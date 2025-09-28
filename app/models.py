from sqlalchemy import Column, Integer, String, Text
from .database import Base
import json

class Fruit(Base):
    __tablename__ = "fruits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    color = Column(String(30))
    description = Column(Text)
    embedding = Column(Text, nullable=True)  # store as JSON string

    def set_embedding(self, vec):
        self.embedding = json.dumps(vec)

    def get_embedding(self):
        return json.loads(self.embedding) if self.embedding else None

