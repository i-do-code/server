import sys
import json
import tensorflow
import keras
import h5py
from datetime import date
from flask import Flask
from pymongo import MongoClient, database, collection
from flask_cors import CORS
from keras.models import load_model


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
    prediction_perc = model.predict([[dow, month, district, builings, vehicles, a_lights, s_lights, temp]])
    return prediction_perc * 145

@app.route("/data/<pd>/<year>/<month>/<day>")
def hello(pd, year, month, day):
    item = collection.find_one({'pd': int(pd), 'date': "{}/{}/{}".format(month, day, year)}, projection={'_id': False})
    return json.dumps(item)

@app.route("/predict/crime/<pd>/<year>/<month>/<day>")
def hello(pd, year, month, day):
    item = collection.find_one({'pd': int(pd), 'date': "{}/{}/{}".format(month, day, year)}, projection={'_id': False})
    dow = date(year, month, day).weekday()
    data = inference(dow, month, pd, item["abandoned_building"], item["abandoned_vehicle"], item["alley_light_out"], item["street_light_out"], item["temperature"])
    return json.dumps(data)


