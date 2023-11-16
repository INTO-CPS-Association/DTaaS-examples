import json

def get_data():
    # Opening JSON file
    f = open('/workspace/examples/digit_brain/drobotti_rmqfmu/rabbitMQ-credentials.json')

    # returns JSON object as 
    # a dictionary
    credentials = json.load(f) 

    # Closing file
    f.close()

    # Return data
    return credentials