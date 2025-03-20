# chat_history.py
class ChatHistory:
    """Handles storing and managing chat history."""
    
    def __init__(self):
        self.history = [{"role": "system", "content": "You are a helpful assistant."}]
    
    def add_user_message(self, message):
        """Adds a user message to chat history."""
        self.history.append({"role": "user", "content": message})
    
    def add_bot_response(self, response):
        """Adds a chatbot response to chat history."""
        self.history.append({"role": "assistant", "content": response})
    
    def get_history(self):
        """Returns the chat history."""
        return self.history
