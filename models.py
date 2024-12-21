# models.py

from typing import List, Optional
from beanie import Document, init_beanie
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from pymongo import MongoClient

class Ingredient(Document):
    name: str
    quantity: float
    unit: str

    class Settings:
        name = "ingredients"  # Collection name

class RecipeIngredient(BaseModel):
    name: str
    quantity: float
    unit: str

class Recipe(Document):
    title: str
    taste: str
    reviews: int = 0
    cuisine_type: str
    preparation_time: int  # in minutes
    instructions: str
    ingredients: List[RecipeIngredient]
    image_path: Optional[str] = None

    class Settings:
        name = "recipes"  # Collection name

# Initialize Beanie (to be called in main.py)
async def init():
    client = AsyncIOMotorClient("mongodb+srv://eazdanrafin:rAcA2YU66mXRqxEO@fastapilearning.tuidz.mongodb.net/")  # Update with your MongoDB URI
    await init_beanie(database=client.kitchen_buddy, document_models=[Ingredient, Recipe])
