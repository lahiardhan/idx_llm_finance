import requests
import json

def retrieve_from_endpoint(url: str, api_key) -> dict:
    headers = {"Authorization": api_key}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    return json.dumps(data)