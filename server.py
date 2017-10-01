from flask import Flask
from pymongo import MongoClient, database, collection
import sys
import json

app = Flask(__name__)

client = MongoClient('mongodb://18.221.222.193:27017/')
db = database.Database(client, "autocad")
collection = db.get_collection("date-pd-information")

@app.route("/data/<pd>/<year>/<month>/<day>")
def hello(pd, year, month, day):
    item = collection.find_one({'pd': int(pd), 'date': "{}/{}/{}".format(month, day, year)}, projection={'_id': False})
    print(item, file=sys.stderr)
    return json.dumps(item)
