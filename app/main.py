from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, database
from .embeddings import embed_text
import numpy as np

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Fruit Encyclopedia API 🍓")

# DB dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/fruits/", response_model=schemas.FruitResponse)
def create_fruit(fruit: schemas.FruitCreate, db: Session = Depends(get_db)):
    db_fruit = db.query(models.Fruit).filter(models.Fruit.name == fruit.name).first()
    if db_fruit:
        raise HTTPException(status_code=400, detail="Fruit already exists")

    db_fruit = models.Fruit(**fruit.dict())
    db_fruit.set_embedding(embed_text(fruit.name))  # embed the name

    db.add(db_fruit)
    db.commit()
    db.refresh(db_fruit)
    return db_fruit

@app.get("/fruits/", response_model=list[schemas.FruitResponse])
def get_fruits(db: Session = Depends(get_db)):
    return db.query(models.Fruit).all()

@app.get("/fruits/{fruit_id}", response_model=schemas.FruitResponse)
def get_fruit(fruit_id: int, db: Session = Depends(get_db)):
    fruit = db.query(models.Fruit).filter(models.Fruit.id == fruit_id).first()
    if not fruit:
        raise HTTPException(status_code=404, detail="Fruit not found")
    return fruit

@app.delete("/fruits/{fruit_id}")
def delete_fruit(fruit_id: int, db: Session = Depends(get_db)):
    fruit = db.query(models.Fruit).filter(models.Fruit.id == fruit_id).first()
    if not fruit:
        raise HTTPException(status_code=404, detail="Fruit not found")
    db.delete(fruit)
    db.commit()
    return {"message": f"Fruit with id {fruit_id} deleted."}

@app.get("/fruits/search/{query}", response_model=schemas.FruitResponse)
def search_fruit(query: str, db: Session = Depends(get_db)):
    fruits = db.query(models.Fruit).all()
    if not fruits:
        raise HTTPException(status_code=404, detail="No fruits in DB")

    # embed query
    query_vec = np.array(embed_text(query))

    # compute cosine similarity for each fruit
    best_match = None
    best_score = -1
    for fruit in fruits:
        vec = np.array(fruit.get_embedding())
        score = np.dot(query_vec, vec) / (np.linalg.norm(query_vec) * np.linalg.norm(vec))
        if score > best_score:
            best_score = score
            best_match = fruit

    return best_match
