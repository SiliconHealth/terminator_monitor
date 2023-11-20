import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

load_dotenv()

user = os.getenv('USER')
password = os.getenv('PASSWORD')
host = os.getenv('HOST')
db = os.getenv('DATABASE')

def get_db():
    # print(user, password, host, db)
    uri = "mongodb://%s:%s@%s" % (
        user, password, host)
    # print(uri)
    client = MongoClient(uri)

    if db in client.list_database_names():
        return client[db], "Terminator Tracker v0.1"
    else:
        return None, "Error"



