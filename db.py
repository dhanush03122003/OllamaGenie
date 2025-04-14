from pymongo import MongoClient

class Mongo:
    """
    A class to handle MongoDB operations for chat history storage and retrieval.

    This class provides methods to save user input and model responses into 
    a MongoDB collection and retrieve chat history based on the AI model.
    """

    def __init__(self, client_url="mongodb://localhost:27017/", database="AI_MODEL", collection="chat_history"):
        """
        Initializes the Mongo class and sets up the MongoDB connection.

        Args:
            client_url (str): The MongoDB connection URL. Defaults to "mongodb://localhost:27017/".
            database (str): The name of the database to connect to. Defaults to "AI_MODEL".
            collection (str): The name of the collection to use. Defaults to "chat_history".

        Attributes:
            client (MongoClient): The MongoDB client instance.
            database (Database): The connected MongoDB database instance.
            collection (Collection): The MongoDB collection instance for chat history.
        """
        self.client = MongoClient(client_url)
        self.database = self.client[database]
        self.collection = self.database[collection]

    def save_into_db(self, user_input, model_res):
        """
        Saves user input and model response into the MongoDB collection.

        Args:
            user_input (dict): A dictionary containing the user's input message.
                               Example: {"role": "user", "content": "...", "model": "..."}
            model_res (dict): A dictionary containing the model's response message.
                              Example: {"role": "assistant", "content": "...", "model": "..."}
        """
        self.collection.insert_one(user_input)
        self.collection.insert_one(model_res)

    def get_history(self, model):
        """
        Retrieves chat history for a specific AI model from the MongoDB collection.

        Args:
            model (str): The name of the AI model whose chat history is to be retrieved.

        Returns:
            list: A list of dictionaries representing the chat history,
                  excluding '_id' and 'model' fields from the results.
                  Example: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        """
        return list(self.collection.find({"model": model}, {"_id": 0 , "model": 0}))