from flask import Flask, request, jsonify, render_template
import openai
import json
import re

app = Flask(__name__)

# Set your OpenAI API key
openai.api_key = 'YOUR_OPENAI_API_KEY'

# Load animal tag data
with open('animal_data.json') as f:
    animal_data = json.load(f)

# Function to pull tag from user message
def extract_tag(text):
    match = re.search(r'\b([A-Z]?\d{2,4})\b', text)
    return match.group(1) if match else None

# Create prompt for OpenAI
def create_prompt(tag, question):
    data = animal_data.get(tag)
    if not data:
        return f"Sorry, I don't have data for animal {tag}."

    return f"""
You are Olive.AI, a helpful assistant for farmers.

Animal Tag: {tag}
- Temperature: {data['temperature']}
- Weight: {data['weight']}
- Activity Level: {data['activity']}
- Last Health Check: {data['lastCheck']}

Answer the farmer’s question: {question}
"""

# Serve the main website
@app.route('/')
def home():
    return render_template('index.html')

# Handle chat messages
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    tag = extract_tag(user_input)

    if not tag:
        return jsonify({'reply': "Please include an animal tag in your message."})

    prompt = create_prompt(tag, user_input)

    if prompt.startswith("Sorry"):
        return jsonify({'reply': prompt})

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150,
        temperature=0.7
    )
    answer = response.choices[0].text.strip()
    return jsonify({'reply': answer})

if __name__ == '__main__':
    app.run(debug=True)
