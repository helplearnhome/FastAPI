from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from deta import Deta

deta = Deta("c0d650br_vmCwwEVhJZpUvTmvWimS48YEAYcoDcA8")

db = deta.Base("bus_details")

app = FastAPI()

fake_db = []

class BusDetails(BaseModel):
    vehicle_id: int
    trip: str
    front_door_entry: int
    front_door_exit: int
    back_door_entry: int
    back_door_exit: int
    trip_count: int
    distress_count: int

class UpdatedBusDetails(BaseModel):
    trip: str = None
    front_door_entry: int = None
    front_door_exit: int = None
    back_door_entry: int = None
    back_door_exit: int = None
    trip_count: int = None
    distress_count: int = None

@app.get("/")
async def read_root():
    return {"greetings": "Welcome to the Bus Tracking API!"}


@app.get("/busdetails")
async def get_bus_details():
    return next(db.fetch())

@app.get("/busdetails/{vehicle_id}")
async def get_bus_detail_by_no(vehicle_id: int):
    item = next(db.fetch({"vehicle_id":vehicle_id}))
    #we can use try method also to handle errors eg:
    # try:
    #     db.delete(1234)
    # except:
    #     return {"error":"delete error"}
    if item:
        return item
    else:
        raise HTTPException(status_code=404, detail="Vehicle ID not found")

@app.post("/busdetails/")
async def add_bus_details(bus_details: BusDetails):
    current_object_vehicle_id = bus_details.dict()["vehicle_id"]
    item = next(db.fetch({"vehicle_id":current_object_vehicle_id}))
    if item:
        raise HTTPException(status_code=409, detail="Bus with same vehicle_id exist")
    else:
        db.put(bus_details.dict())
        return next(db.fetch())[-1]

@app.delete("/busdetails/{vehicle_id}")
async def delete_bus_details(vehicle_id: int):
    item = next(db.fetch({"vehicle_id":vehicle_id}))
    if item:
        db.delete(item[0]["key"])
        return {"task":"Deleted Successfully"}
    else:
        raise HTTPException(status_code=404, detail="Vehicle ID not found")

@app.put("/busdetails/{vehicle_id}")
async def update_bus_details(vehicle_id: int, updated_bus_details: UpdatedBusDetails):
    item = next(db.fetch({"vehicle_id":vehicle_id}))
    item_key = item[0]["key"]
    updated_dictionary_of_bus_details = {k:v for k,v in updated_bus_details.dict().items() if (v is not None)}
    db.update(updated_dictionary_of_bus_details,item_key)
    return db.get(item_key)