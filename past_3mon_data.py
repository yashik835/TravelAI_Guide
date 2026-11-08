

import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import calendar
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

import pandas as  pd
import numpy as np
import requests
from geopy.geocoders import Nominatim
from datetime import date

from langchain_core.output_parsers import JsonOutputParser


app= FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model1=ChatOpenAI(model="gpt-6")
parser = JsonOutputParser()

@app.get("/pasttravel")
def get_pasttravel(location:str):
    try:
        return get_travel_data(location)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
    
def get_location(city):

    geolocator= Nominatim(user_agent="weather_app")

    location= geolocator.geocode(city)

    if location is None:
        raise Exception("Location not found")
    
    return location.latitude, location.longitude
def get_travel_data(location):
    city = location

    latitude, longitude = get_location(city)


    #download old data

    current_date=date.today()

    start_month=current_date.month-3
    end_month= start_month+2
    year= current_date.year



    tot_days_end_month= calendar.monthrange(year,end_month)[1]


    start_date=datetime.strptime(f"01-{start_month}-{year}",  "%d-%m-%Y").date()

    end_date=datetime.strptime(f"{tot_days_end_month}-{end_month}-{year}", "%d-%m-%Y").date()







    url = "https://archive-api.open-meteo.com/v1/archive"

    params={
        "latitude": latitude,
        "longitude": longitude,
        "start_date":start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "daily": [
            "temperature_2m_mean",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "snowfall_sum"
        ],
        "timezone": "auto"
    }


    response= requests.get(url, params=params)

    data=response.json()
    daily=data["daily"]
    weather = pd.DataFrame({
        "date": data["daily"]["time"],
        "temp_mean": data["daily"]["temperature_2m_mean"],
        "temp_max": data["daily"]["temperature_2m_max"],
        "temp_min": data["daily"]["temperature_2m_min"],
        "rainfall": data["daily"]["precipitation_sum"],
        "snowfall": data["daily"]["snowfall_sum"]
    })
    weather["date"] = pd.to_datetime(weather["date"])
    monthly = (
        weather
        .set_index("date")
        .resample("ME")
        .agg({
            "temp_mean": "mean",
            "temp_max": "mean",
            "temp_min": "mean",
            "rainfall": "sum",
            "snowfall": "sum"
        })
        .reset_index()
    )

    def check_snow(snowfall):
        if snowfall>0 and snowfall<1:
            return "No snow"
        elif snowfall >=1 and snowfall<15:
            return "Light snow"
        elif snowfall>=15 and snowfall<50:
            return "Moderate snow"
        elif snowfall>=50 and snowfall<100:
            return "Heavy Snow"
        elif snowfall>=100 :
            return "Extremely Heavy Snow"
        else:   
            return "Invalid data"


    def check_rain(precipitation):
    
        if precipitation>=0 and precipitation<50:
            return "Dry"
        elif precipitation>=50 and precipitation<100:
            return "Light Rain"
        elif precipitation>=100 and precipitation<200:
            return "Moderate Rain"
        elif precipitation>=200 and precipitation<250:
            return "Heavy Rain"
        elif precipitation>=250:
            return "Extremely Heavy Rain"
        else:
            return "Invalid data"

    monthly["temp_mean"]=monthly["temp_mean"].round(2)
    monthly["temp_max"]=monthly["temp_max"].round(2)
    monthly["temp_min"]=monthly["temp_min"].round(2)


    monthly["snowfall_status"]=monthly["snowfall"].apply(check_snow)
    monthly["snowfall"]=monthly["snowfall"].round(2).astype(str) +"("+monthly["snowfall_status"]+")"
    monthly["rainfall_status"]=monthly["rainfall"].apply(check_rain)
    monthly["rainfall"]=monthly["rainfall"].round(2).astype(str) +"("+monthly["rainfall_status"]+")"
    monthly = monthly.drop(columns=["rainfall_status"])
    monthly = monthly.drop(columns=["snowfall_status"])
    monthly["location"]=city
    
    monthly=monthly.to_json(orient="records", indent=4)

    prompt=PromptTemplate(template="""You are an expert smart travel assistant.

        Analyze the following environmental and weather data. Display each topic in structured format separately with proper indentation.
        Return ONLY valid JSON array.

        Return the response strictly as JSON array where each object contains the original weather fields(month, location,rainfall,temperature_mean,snowfall) plus a new field called "Travel_advice" for each month .
        Return travel advice with exaclty same topic name given inside bracket below. give proper advice with all the fields .
        Return all fields value in string type only.
        Provide: 

        1. Whether travel is recommended.Give a proper recommendation(recommendation)  
        2. What to avoid in this weather or anything related to people or places.(avoid)
        3. Recommended clothing. Types of clothing to wear(clothing)   
        4. Health precautions.Give a detail health precaution based on location and data(health_precautions)
        5. Ideal travel timings.Best time to visit in that month.(ideal_travel_timings)
        6. Travel warnings if any.Related to weather, places etc.(travel_warnings)
    
                            
                            

        Data:
        {monthly}
        Return JSON array in string type.
        Give detailed but clean travel advice.""", input_variables=["monthly"])


    chain=prompt|model1|parser
    travel_advice=chain.invoke({"monthly":monthly})

    #travel_advice is a list of dictionary
    #combined.to_csv(fr"C:\Users\techi\OneDrive\Desktop\AI\data\{location}\combined.csv", index=False)
    #travel=travel_advice.to_json(orient="records", indent=4)
    #json_string is a json formatted string

#json_string=json.dumps(travel_advice,indent=4,ensure_ascii=False)
    #with open(fr"C:\Users\techi\OneDrive\Desktop\AI\data\{city}\travel_advice_past_3_months.json","w", encoding="utf-8") as f:
        #json.dump(travel_advice, f, indent=4, ensure_ascii=False)

    return travel_advice



