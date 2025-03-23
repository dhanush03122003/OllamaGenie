# chat_history.py
from db import Mongo

class ChatHistory(Mongo):
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
