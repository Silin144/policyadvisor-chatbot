# PolicyAdvisor Chatbot

A web-based chatbot interface for PolicyAdvisor that uses scraped data to provide accurate insurance-related information.

## Features

- Web-based chat interface
- Integration with PolicyAdvisor's data
- Real-time responses using OpenAI's API
- Modern, responsive design

## Tech Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Python with Flask
- Data: Scraped PolicyAdvisor content
- AI: OpenAI GPT-3.5 Turbo
- Deployment: Vercel (configured)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the development server:
```bash
python3 server.py
```

3. Visit http://localhost:5000 in your browser

## Environment Variables

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key

## Project Structure

- `static/`: Frontend files (HTML, CSS, JS)
- `data/`: Scraped PolicyAdvisor data
- `server.py`: Flask backend
- `chatbot.py`: Chatbot implementation
- `scraper.py`: Data scraping script