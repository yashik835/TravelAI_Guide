import pandas as pd
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from pathlib import Path

from past_3mon_data import get_travel_data as get_past_travel_data


from dotenv import load_dotenv
import os
import json
from fastapi import FastAPI
load_dotenv()
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


model1=ChatOpenAI(model="gpt-6.1-terra")
parser = JsonOutputParser()


@app.get("/search")
def search_location(location:str):
    try:
        return get_travel_data(location)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.get("/pasttravel")
def get_pasttravel(location:str):
    try:
        return get_past_travel_data(location)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

def get_travel_data(location):

    print("Collecting data")
    

    BASE_DIR = Path(__file__).resolve().parent
    DATA_DIR = BASE_DIR / "data"
    
    temp_df = pd.read_csv(DATA_DIR / location / "temp_data.csv")
    #temp_df = pd.read_csv(fr"C:\Users\techi\OneDrive\Desktop\AI\data\{location}\temp_data.csv")
    temp_df=temp_df.drop(columns=['unique_id','index'])
    temp_df=temp_df.rename(columns={'NHITS':'temperature'})

    BASE_DIR = Path(__file__).resolve().parent
    DATA_DIR = BASE_DIR / "data"
    
    rainfall_df = pd.read_csv(DATA_DIR / location / "rainfall_data.csv")

    #rainfall_df = pd.read_csv(fr"C:\Users\techi\OneDrive\Desktop\AI\data\{location}\rainfall_data.csv")
    rainfall_df=rainfall_df.drop(columns=['unique_id','index','location'])
    rainfall_df= rainfall_df.rename(columns={"NHITS": "rainfall"})


    BASE_DIR = Path(__file__).resolve().parent
    DATA_DIR = BASE_DIR / "data"
    
    snowfall_df = pd.read_csv(DATA_DIR / location / "snowfall_data.csv")
    
    #snowfall_df = pd.read_csv(fr"C:\Users\techi\OneDrive\Desktop\AI\data\{location}\snowfall_data.csv")
    snowfall_df=snowfall_df.drop(columns=['unique_id','index','location'])
    snowfall_df=snowfall_df.rename(columns={'NHITS':'snowfall'})
    # Merge first two
    combined = pd.merge(temp_df, rainfall_df, on="ds", how="inner")

    # Merge the third
    combined = pd.merge(combined, snowfall_df, on="ds", how="inner")
    combined['ds'] = pd.to_datetime(combined['ds'])
    combined['month'] = combined['ds'].dt.month_name()
    BASE_DIR = Path(__file__).resolve().parent
    DATA_DIR = BASE_DIR / "data"
    
    combined.to_csv(DATA_DIR / location / "combined.csv")
    #combined.to_csv(fr"C:\Users\techi\OneDrive\Desktop\AI\data\{location}\combined.csv", index=False)


    travel_data=combined.to_json(orient="records", indent=4)



    prompt=PromptTemplate(template="""You are an expert smart travel assistant.

    Analyze the following environmental and weather data. Display each topic in structured format separately with proper indentation.
    Return ONLY valid JSON.

    Return a JSON array where each object contains the original weather fields(month, rainfall,temperature,snowfall, location) plus a new field called "Travel_advice" for each month .
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
    {travel_data}

    Give detailed but clean travel advice.""", input_variables=["travel_data"])

    chain=prompt|model1|parser
    travel_advice=chain.invoke({"travel_data":travel_data})

    #travel_advice is a list of dictionary
    #combined.to_csv(fr"C:\Users\techi\OneDrive\Desktop\AI\data\{location}\combined.csv", index=False)
    #travel=travel_advice.to_json(orient="records", indent=4)
    #json_string is a json formatted string

    json_string=json.dumps(travel_advice,indent=4,ensure_ascii=False)
    #with open(fr"C:\Users\techi\OneDrive\Desktop\AI\data\{location}\travel_advice.json","w", encoding="utf-8") as f:
        #json.dump(travel_advice, f, indent=4, ensure_ascii=False)

    return json_string

