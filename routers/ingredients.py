# routers/ingredients.py

from fastapi import APIRouter, HTTPException
from models import Ingredient
from pydantic import BaseModel
from typing import List
from beanie import PydanticObjectId
from typing import Optional

router = APIRouter(prefix="/ingredients", tags=["Ingredients"])

# Pydantic Schemas
class IngredientCreate(BaseModel):
    name: str
    quantity: float
    unit: str

class IngredientUpdate(BaseModel):
    quantity: Optional[float] = None
    unit: Optional[str] = None

@router.post("/", response_model=Ingredient)
async def create_ingredient(ingredient: IngredientCreate):
    existing = await Ingredient.find_one(Ingredient.name == ingredient.name)
    if existing:
        raise HTTPException(status_code=400, detail="Ingredient already exists")
    ing = Ingredient(**ingredient.dict())
    await ing.insert()
    return ing

@router.put("/{ingredient_id}", response_model=Ingredient)
async def update_ingredient(ingredient_id: PydanticObjectId, ingredient: IngredientUpdate):
    ing = await Ingredient.get(ingredient_id)
    if not ing:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    update_data = ingredient.dict(exclude_unset=True)
    await ing.set(update_data)
    return ing

@router.get("/", response_model=List[Ingredient])
async def get_ingredients():
    ingredients = await Ingredient.find_all().to_list()
    return ingredients

@router.delete("/{ingredient_id}")
async def delete_ingredient(ingredient_id: PydanticObjectId):
    ing = await Ingredient.get(ingredient_id)
    if not ing:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    await ing.delete()
    return {"detail": "Ingredient deleted"}
