from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import json
import os

app = FastAPI(
    title="FastAPI REST API with JSON Storage",
    description="A REST API that stores items in a JSON file instead of memory.",
    version="1.0.0"
)

DATA_FILE = "items.json"


# Pydantic model

class Item(BaseModel):
    name: str = Field(..., example="Apple")
    description: Optional[str] = Field(None, example="Fresh red apple")
    price: float = Field(..., gt=0, example=0.5)


# Helper functions

def load_items() -> List[Item]:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            return [Item(**item) for item in data]
    return []

def save_items(items: List[Item]):
    with open(DATA_FILE, "w") as f:
        json.dump([item.dict() for item in items], f, indent=4)


# Routes

@app.get("/", summary="Root Endpoint")
def read_root():
    return {"message": "Welcome to the FastAPI REST API with JSON storage!"}

@app.post("/items/", response_model=Item, summary="Create a new item")
def create_item(item: Item):
    items = load_items()
    items.append(item)
    save_items(items)
    return item

@app.get("/items/", response_model=List[Item], summary="Get all items")
def get_all_items():
    return load_items()

@app.get("/items/{item_id}", response_model=Item, summary="Get an item by ID")
def get_item(item_id: int):
    items = load_items()
    if item_id < 0 or item_id >= len(items):
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]

@app.put("/items/{item_id}", response_model=Item, summary="Update an item by ID")
def update_item(item_id: int, updated_item: Item):
    items = load_items()
    if item_id < 0 or item_id >= len(items):
        raise HTTPException(status_code=404, detail="Item not found")
    items[item_id] = updated_item
    save_items(items)
    return updated_item

@app.delete("/items/{item_id}", summary="Delete an item by ID")
def delete_item(item_id: int):
    items = load_items()
    if item_id < 0 or item_id >= len(items):
        raise HTTPException(status_code=404, detail="Item not found")
    deleted = items.pop(item_id)
    save_items(items)
    return {"message": "Item deleted successfully", "item": deleted}
