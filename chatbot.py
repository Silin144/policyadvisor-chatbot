import openai
import json
import os
from typing import List, Dict

class PolicyAdvisorBot:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.data = self.load_data()
        self.conversation_history = []
        self.max_history = 5  # Keep last 5 messages for context
        
    def load_data(self) -> List[Dict]:
        try:
            with open('data/policyadvisor_data.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("No data file found. Please run the scraper first.")
            return []

    def find_relevant_content(self, query: str) -> str:
        # Enhanced search including all structured data
        relevant_texts = []
        query = query.lower()
        query_terms = query.split()
        
        for page in self.data:
            score = 0
            metadata_text = ""
            
            # Search in title and content with term matching
            title_lower = page['title'].lower()
            content_lower = page['content'].lower() if page['content'] else ""
            
            # Score based on number of query terms matched
            for term in query_terms:
                if term in title_lower:
                    score += 3  # Title matches are more important
                if term in content_lower:
                    score += 2
            
            # Search in structured data
            if 'structured_data' in page and page['structured_data']:
                structured_text = json.dumps(page['structured_data']).lower()
                for term in query_terms:
                    if term in structured_text:
                        score += 2
                metadata_text += "Structured Data:\n" + json.dumps(page['structured_data'], indent=2) + "\n"
            
            # Search in FAQs
            if 'faqs' in page and page['faqs']:
                for faq in page['faqs']:
                    faq_text = (faq.get('question', '') + ' ' + faq.get('answer', '')).lower()
                    for term in query_terms:
                        if term in faq_text:
                            score += 2
                    if score > 0:
                        metadata_text += "FAQ:\n" + json.dumps(faq, indent=2) + "\n"
            
            # Enhanced metadata search
            if 'metadata' in page:
                for key, value in page['metadata'].items():
                    if isinstance(value, str):
                        value_lower = value.lower()
                        for term in query_terms:
                            if term in value_lower:
                                score += 1
                                if key in ['description', 'og:description', 'twitter:description']:
                                    score += 1  # Boost description matches
                        metadata_text += f"{key}: {value}\n"
                    elif key == 'author' and any(term in ['ceo', 'founder', 'author', 'who'] for term in query_terms):
                        score += 2  # Boost author matches for leadership questions
                        metadata_text += f"Author: {value}\n"
            
            # Include categories and related topics
            if 'categories' in page and page['categories']:
                categories_text = ' '.join(page['categories']).lower()
                for term in query_terms:
                    if term in categories_text:
                        score += 1
                metadata_text += f"Categories: {', '.join(page['categories'])}\n"
            
            if 'related_topics' in page and page['related_topics']:
                topics_text = ' '.join(page['related_topics']).lower()
                for term in query_terms:
                    if term in topics_text:
                        score += 1
                metadata_text += f"Related Topics: {', '.join(page['related_topics'])}\n"
            
            if score > 0:
                content = f"Title: {page['title']}\n"
                if metadata_text:
                    content += f"Additional Information:\n{metadata_text}\n"
                if page.get('content_structure'):
                    content += "Content Structure:\n"
                    for item in page['content_structure']:
                        if item['type'] == 'heading':
                            content += f"\nHeading (Level {item['level']}): {item['text']}\n"
                        elif item['type'] == 'paragraph':
                            content += f"{item['text']}\n"
                        elif item['type'] == 'list':
                            content += "- " + "\n- ".join(item['items']) + "\n"
                elif page['content']:
                    content += f"Content: {page['content'][:1000]}..."
                relevant_texts.append((score, content))
        
        # Sort by relevance score and return top 5 (increased from 3)
        relevant_texts.sort(key=lambda x: x[0], reverse=True)
        return "\n\n".join(text for score, text in relevant_texts[:5])

    def process_file(self, file_content: str, file_type: str) -> str:
        """Process uploaded files and extract relevant information."""
        # Basic text extraction based on file type
        if file_type == 'application/pdf':
            # For now, just use the raw text. In a real implementation,
            # you'd want to use a proper PDF parser
            return file_content
        elif file_type.startswith('text/'):
            return file_content
        else:
            return "Unsupported file type"

    def get_response(self, user_input: str, file_content: str = None, file_type: str = None) -> str:
        # Process any uploaded file
        file_context = ""
        if file_content and file_type:
            file_context = self.process_file(file_content, file_type)

        # Find relevant content from our scraped data
        data_context = self.find_relevant_content(user_input)
        
        if not data_context:
            data_context = "No specific information found in the database."

        # Combine file context with database context
        context = f"{data_context}\n\nUploaded Document Context:\n{file_context}" if file_context else data_context

        # Create the prompt for the API
        system_message = {
            "role": "system",
            "content": (
                "You are an expert insurance advisor bot trained on PolicyAdvisor's comprehensive data. "
                "Your knowledge encompasses:\n"
                "- Detailed insurance product information including term life, whole life, critical illness, disability, and other insurance types\n"
                "- In-depth understanding of insurance concepts, terms, and industry practices\n"
                "- Current insurance rates, trends, and market conditions in Canada\n"
                "- PolicyAdvisor's services, company history, leadership, and operational processes\n"
                "- Regulatory requirements and compliance in the Canadian insurance industry\n\n"
                "When formatting responses with comparisons or structured data:\n"
                "1. ALWAYS use tables with clear headers\n"
                "2. Format tables using | character as column separator\n"
                "3. First row should be the header row\n"
                "4. Example table format:\n"
                "   Aspect | With Insurance | Without Insurance\n"
                "   Financial Security | Protected | At Risk\n"
                "   Monthly Cost | $X | $0\n"
                "5. Keep table columns aligned and use consistent spacing\n"
                "6. For non-table content, use clear paragraphs\n\n"
                "When formatting responses:\n"
                "1. For numbered lists, use format '1. ' at the start of each point\n"
                "2. Each numbered point should start on a new line\n"
                "3. For bold text, use **text** format\n"
                "4. For bullet points, use '- ' at the start of each point\n"
                "5. For tables, use | as column separator\n"
                "6. Keep formatting consistent throughout the response\n\n"
                "When structuring content:\n"
                "1. Start with a brief introduction\n"
                "2. Use numbered points for main sections\n"
                "3. Use bullet points for sub-items\n"
                "4. Use tables for comparisons\n"
                "5. Bold important terms and headings\n"
                "6. Keep paragraphs short and readable\n\n"
                "If you're not completely certain about any information, clearly state your limitations "
                "and suggest where the user might find more definitive answers."
            )
        }

        # Add conversation history to messages
        messages = [system_message]
        messages.extend(self.conversation_history[-self.max_history:])  # Add recent conversation history
        messages.append({"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_input}"})

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            # Get the response content
            response_content = response.choices[0].message['content'].strip()
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": response_content})
            
            # Trim history if it gets too long
            if len(self.conversation_history) > self.max_history * 2:  # *2 because we store pairs of messages
                self.conversation_history = self.conversation_history[-self.max_history * 2:]
            
            return response_content
        except Exception as e:
            error_msg = f"I apologize, but I encountered an error: {str(e)}"
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": error_msg})
            return error_msg

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