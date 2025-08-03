from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Pydantic model for data validation
class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = None

# GET endpoint
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

# GET endpoint with path parameter
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "query": q}

# POST endpoint
@app.post("/items/")
def create_item(item: Item):
    return {"item": item}
