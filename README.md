# Ollama Chatbot Assistant

A conversational AI assistant in Python leveraging Ollama models for natural, interactive chat via text or speech. Chat history is stored in MongoDB, and the project includes tools for easy Ollama installation, model management, and real-time user interaction.

<br>

## 🚀 Features
Ollama Model Integration: Install, search, and manage Ollama models with a user-friendly interface.

Flexible Input: Choose between text or voice input for chatting.

Text-to-Speech Output: Hear responses aloud, with spacebar to interrupt playback.

Persistent Chat History: All conversations are stored in MongoDB for each model.

Cross-Platform: Windows installer for Ollama; manual setup possible for other OSes.

<br>

## 📂 Project Structure

    OllamaGenie/
    │
    ├── chat_assistant.py      # Main application: user interaction (text/speech)
    ├── chat.py                # Chat logic and chat history management
    ├── db.py                  # MongoDB connection and chat storage
    ├── ollama_installer.py    # Script to install/configure Ollama (Windows)
    ├── ollama_model.py        # Model selection, search, and management
    ├── requirements.txt       # Python dependencies
    ├── README.md              # Project documentation

<br>

## 🛠 Prerequisites
Python 3.8+
Download Python

MongoDB
Install MongoDB Community Edition
Ensure it runs locally at mongodb://localhost:27017/

Git
Download Git

Windows (for Ollama installer; other OS users must install Ollama manually)

<br>

## ⚡️ Quickstart
1. Clone the Repository

    ```bash 
    git clone https://github.com/dhanush03122003/OllamaGenie.git
    cd OllamaGenie
    ```

2. Create & Activate Virtual Environment (Recommended)
    ```bash 
    python -m venv venv
    ```
    ### Windows:
    ```bash 
    venv\Scripts\activate
    ```
    ### If you get an execution policy error, use this command:
    ```bash 
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    ```

3. Install Dependencies
    ```bash 
    pip install -r requirements.txt
    ```

    On Linux, you may need:
    ```bash 
    sudo apt-get install portaudio19-dev
    ```

4. Install Ollama (Windows)
    >python ollama_installer.py -i "C:/ollama" -m "C:/ollama/models" -M silent

    - `-i`: Installation directory
    - `-m`: Model storage directory
    - `-M`: Installation mode (`silent` for minimal prompts)

    Non-Windows users: Install Ollama manually and ensure ollama is in your PATH.

5. Start MongoDB
    ```bash 
    mongod
    ```

    If using a remote MongoDB, update `mongo_client_url` in `chat_assistant.py`.

6. Run the Chatbot
    ```bash 
    python chat_assistant.py
    ```

<br>

## 💬 Usage

* Model Selection:

    Choose to install/search for a new model or use an existing one.

    Follow prompts to select and download models.

* Input Mode:
    - Type 1 for text input
    - Type 2 for speech input (requires microphone)

* Chat:
    - In text mode, type your question and press Enter.
    - In speech mode, speak your question; responses are read aloud.
    - Type or say exit, quit, or goodbye to end the session.

<br>

## 🧩 Troubleshooting
* Ollama Installation Fails:
    - Ensure admin rights and a stable internet connection.
    - Check logs in `ollama_install.log`.

* MongoDB Errors:
    - Verify MongoDB is running and the connection URL is correct.

* Speech Issues:
    - Test your microphone.
    - On Linux, ensure portaudio is installed.

* Model Not Found:
    - Ensure Ollama is installed and models are downloaded.

<br>

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository

2. Create a feature branch:

    ```bash 
    git checkout -b feature/your-feature
    ```

3. Commit your changes:
    ```bash 
    git commit -m "Add your feature"
    ```

4. Push to your branch:
    ```bash 
    git push origin feature/your-feature
    ```

5. Open a Pull Request

<br>


## 📝 License

MIT License

Copyright (c) 2025 dhanush03122003

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
