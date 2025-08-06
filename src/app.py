from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')  # Ensure your Mistral API key is set in the .env file
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"  # Example URL, change if needed

@app.route('/')
def home():
    return render_template('index.html') 

@app.route("/generate-recipe", methods=["POST"])
def generate_recipe():
    data = request.json
    preferences = data.get("preferences", "")
    restrictions = data.get("restrictions", "")
    ingredients = data.get("ingredients", "")

    prompt = f"""
You are a creative and professional AI Chef. Create a unique recipe based on the following input:

User Preferences: {preferences}
Dietary Restrictions: {restrictions}
Available Ingredients: {ingredients}

Please output:
- Recipe Name
- Description
- Ingredients List
- Step-by-Step Instructions
- Estimated Prep & Cook Time
"""

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistral-medium",  # or mistral-tiny / mistral-large, depending on your plan
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        response = requests.post(MISTRAL_API_URL, headers=headers, json=payload)
        print("Raw response:", response.text)

        if response.status_code == 200:
            try:
                result = response.json()
                generated_text = result["choices"][0]["message"]["content"]
                return jsonify({"recipe": generated_text})
            except Exception as json_err:
                return jsonify({"error": "Failed to parse JSON: " + str(json_err), "raw": response.text}), 500
        else:
            return jsonify({
                "error": f"API Error {response.status_code}",
                "raw": response.text
            }), response.status_code

    except Exception as e:
        return jsonify({"error": f"Exception: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)