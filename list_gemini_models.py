
import requests

API_KEY = 'AIzaSyBJgQ-A-MDnloAaj4kmknOG9BMBh7v2IrI'

def list_models():
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        models = response.json().get('models', [])
        for m in models:
            if 'generateContent' in m.get('supportedGenerationMethods', []):
                print(f"Model: {m['name']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    list_models()
