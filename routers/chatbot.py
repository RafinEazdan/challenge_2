# routers/chatbot.py

from fastapi import APIRouter, HTTPException
from models import Ingredient, Recipe
from typing import List
import httpx
import os
from config import GEMINI_API_KEY

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

# Define Gemini API endpoint (hypothetical)
GEMINI_API_ENDPOINT = "https://api.gemini.ai/v1/completions"

@router.post("/", response_model=dict)
async def chatbot_interaction(user_message: str):
    # Fetch available ingredients
    ingredients = await Ingredient.find(Ingredient.quantity > 0).to_list()
    ingredient_list = ', '.join([ing.name for ing in ingredients])

    # Fetch recipes
    recipes = await Recipe.find_all().to_list()
    recipe_text = "\n\n".join([
        f"Title: {r.title}\nTaste: {r.taste}\nCuisine Type: {r.cuisine_type}\nIngredients: {', '.join([ing.name for ing in r.ingredients])}"
        for r in recipes
    ])

    # Prepare the prompt
    prompt = f"""
    You are a helpful cooking assistant.
    Available ingredients at home: {ingredient_list}.
    Here are my favorite recipes:

    {recipe_text}

    User: {user_message}
    Assistant:
    """

    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gemini-1.0",  # Replace with the actual model name
        "prompt": prompt,
        "max_tokens": 150,
        "temperature": 0.7,
        "n": 1,
        "stop": ["User:", "Assistant:"]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(GEMINI_API_ENDPOINT, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            answer = data['choices'][0]['text'].strip()
            return {"response": answer}
    except httpx.HTTPStatusError as http_err:
        raise HTTPException(status_code=response.status_code, detail=str(http_err))
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))
