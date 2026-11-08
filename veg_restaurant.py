import pandas as pd
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser


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


model1=ChatOpenAI(model="gpt-6")
parser = JsonOutputParser()



@app.get("/vrestaurant")
def getVegRestaurant(location:str):
    try:
        return get_vrestaurant(location)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

def get_vrestaurant(location):

    print("Collecting data")


    prompt=PromptTemplate(template="""You are an expert smart travel assistant.

    Analyze all the top Veg Restaurants and send the detailed response  in structured format with proper indentation.
    Return ONLY valid JSON.


    Return the response strictly as JSON array with the following topic with no sub fields or elements.Return data type should be string in JSON Format . Topic name should be exactly this.
    1.name
    2.category
    3.location
    4.menu_details
    5.timings
                            
                            

    Provide: 

                        
    all Top Veg Resaturants in the given location and its details.Its timings.
    Dont include any other information apart from the given info.
                        
                
                            
                        

    Data:
    {location}

    Give detailed but clean response.""", input_variables=["location"])

    chain=prompt|model1|parser
    vrest=chain.invoke({"location":location})

    #travel_advice is a list of dictionary
    #combined.to_csv(fr"C:\Users\techi\OneDrive\Desktop\AI\data\{location}\combined.csv", index=False)
    #travel=travel_advice.to_json(orient="records", indent=4)
    #json_string is a json formatted string

    #json_string=json.dumps(vrest,indent=4,ensure_ascii=False)
    #with open(fr"C:\Users\techi\OneDrive\Desktop\AI\data\{location}\Veg_Restaurant.json","w", encoding="utf-8") as f:
        #json.dump(vrest, f, indent=4, ensure_ascii=False)

    return vrest

