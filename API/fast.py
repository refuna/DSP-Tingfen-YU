# from signal import signal
# from fastapi import FastAPI, Query, UploadFile

from db import database
import pandas as pd
from pydantic import BaseModel
import uvicorn
from fastapi import FastAPI, UploadFile
import sys
from pathlib import Path

sys.path.append(str(Path.cwd()))
# sys.path

from houseprices.inference import make_predictions

# create an instance for the fastapi
app = FastAPI(
    title='HousePrice Prediction',
    version='1.0',
    description=''
)

# create a class for the user input
class HousePrcie(BaseModel):
    OverallQual: int
    GrLivArea: int
    GarageArea: float
    TotalBsmtSF: float
    Street: str
    LotShape: str


@app.get('/')
# home message for the API
@app.get("/home")
async def read_home():
    return {"message": "Thank you for using our HousePrice prediction!"}

# API for single prediction

# provide the address http://localhost:8000/single-prediction that will be used to call the API for single prediction
@app.post("/single-prediction")
async def predict_single(req: HousePrcie):
    # get the data from the request
    HousePrcie_dict = {
        "OverallQual": req.OverallQual,
        "GrLivArea": req.GrLivArea,
        "GarageArea": req.GarageArea,
        "TotalBsmtSF": req.TotalBsmtSF,
        "Street": req.Street,
        "LotShape": req.LotShape
    }
    # convert the data to dataframe
    single_df = pd.DataFrame([HousePrcie_dict])
    # make the prediction
    single_prediction = make_predictions(single_df)
    # single_prediction = [345678] ---> first try for test API without ML
    # create the dataframe for the prediction
    single_pred = pd.DataFrame(single_prediction, columns=['SalePrice'])
    predict_df = single_df.join(single_pred)
    # save the prediction in the database --> db.py
    database().create_HousePricePrediction_single(predict_df)
    # return the prediction to the user
    return {"status": 200,
            "message": "Successful",
            "results": predict_df.values.tolist()}


# provide the address http://localhost:8000/multi-predictions that will be used to call the API for multiple predictions
@app.post("/multi-predictions")
async def predict(csv_file: UploadFile):
    user_data_df = pd.read_csv(csv_file.file)
    # predictions = [235443, 3432534, 4543534] --> first try for test API without ML
    # make the prediction
    predictions = make_predictions(user_data_df)
    multi_predictions = [round(prediction) for prediction in predictions]
    predict_df = user_data_df.join(pd.DataFrame(
        multi_predictions, columns=['SalePrice']))
    # save the prediction in the database --> db.py
    database().create_HousePricePredictions_df(predict_df)
    # return the prediction to the user
    return {"status": 200,
            "message": "Successful-1111",
            "results": predict_df.values.tolist()}


# provide the address http://localhost:8000/past-predictions that will be used to call the API for past predictions
@app.get('/past-predictions', status_code=200)
async def get_all_preds():
    # get the data from the database --> db.py
    all_preds = database().get_housePrices_predictions()
    # return the data to the user
    return {"status": 200,
            "message": "Successful",
            "results": all_preds}

# run the API
if __name__ == '__main__':
    uvicorn.run(app='fast:app', reload=True)
