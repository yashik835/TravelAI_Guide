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
location='Colombo';


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


model1=ChatOpenAI(model="gpt-6")
parser = JsonOutputParser()




print("API Key:", os.getenv("OPENAI_API_KEY"))
print("Collecting data")
@app.get("/sightseeing")
def getSightseeing(location:str):
    try:
        return get_sightseeing(location)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

def get_sightseeing(location):

    prompt=PromptTemplate(template="""You are an expert smart travel assistant.

    Analyze the locations top sightseeing and send the detailed response  in structured format with proper indentation.
    Return ONLY valid JSON.


    Return the response strictly as JSON array with the following topic with no sub fields or elements.Return data type should be string in JSON Format . Topic name should be exactly this.
    1.name
    2.category
    3.location
    4.details
    5.timings
                            

    Provide: 

                        
    Top sightseeing in the given location and its details.Its timings.
    Dont include any other information apart from sightseeing.
                        
                
                            
                        

    Data:
    {location}

    Give detailed but clean response.""", input_variables=["location"])

    chain=prompt|model1|parser
    sightseeing=chain.invoke({"location":location})

    #travel_advice is a list of dictionary
    #combined.to_csv(fr"C:\Users\techi\OneDrive\Desktop\AI\data\{location}\combined.csv", index=False)
    #travel=travel_advice.to_json(orient="records", indent=4)
    #json_string is a json formatted string

    #json_string=json.dumps(sightseeing,indent=4,ensure_ascii=False)
    
    #with open(fr"C:\Users\techi\OneDrive\Desktop\AI\data\{location}\sightseeing.json","w", encoding="utf-8") as f:
        
        #json.dump(sightseeing, f, indent=4, ensure_ascii=False)

    
    return sightseeing

