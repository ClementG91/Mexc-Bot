import json

def load_secret(file_path):
    with open(file_path) as f:
        secret = json.load(f)
    return secret
