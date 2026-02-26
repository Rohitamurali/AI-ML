from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, conlist
from typing import List, Optional
import os
import pandas as pd
from FastAPI_Backend.model import recommend, output_recommended_recipes

# Load dataset safely
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # diet-plan folder
csv_path = os.path.join(BASE_DIR, "Data", "dataset.csv")
dataset = pd.read_csv(csv_path)

# FastAPI app setup
app = FastAPI()
templates = Jinja2Templates(directory="Frontend/templates")
app.mount("/static", StaticFiles(directory="Frontend/static"), name="static")

# Pydantic models
class Params(BaseModel):
    n_neighbors: int = 5
    return_distance: bool = False

class PredictionIn(BaseModel):
    nutrition_input: conlist(float, min_items=9, max_items=9)
    ingredients: list[str] = []
    params: Optional[Params]

class Recipe(BaseModel):
    Name: str
    CookTime: str
    PrepTime: str
    TotalTime: str
    RecipeIngredientParts: list[str]
    Calories: float
    FatContent: float
    SaturatedFatContent: float
    CholesterolContent: float
    SodiumContent: float
    CarbohydrateContent: float
    FiberContent: float
    SugarContent: float
    ProteinContent: float
    RecipeInstructions: list[str]

class PredictionOut(BaseModel):
    output: Optional[List[Recipe]] = None

# Routes
@app.get("/")
def home():
    return {"health_check": "OK"}

@app.post("/predict/", response_model=PredictionOut)
def update_item(prediction_input: PredictionIn):
    params_dict = prediction_input.params.dict() if prediction_input.params else {}
    recommendation_dataframe = recommend(dataset, prediction_input.nutrition_input, prediction_input.ingredients, params_dict)
    output = output_recommended_recipes(recommendation_dataframe)
    return {"output": output if output else None}