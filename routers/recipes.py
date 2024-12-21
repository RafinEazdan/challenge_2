# routers/recipes.py (continued)

from fastapi import APIRouter, HTTPException, UploadFile, File
from models import Recipe, Ingredient
from pydantic import BaseModel
from typing import Optional, List
from utils import parse_recipe_text
from beanie import PydanticObjectId
import pytesseract
from typing import Optional

from PIL import Image

import io

router = APIRouter(prefix="/recipes", tags=["Recipes"])


# Pydantic Schemas
class RecipeIngredientCreate(BaseModel):
    name: str
    quantity: float
    unit: str


class RecipeCreate(BaseModel):
    recipe_text: Optional[str] = None


class RecipeResponse(BaseModel):
    id: PydanticObjectId
    title: str
    taste: str
    reviews: int
    cuisine_type: str
    preparation_time: int
    instructions: str
    ingredients: List[RecipeIngredientCreate]
    image_path: Optional[str] = None

    class Config:
        orm_mode = True


# Utility function to append recipe text to file
async def append_recipe_to_file(recipe_text: str, file_path='my_fav_recipes.txt'):
    async with aiofiles.open(file_path, 'a') as f:
        await f.write(recipe_text + '\n\n')  # Separate recipes by two newlines


import aiofiles


@router.post("/text/", response_model=RecipeResponse)
async def add_recipe_text(recipe: RecipeCreate):
    if not recipe.recipe_text:
        raise HTTPException(status_code=400, detail="No recipe text provided")
    parsed = parse_recipe_text(recipe.recipe_text)

    # Check if recipe exists
    existing = await Recipe.find_one(Recipe.title == parsed['title'])
    if existing:
        raise HTTPException(status_code=400, detail="Recipe already exists")

    # Create Recipe
    recipe_obj = Recipe(
        title=parsed['title'],
        taste=parsed['taste'],
        reviews=parsed.get('reviews', 0),
        cuisine_type=parsed['cuisine_type'],
        preparation_time=parsed['preparation_time'],
        instructions=parsed['instructions'],
        ingredients=[ing.dict() for ing in parsed['ingredients']]
    )
    await recipe_obj.insert()

    # Optionally, handle ingredients in the Ingredients collection
    for ing in parsed['ingredients']:
        existing_ing = await Ingredient.find_one(Ingredient.name == ing.name)
        if not existing_ing:
            new_ing = Ingredient(name=ing.name, quantity=0, unit=ing.unit)
            await new_ing.insert()

    # Append to file
    await append_recipe_to_file(recipe.recipe_text)

    return recipe_obj


@router.post("/image/", response_model=RecipeResponse)
async def add_recipe_image(file: UploadFile = File(...)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Invalid image file")

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        recipe_text = pytesseract.image_to_string(image)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to process image") from e

    parsed = parse_recipe_text(recipe_text)

    # Check if recipe exists
    existing = await Recipe.find_one(Recipe.title == parsed['title'])
    if existing:
        raise HTTPException(status_code=400, detail="Recipe already exists")

    # Create Recipe
    recipe_obj = Recipe(
        title=parsed['title'],
        taste=parsed['taste'],
        reviews=parsed.get('reviews', 0),
        cuisine_type=parsed['cuisine_type'],
        preparation_time=parsed['preparation_time'],
        instructions=parsed['instructions'],
        ingredients=[ing.dict() for ing in parsed['ingredients']],
        image_path=f"images/{file.filename}"  # Adjust as needed
    )
    await recipe_obj.insert()

    # Optionally, handle ingredients in the Ingredients collection
    for ing in parsed['ingredients']:
        existing_ing = await Ingredient.find_one(Ingredient.name == ing.name)
        if not existing_ing:
            new_ing = Ingredient(name=ing.name, quantity=0, unit=ing.unit)
            await new_ing.insert()

    # Save image to disk (optional)
    async with aiofiles.open(f"images/{file.filename}", 'wb') as out_file:
        await out_file.write(contents)

    # Append to file
    await append_recipe_to_file(recipe_text)

    return recipe_obj
