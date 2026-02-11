
import requests

API_KEY = 'AIzaSyBJgQ-A-MDnloAaj4kmknOG9BMBh7v2IrI'

def get_models():
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    r = requests.get(url)
    if r.status_code == 200:
        return [m['name'] for m in r.json().get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
    return []

def test_all():
    models = get_models()
    print(f"Testing {len(models)} models...")
    for m in models:
        # m is already "models/gemini-..."
        url = f"https://generativelanguage.googleapis.com/v1beta/{m}:generateContent?key={API_KEY}"
        r = requests.post(url, json={"contents": [{"parts": [{"text": "hi"}]}]})
        print(f"Model: {m} -> Status: {r.status_code}")
        if r.status_code == 200:
            print("SUCCESS!")
            break

if __name__ == "__main__":
    test_all()
