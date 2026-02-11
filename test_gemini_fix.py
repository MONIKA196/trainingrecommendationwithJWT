
import os
import google.generativeai as genai
from PIL import Image

# Use the key from your app
API_KEY = 'AIzaSyBJgQ-A-MDnloAaj4kmknOG9BMBh7v2IrI'

def test_gemini():
    try:
        print("Testing Gemini Vision connection...")
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Just a simple prompt to check if the library imports and authenticates
        response = model.generate_content("Hello, this is a test.")
        print(f"Success! Response: {response.text}")
        
    except Exception as e:
        print(f"Error detected: {e}")

if __name__ == "__main__":
    test_gemini()
