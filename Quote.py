import requests
import json


def getQuote():
    response = requests.request("GET", "https://catfact.ninja/fact")
    formatted = response.text
    return formatted
