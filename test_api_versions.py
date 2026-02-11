
import requests

API_KEY = 'AIzaSyBJgQ-A-MDnloAaj4kmknOG9BMBh7v2IrI'

def test_url(full_url):
    payload = {"contents": [{"parts": [{"text": "hi"}]}]}
    response = requests.post(full_url, json=payload)
    print(f"URL: {full_url}\nStatus: {response.status_code}\nResponse: {response.text[:200]}\n")

# Try with and without v1beta/models paths
test_url(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}")
test_url(f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={API_KEY}")
test_url(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}")
