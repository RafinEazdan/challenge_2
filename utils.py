# utils.py

import re
from models import RecipeIngredient

def parse_recipe_text(recipe_text: str):
    # Example format:
    # Title: Chocolate Cake
    # Taste: Sweet
    # Reviews: 150
    # Cuisine Type: American
    # Preparation Time: 45
    # Ingredients:
    # - Flour: 2 cups
    # - Sugar: 1.5 cups
    # Instructions:
    # Mix ingredients and bake.

    recipe = {}
    lines = recipe_text.split('\n')
    ingredients = []
    instructions = []
    mode = None

    for line in lines:
        if line.startswith('Title:'):
            recipe['title'] = line.replace('Title:', '').strip()
        elif line.startswith('Taste:'):
            recipe['taste'] = line.replace('Taste:', '').strip()
        elif line.startswith('Reviews:'):
            try:
                recipe['reviews'] = int(line.replace('Reviews:', '').strip())
            except ValueError:
                recipe['reviews'] = 0
        elif line.startswith('Cuisine Type:'):
            recipe['cuisine_type'] = line.replace('Cuisine Type:', '').strip()
        elif line.startswith('Preparation Time:'):
            try:
                recipe['preparation_time'] = int(line.replace('Preparation Time:', '').strip())
            except ValueError:
                recipe['preparation_time'] = 0
        elif line.startswith('Ingredients:'):
            mode = 'ingredients'
        elif line.startswith('Instructions:'):
            mode = 'instructions'
        elif mode == 'ingredients' and line.startswith('-'):
            ing = re.findall(r'- (.*?): (\d+\.?\d*) (\w+)', line)
            if ing:
                ingredients.append(RecipeIngredient(
                    name=ing[0][0],
                    quantity=float(ing[0][1]),
                    unit=ing[0][2]
                ))
        elif mode == 'instructions':
            instructions.append(line.strip())

    recipe['ingredients'] = ingredients
    recipe['instructions'] = ' '.join(instructions)
    return recipe
