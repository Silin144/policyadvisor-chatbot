from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot import PolicyAdvisorBot
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={
    r"/chat": {
        "origins": ["http://localhost:3000", "http://localhost:8000", "null"],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Initialize the chatbot
logger.info("Initializing PolicyAdvisor chatbot...")
bot = PolicyAdvisorBot()
logger.info("Chatbot initialized successfully")

@app.route('/chat', methods=['POST'])
def chat():
    try:
        logger.info("Received chat request")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Request origin: {request.headers.get('Origin')}")
        
        data = request.json
        logger.debug(f"Request data: {data}")
        
        message = data.get('message')
        if not message:
            logger.warning("No message provided in request")
            return jsonify({'error': 'No message provided'}), 400
            
        logger.info(f"Processing message: {message}")
        response = bot.get_response(message)
        logger.info(f"Generated response: {response}")
        
        return jsonify({'response': response})
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Flask server...")
    app.run(port=5001, debug=True)