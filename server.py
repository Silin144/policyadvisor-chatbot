from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from chatbot import PolicyAdvisorBot
import os

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)  # Enable CORS for all routes

# Initialize the chatbot
bot = PolicyAdvisorBot()

@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
            
        # Get response from the chatbot
        response = bot.get_response(message)
        
        return jsonify({'response': response})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vercel requires an app handler
app.debug = True
handler = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))