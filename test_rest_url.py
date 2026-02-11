
import requests
import json

API_KEY = 'AIzaSyBJgQ-A-MDnloAaj4kmknOG9BMBh7v2IrI'

def test_model(model_name):
    # Try with 'models/' prefix
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={API_KEY}"
    payload = {"contents": [{"parts": [{"text": "Say hello"}]}]}
    response = requests.post(url, json=payload)
    print(f"Testing {model_name} -> Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_model("gemini-2.0-flash")
    test_model("gemini-1.5-flash")
    test_model("gemini-2.0-flash-exp")
