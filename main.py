from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="Mini House-Price Prediction API")

# Task 1: Prediction function
def predict_price(area: float, bedrooms: int, location: str) -> float:
    base_price = 500_000_000.0
    area_cost = 15_000_000.0 * area
    bedroom_cost = 50_000_000.0 * bedrooms
    total = base_price + area_cost + bedroom_cost
    
    loc = location.strip().lower()
    if loc == "hanoi":
        total *= 1.3
    elif loc == "hcmc":
        total *= 1.25
        
    return float(round(total, -6))


# Task 2: Expose GET /predict endpoint
@app.get("/predict")
def predict_get(area: float, bedrooms: int, location: str = "other"):
    price = predict_price(area=area, bedrooms=bedrooms, location=location)
    return {
        "area": area,
        "bedrooms": bedrooms,
        "location": location,
        "predicted_price": price
    }


# Task 6 (Bonus): POST /predict endpoint using Pydantic model
class HouseInput(BaseModel):
    area: float
    bedrooms: int
    location: str = "other"

@app.post("/predict")
def predict_post(house: HouseInput):
    price = predict_price(area=house.area, bedrooms=house.bedrooms, location=house.location)
    return {
        "area": house.area,
        "bedrooms": house.bedrooms,
        "location": house.location,
        "predicted_price": price
    }


# Task 4: Mount static files directory after route definitions
app.mount("/static", StaticFiles(directory="../frontend"), name="static")