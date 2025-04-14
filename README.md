# Ollama Chatbot Assistant

A Python-based chatbot assistant that leverages Ollama models for conversational AI. Users can interact with the chatbot via text or speech input, and chat history is stored in a MongoDB database. The project includes tools to install Ollama, manage models, and handle real-time interactions.

## Features
- **Ollama Integration**: Installs and manages Ollama models with a user-friendly interface.
- **Model Selection**: Choose from recommended models, search for specific models, or use existing ones.
- **Input Modes**: Supports typed input or speech-to-text for user queries.
- **Text-to-Speech**: Converts chatbot responses to audio with interrupt support (spacebar).
- **Chat History**: Stores conversations in MongoDB for retrieval based on the selected model.
- **Cross-Platform**: Primarily designed for Windows (Ollama installer), with potential for broader compatibility.

## Prerequisites
Before setting up the project, ensure you have the following installed:
- **Python 3.8+**: [Download Python](https://www.python.org/downloads/)
- **MongoDB**: Install MongoDB Community Edition and ensure it's running locally on `mongodb://localhost:27017/`. [MongoDB Installation Guide](https://www.mongodb.com/docs/manual/installation/)
- **Git**: To clone the repository. [Download Git](https://git-scm.com/downloads)
- A Windows system (for the Ollama installer; other OS users may need to install Ollama manually).

## Setup Instructions
Follow these steps to clone, install, and run the chatbot assistant:

1. Clone the Repository
git clone "https://github.com/dhanush03122003/OllamaGenie.git"
cd OllamaGenie

2. Create a Virtual Environment(Creating virtual environment is highly recommended):
    python -m venv venv

Activate the virtual environment:
    Windows: venv\Scripts\activate
    ## Solution for problem -- cannot be loaded because running scripts is disabled on this system. For more information, see about_Execution_Policies at
    https:/go.microsoft.com/fwlink/?LinkID=135170:
        Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass, execute this to bypass the permissions temporarily


3. Install Dependencies
    Install all required Python packages from the requirements.txt file: 
    pip install -r requirements.txt
    Note: For speech recognition, ensure you have a working microphone. On Linux, you may need portaudio
    # Ubuntu/Debian:
    sudo apt-get install portaudio19-dev

4. Install Ollama
    The project includes a script to install Ollama on Windows. 
    Run: python ollama_installer.py -i "C:/ollama" -m "C:/ollama/models" -M silent
    Modes:
        -i: Installation directory (e.g., C:/ollama).
        -m: Directory to store models (e.g., C:/ollama/models).
        -M: Installation mode (silent for minimal prompts).
    Non-Windows Users: Install Ollama manually following Ollama's official guide and ensure the ollama command is available in your PATH.

5. Start MongoDB
    Ensure MongoDB is running locally: mongod
    If MongoDB is hosted elsewhere, update the mongo_client_url in chat_assistant.py accordingly.

6. Run the Chatbot
    Start the chatbot assistant: python chat_assistant.py

7. Using the Chatbot
    Select a Model:
        Choose to install a new model, search for a specific model, or use an existing one.
        Follow prompts to install recommended models or type a model name for live search.
        Press ESC to cancel search or return to the menu.
    Choose Input Mode:
        Type 1 for text input.
        Type 2 for speech input (requires a microphone).
    Interact:
        Text Mode: 
            Type your question and press Enter. Type exit, quit, or goodbye to stop.
            Speech Mode: Speak your question; the chatbot will respond with audio. Press spacebar to interrupt audio playback.
            Chat history is saved in MongoDB and retrieved for the selected model.

$ python chat_assistant.py
    Model Selection Menu:
    1. Install a recommended model or search for a specific model
    2. Use existing models(if any)
    3. Exit
    Select an option (1-3): 1
    Start typing your model name (Enter = select, ESC = cancel):
    llama
    Matching models:
    1. llama3
    2. llama3.1
    [Select a model and proceed...]
    Choose input mode: '1' for typing, '2' for speaking: 1
    Hello, how can I help you?
    Ask me anything (or type 'exit' to quit): What's the weather like today?
    [Chatbot responds...]

Project Structure:
    ollama_installer.py: Installs and configures Ollama on Windows.
    ollama_model.py: Manages model selection, scraping, and installation.
    db.py: Handles MongoDB connections and chat history storage.
    chat.py: Processes questions and manages chat history with Ollama integration.
    chat_assistant.py: Main application for user interactions (text/speech).
    requirements.txt: Lists all Python dependencies for easy installation.

Troubleshooting:
    Ollama Installation Fails: Ensure you have admin privileges and a stable internet connection. Check logs in ollama_install.log.
    MongoDB Errors: Verify MongoDB is running and the connection URL is correct.
    Speech Issues: Test your microphone and ensure portaudio is installed for Linux.
    Model Not Found: Ensure Ollama is installed and models are downloaded successfully.

Contributing:
    Contributions are welcome! Please:
        Fork the repository.
            Create a feature branch (git checkout -b feature/your-feature).
            Commit your changes (git commit -m 'Add your feature').
            Push to the branch (git push origin feature/your-feature).
            Open a Pull Request.

License:
    This project is licensed under the MIT License. See the  file for details.