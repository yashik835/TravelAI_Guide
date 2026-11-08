from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from main import get_travel_data
from past_3mon_data import get_travel_data as get_past_travel_data
from sightseeing import get_sightseeing
from veg_restaurant import get_vrestaurant
from non_veg_restaurant import get_nvrestaurant
from about import get_about
from currmonth import get_currmonth

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Travel Intelligent Guide")

# The website and API are served from the same origin.
# CORS is kept permissive for now; it can be restricted later to your domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/images", StaticFiles(directory=BASE_DIR / "images"), name="images")


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "index.html")


@app.get("/travel.html")
def travel_page():
    return FileResponse(BASE_DIR / "travel.html")


@app.get("/search")
def search(location: str):
    return get_travel_data(location)


@app.get("/pasttravel")
def pasttravel(location: str):
    return get_past_travel_data(location)


@app.get("/sightseeing")
def sightseeing(location: str):
    return get_sightseeing(location)


@app.get("/vrestaurant")
def vrestaurant(location: str):
    return get_vrestaurant(location)


@app.get("/nvrestaurant")
def nvrestaurant(location: str):
    return get_nvrestaurant(location)


@app.get("/about")
def about(location: str):
    return get_about(location)


@app.get("/currmonth")
def currmonth(location: str):
    return get_currmonth(location)
