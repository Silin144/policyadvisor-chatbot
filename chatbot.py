import openai
import json
import os
from typing import List, Dict

class PolicyAdvisorBot:
    def __init__(self):
        openai.api_key = "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"
        self.data = self.load_data()
        
    def load_data(self) -> List[Dict]:
        try:
            with open('data/policyadvisor_data.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("No data file found. Please run the scraper first.")
            return []

    def find_relevant_content(self, query: str) -> str:
        # Enhanced search including metadata
        relevant_texts = []
        query = query.lower()
        
        for page in self.data:
            score = 0
            metadata_text = ""
            
            # Search in title and content
            if query in page['title'].lower():
                score += 3  # Title matches are more important
            if query in page['content'].lower():
                score += 2
                
            # Search in metadata
            if 'metadata' in page:
                for key, value in page['metadata'].items():
                    if isinstance(value, str):
                        if query in value.lower():
                            score += 1
                        metadata_text += f"{key}: {value}\n"
                    elif key == 'author' and query in ['ceo', 'founder', 'author', 'who']:
                        score += 2  # Boost author matches for leadership questions
                        metadata_text += f"Author: {value}\n"
            
            if score > 0:
                content = f"Title: {page['title']}\n"
                if metadata_text:
                    content += f"Additional Information:\n{metadata_text}\n"
                if page['content']:
                    content += f"Content: {page['content'][:1000]}..."
                relevant_texts.append((score, content))
        
        # Sort by relevance score and return top 3
        relevant_texts.sort(key=lambda x: x[0], reverse=True)
        return "\n\n".join(text for score, text in relevant_texts[:3])

    def get_response(self, user_input: str) -> str:
        # Find relevant content from our scraped data
        context = self.find_relevant_content(user_input)
        
        if not context:
            context = "No specific information found in the database."

        # Create the prompt for the API
        messages = [
            {"role": "system", "content": (
                "You are a helpful insurance advisor bot trained on PolicyAdvisor's data. "
                "You can answer questions about PolicyAdvisor's services, company information, leadership, and insurance products. "
                "Pay special attention to metadata like authors and publication dates when answering questions about the company. "
                "For leadership questions, note that article authors may be key company figures. "
                "Use the provided context to answer questions accurately and comprehensively. "
                "If you're not sure about something, say so rather than making assumptions."
            )},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_input}"}
        ]

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"

def main():
    bot = PolicyAdvisorBot()
    print("PolicyAdvisor Bot initialized! Type 'quit' to exit.")
    
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ['quit', 'exit', 'bye']:
            break
            
        response = bot.get_response(user_input)
        print("\nBot:", response)

if __name__ == "__main__":
    main()