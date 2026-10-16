import json
import os

# Credentials of the drobotti_rmqfmu digital twin; the location can be
# changed with the RABBITMQ_CREDENTIALS environment variable
CREDENTIALS_FILE = os.environ.get(
    "RABBITMQ_CREDENTIALS",
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "../../digital_twins/drobotti_rmqfmu/rabbitMQ-credentials.json"))

def get_data():
    # Opening JSON file
    f = open(CREDENTIALS_FILE)

    # returns JSON object as 
    # a dictionary
    credentials = json.load(f) 

    # Closing file
    f.close()

    # Return data
    return credentials
