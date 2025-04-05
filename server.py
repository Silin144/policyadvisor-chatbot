from flask import Flask, request, jsonify, send_from_directory, current_app
from werkzeug.utils import secure_filename
import os
from flask_cors import CORS
from chatbot import PolicyAdvisorBot
import os

# File upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)  # Enable CORS for all routes

# Configure upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize the chatbot
bot = PolicyAdvisorBot()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        message = request.form.get('message')
        if not message:
            return jsonify({'error': 'No message provided'}), 400

        # Handle file upload
        file_content = None
        file_type = None
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                file_type = file.content_type
                
                # Clean up the file after reading
                os.remove(file_path)

        # Get response from the chatbot
        response = bot.get_response(message, file_content, file_type)
        
        # Return both the response and the full conversation history
        return jsonify({
            'response': response,
            'history': bot.conversation_history
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Vercel requires an app handler
app.debug = True
handler = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))