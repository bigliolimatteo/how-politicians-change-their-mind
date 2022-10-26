import json
import os

RELEVANT_FIELDS = ["text", "created_at"]

def extract_relevant_data_from_file(file):
    tweets = json.load(file)["tweets"]
    return [{ key: tweet[key] for key in RELEVANT_FIELDS } for tweet in tweets]

def read_data(input_directory: str):
    input_data = dict()

    for filename in os.listdir(input_directory):
        if filename.endswith("json"):
            politician_name = filename.split(".")[0]
            file = open(os.path.join(input_directory, filename), "r")
            input_data[politician_name] = extract_relevant_data_from_file(file)
            
        else: 
            raise Exception(f"Input file {filename} has a non supported format.")

    return input_data