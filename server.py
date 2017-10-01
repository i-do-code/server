import sys
import json
from datetime import date, timedelta
from flask import Flask
from pymongo import MongoClient, database, collection
from flask_cors import CORS
from keras.models import load_model
import tensorflow
import keras
import h5py
import numpy as np


app = Flask(__name__)
CORS(app)

client = MongoClient('mongodb://18.221.222.193:27017/')
db = database.Database(client, "autocad")
collection = db.get_collection("date-pd-information")

def inference(dow, month, district, builings, vehicles, a_lights, s_lights, temp):
    # Pass in:
    #  - Day of Week
    #  - Month
    #  - District
    #  - Abandoned buildings
    #  - Abandoned vehicles
    #  - Alley lights out
    #  - Street lights out
    #  - Temperature
    model = load_model('predict-{}.h5'.format(district))
    prediction_perc = model.predict(np.array([dow, month, builings, vehicles, a_lights, s_lights, temp]).reshape(1, 7))
    return prediction_perc * 145

@app.route("/data/<pd>/<year>/<month>/<day>")
def get_data(pd, year, month, day):
    item = collection.find_one({'pd': int(pd), 'date': "{}/{}/{}".format(month, day, year)}, projection={'_id': False})
    return json.dumps(item)

@app.route("/predict/crime/<pd>/<year>/<month>/<day>")
def predict_crime(pd, year, month, day):
    item = collection.find_one({'pd': int(pd), 'date': "{}/{}/{}".format(month, day, year)}, projection={'_id': False})
    dow = date(int(year), int(month), int(day)).weekday()
    data = inference(dow, month, pd, item["abandoned_building"], item["abandoned_vehicle"], item["alley_light_out"], item["street_light_out"], item["temperature"])
    
    return str(data)

@app.route("/forecast/crime/<pd>/<year>/<month>/<day>")
def forecast_crime(pd, year, month, day):
    start = date(2012, 3, 5)
    diff = date(int(year), int(month), int(day)) - start

    model = load_model('lstm-{}.h5'.format(pd))
    date_range = []
    for i in range(diff.days, diff.days + 10):
        element = model.predict(np.array([[[i]]]))
        date_range.append(int(element[0]*145))
    
    return json.dumps(date_range)