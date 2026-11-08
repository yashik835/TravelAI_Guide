import json
from datetime import date
from fastapi import FastAPI
from main import get_travel_data

app = FastAPI()


def get_currmonth(location: str):
    """
    The original currmonth.py was not included in the uploaded project.
    This AWS-ready implementation reuses the existing /search forecast
    and returns the entry matching the current calendar month.
    """
    result = get_travel_data(location)

    if isinstance(result, str):
        result = json.loads(result)

    current_month = date.today().strftime("%B")
    return [item for item in result if item.get("month") == current_month]


@app.get("/currmonth")
def currmonth(location: str):
    try:
        return get_currmonth(location)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
