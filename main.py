from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float
from databases import Database
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "postgresql://qatestuser:qatestuserpassword@db/test_db"

database = Database(DATABASE_URL)
metadata = MetaData()

Base = declarative_base()

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    price = Column(Float)

# Pydantic models for API interactions
class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

class ItemResponse(ItemCreate):
    id: int

engine = create_engine(DATABASE_URL)
metadata.create_all(engine)

app = FastAPI(
    title="API testing",
    description="This is an API for API and CI testing of a QA engineering position @ Stellar Blue.",
    version="1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # allows all methods
    allow_headers=["*"],  # allows all headers
)

@app.on_event("startup")
async def startup():
    await database.connect()

    # Use databases' connection for async operations
    async with database.transaction():
        # Create the table
        Base.metadata.create_all(bind=engine)

        # Delete all existing data from the table
        delete_query = Item.__table__.delete()
        await database.execute(delete_query)

        seed_data = []
        for i in range(20):
            seed_data.append(
                {"name": f"Item {i + 1}", "description": f"This is item {i+1}", "price": i},
            )
        query = Item.__table__.insert()
        await database.execute_many(query, values=seed_data)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/items/", response_model=List[ItemResponse], tags=["Items"])
async def read_items(skip: int = 0, limit: int = 10):
    query = Item.__table__.select().offset(skip).limit(limit)
    items = await database.fetch_all(query)
    return items

@app.get("/items/", response_model=List[ItemResponse], tags=["Items"])
async def read_items(skip: int = 0, limit: int = 10):
    query = Item.__table__.select().offset(skip).limit(limit)
    items = await database.fetch_all(query)
    return items

@app.post("/items/", response_model=ItemResponse, tags=["Items"])
async def create_item(item: ItemCreate):
    query = Item.__table__.insert().values(**item.dict())
    last_record_id = await database.execute(query)
    return {**item.dict(), "id": last_record_id}

@app.get("/items/{item_id}", response_model=ItemResponse, tags=["Items"])
async def read_item(item_id: int):
    query = Item.__table__.select().where(Item.id == item_id)
    item = await database.fetch_one(query)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.put("/items/{item_id}", response_model=ItemResponse, tags=["Items"])
async def update_item(item_id: int, item: ItemCreate):
    query = Item.__table__.update().where(Item.id == item_id).values(**item.dict())
    await database.execute(query)
    return {**item.dict(), "id": item_id}

@app.delete("/items/{item_id}", response_model=ItemResponse, tags=["Items"])
async def delete_item(item_id: int):
    query = Item.__table__.delete().where(Item.id == item_id)
    await database.execute(query)
    return {"id": item_id, "name": "", "description": "", "price": 0.0}  # Returning a dummy response after deletion


