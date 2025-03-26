# chat_history.py
from db import Mongo
from ollama import chat

class Chat(Mongo):
    """Handles storing and managing chat history."""
    
    def __init__(self, model, mongo_client_url, database, collection):
        self.model = model
        self.user_input = None
        self.model_response = None

        try:
            self.mongo_client = Mongo(mongo_client_url, database, collection)
            self.history = self.mongo_client.get_history(model=self.model)
            if len(self.history) == 0:
                pass
                # self.history.append({"role": "system", "content": "You are a helpful assistant."})
        except Exception as e:
            print(f"Error initializing ChatHistory: {e}")
            self.history = [{"role": "system", "content": "You are a helpful assistant."}]

    def process_question(self, question):
        """Processes the user's question and returns a response."""
        print("\nThinking...")
        self.add_user_message(question)

        # print(self.get_history())
        full_response = ""
        
        for response in chat(model=self.model, messages=self.get_history(), stream=True):
            chunk = response.get("message", {}).get("content", "")
            print(chunk, end="", flush=True) 
            full_response += chunk  

        # Clean the final response
        if full_response:
            cleaned_response = full_response.strip()
        else:
            cleaned_response = "Unexpected response format."
        self.add_bot_response(cleaned_response)
        return cleaned_response
    
    def add_user_message(self, message):
        """Adds a user message to chat history."""
        try:
            self.history.append({"role": "user", "content": message})
            self.user_input = {"role": "user", "content": message, "model": self.model}
            # self.mongo_client.save_into_db({"role": "user", "content": message, "model": self.model})
        except Exception as e:
            print(f"Error adding user message: {e}")
    
    def add_bot_response(self, response):
        """Adds a chatbot response to chat history."""
        try:
            self.history.append({"role": "assistant", "content": response})
            self.model_response = {"role": "assistant", "content": response, "model": self.model}
            self.mongo_client.save_into_db(user_input = self.user_input , model_res = self.model_response)
        except Exception as e:
            print(f"Error adding bot response: {e}")
    
    def get_history(self):
        """Returns the chat history."""
        try:
            return self.history
        except Exception as e:
            print(f"Error retrieving chat history: {e}")
            return []
