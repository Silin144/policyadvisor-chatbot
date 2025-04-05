# Insurance Advisor Chatbot

A modern, AI-powered chatbot that provides insurance advice and information using PolicyAdvisor's data. The chatbot features a clean interface with support for file uploads, formatted responses, and interactive messaging.

## Features

- **Smart Responses**: AI-powered responses using OpenAI's GPT-3.5
- **File Upload Support**: Upload and analyze insurance documents
- **Formatted Output**: 
  - Clean table formatting for comparisons
  - Properly formatted lists and sections
  - Bold text for important information
  - Structured content with proper spacing
- **Real-time Chat**: Interactive messaging with typing indicators
- **Mobile Responsive**: Works seamlessly on all devices

## Tech Stack

- **Frontend**:
  - HTML5
  - CSS3 with modern styling
  - Vanilla JavaScript for interactivity
  
- **Backend**:
  - Python with Flask
  - OpenAI API for AI responses
  - File processing capabilities

## Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd <repository-name>
```

2. **Set up Python virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create a `.env` file in the root directory:
```
OPENAI_API_KEY=your_openai_api_key
```

5. **Run the scraper to gather data**
```bash
python scraper.py
```

6. **Start the server**
```bash
python server.py
```

7. **Access the application**
Open `http://localhost:5000` in your web browser

## API Endpoints

- `POST /chat`: Send messages and receive AI responses
  - Accepts: JSON with message content
  - Returns: AI-generated response
  - Supports file uploads

## Project Structure

```
├── static/
│   ├── index.html    # Main chat interface
│   ├── styles.css    # Modern styling
│   └── script.js     # Frontend logic
├── data/
│   └── policyadvisor_data.json    # Scraped data
├── server.py         # Flask server
├── chatbot.py        # Chatbot logic
├── scraper.py        # Data scraper
└── requirements.txt  # Python dependencies
```

## Features in Detail

### Message Formatting
- Tables for comparisons using column separators
- Numbered lists with proper spacing
- Bold text for emphasis
- Bullet points for sub-items
- Clean paragraph formatting

### File Processing
- Support for PDF and text files
- Document analysis and context integration
- File size limits and type validation

### Chat Interface
- Real-time message updates
- Typing indicators
- Message timestamps
- Clean message bubbles
- Smooth animations

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details