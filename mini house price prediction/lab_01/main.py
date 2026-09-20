from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    name: str
    price: float
    in_stock: bool = True

class ItemUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    in_stock: bool | None = None

class ItemPublic(BaseModel):
    id: int
    name: str
    price: float
    in_stock: bool = True

class ItemListResponse(BaseModel):
    items: list[ItemPublic]
    total: int
    skip: int
    limit: int

class HousePriceRequest(BaseModel):
    area_sqm: float = Field(..., gt=0)
    bedrooms: int = Field(..., ge=0)
    distance_to_center_km: float = Field(..., ge=0)

class HousePricePrediction(BaseModel):
    predicted_price: float
    currency: str = "VND"


_items: list[ItemPublic] = []
_next_id: int = 1

app = FastAPI()

app.mount("/static", StaticFiles(directory="../frontend"), name="static")

def _find(item_id: int) -> ItemPublic | None:
    for it in _items:
        if it.id == item_id:
            return it
    return None

# @app.get("/")
# def root():
#     return {"message": "Hello World"}

# @app.get("/items/me")
# def read_me():
#     return {"message": "Welcome me"}

@app.get("/items/{item_id}", response_model=ItemPublic)
def read_item(item_id: int):
    item = _find(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")
    return item

@app.get("/items", response_model=ItemListResponse)
def read_items(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of items to return"),
    min_price: float | None = Query(None, description="Minimum price filter"),
    max_price: float | None = Query(None, description="Maximum price filter"),
    q: str | None = Query(None, min_length=2, description="Query string for searching items"),
    sort_by: str = Query("id", pattern="^(id|name|price)$", description="Field to sort by"),
    order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order: asc or desc")
):
    results = _items

    if q:
        results = [it for it in results if q.lower() in it.name.lower()]

    if min_price is not None:
        results = [it for it in results if it.price >= min_price]
    if max_price is not None:
        results = [it for it in results if it.price <= max_price]

    total = len(results)

    reverse = (order == "desc")
    if sort_by == "name":
        results = sorted(results, key=lambda x: x.name.lower(), reverse=reverse)
    elif sort_by == "price":
        results = sorted(results, key=lambda x: x.price, reverse=reverse)
    else:
        results = sorted(results, key=lambda x: x.id, reverse=reverse)

    sliced = results[skip : skip + limit]

    return {
        "items": sliced,
        "total": total,
        "skip": skip,
        "limit": limit
    }

# CREATE AN ITEM
@app.post("/items", response_model=ItemPublic, status_code=201)
def create_item(data: ItemCreate):
    global _next_id

    if any(it.name.lower() == data.name.lower() for it in _items):
        raise HTTPException(status_code=409, detail="Item with this name already exists")

    new_item = ItemPublic(
        id=_next_id,
        name=data.name,
        price=data.price,
        in_stock=data.in_stock
    )
    _items.append(new_item)
    _next_id += 1
    return new_item

# UPDATE AN ITEM
@app.put("/items/{item_id}", response_model=ItemPublic)
def update_item(item_id: int, data: ItemCreate):
    item = _find(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")
    
    if data.name.lower() != item.name.lower():
        if any(it.id != item_id and it.name.lower() == data.name.lower() for it in _items):
            raise HTTPException(status_code=409, detail="Item with this name already exists")

    updated_item = ItemPublic(
        id=item_id,
        name=data.name,
        price=data.price,
        in_stock=data.in_stock
    )
    index = _items.index(item)
    _items[index] = updated_item
    return updated_item

# PATCH UPDATE
@app.patch("/items/{item_id}", response_model=ItemPublic)
def patch_item(item_id: int, data: ItemUpdate):
    item = _find(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")

    update_data = data.model_dump(exclude_unset=True)

    if "name" in update_data and update_data["name"] is not None:
        new_name = update_data["name"]
        if new_name.lower() != item.name.lower():
            if any(it.id != item_id and it.name.lower() == new_name.lower() for it in _items):
                raise HTTPException(status_code=409, detail="Item with this name already exists")

    updated_item = item.model_copy(update=update_data)
    index = _items.index(item)
    _items[index] = updated_item
    return updated_item

# DELETE AN ITEM
@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    item = _find(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")
    
    _items.remove(item)
    return None

# Toy Prediction Endpoint
@app.post("/predict/house-price", response_model=HousePricePrediction)
def predict_house_price(data: HousePriceRequest):
    price = data.area_sqm * 15_000_000 - data.distance_to_center_km * 5_000_000 + data.bedrooms * 20_000_000
    return HousePricePrediction(predicted_price=price, currency="VND")