import subprocess
import sys
import time
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import os
from gtts import gTTS
from ollama import chat
from DHANUSH_REQUIREMENT import type_out
from chat_history import ChatHistory  # ✅ Importing ChatHistory

class SpeechHandler:
    """Handles text-to-speech and speech-to-text conversion."""
    
    def speak(self, text):
        """Converts text to speech and plays it."""
        try:
            tts = gTTS(text=text, lang="en")
            tts.save("temp_output.mp3")
            data, samplerate = sf.read("temp_output.mp3")
            sd.play(data, samplerate)
            sd.wait()
        except Exception as e:
            print(f"❌ Speech generation error: {e}")
    
    def listen(self):
        """Converts speech to text."""
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        
        with mic as source:
            print("\n🎤 Listening... (Speak now)")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            except sr.WaitTimeoutError:
                print("⏳ Timeout! No speech detected.")
                return None
        
        try:
            text = recognizer.recognize_google(audio).lower().strip()
            print(f"🗣️ You said: {text}")
            return text
        except (sr.UnknownValueError, sr.RequestError):
            print("❌ Sorry, I couldn't understand.")
            return None

class Chatbot:
    """Handles AI chatbot interactions."""
    
    def __init__(self, model, chat_history):
        self.model = model
        self.chat_history = chat_history
    
    def ask(self, question):
        """Generates a response from the chatbot."""
        print("\nThinking...")
        self.chat_history.add_user_message(question)
        
        response = chat(model=self.model, messages=self.chat_history.get_history())
        cleaned_response = response.get('message', {}).get('content', "Unexpected response format.").strip()
        
        self.chat_history.add_bot_response(cleaned_response)
        return cleaned_response

class OllamaModelHandler:
    """Handles selection and listing of available AI models."""
    
    def list_ollama_models(self):
        """Lists available Ollama models."""
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                return [line.split()[0] for line in lines[1:]] if len(lines) > 1 else []
            else:
                print("❌ Error fetching Ollama models:", result.stderr)
                return []
        except FileNotFoundError:
            print("❌ Ollama is not installed or not found in PATH.")
            return []
    
    def choose_model(self):
        """Allows user to select an Ollama model."""
        available_models = self.list_ollama_models()
        if not available_models:
            print("\nNo Ollama models found. Install at least one model.")
            sys.exit(1)
        
        print("\nAvailable models:")
        for idx, model in enumerate(available_models, start=1):
            print(f"{idx}. {model}")
        
        while True:
            choice = input("\nSelect a model by entering its number: ").strip()
            if choice.isdigit():
                choice = int(choice)
                if 1 <= choice <= len(available_models):
                    return available_models[choice - 1]
            print("❌ Invalid choice. Please enter a valid number.")

class ChatAssistant:
    """Handles user queries and AI chatbot interactions."""
    
    def __init__(self):
        self.speech_handler = SpeechHandler()
        self.model_handler = OllamaModelHandler()
        self.model = self.model_handler.choose_model()
        self.chat_history = ChatHistory()  # ✅ Using imported ChatHistory
        self.chatbot = Chatbot(self.model, self.chat_history)
        self.input_mode = input("Choose input mode: '1' for typing, '2' for speaking: ")
        self.user_name = os.getenv('USERNAME') or os.getenv('USER') or "there"
        self.welcome_user()
    
    def welcome_user(self):
        """Welcomes the user."""
        welcome_message = f"Hello {self.user_name}, how can I help you?"
        print(welcome_message)
        if self.input_mode == "2":
            self.speech_handler.speak(welcome_message)
    
    def run(self):
        """Runs the assistant in a loop."""
        while True:
            user_input = input("\nAsk me anything (or type 'exit' to quit): ") if self.input_mode == "1" else self.speech_handler.listen()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "goodbye"]:
                print(f"Goodbye, {self.user_name}! Session ended. ")
                break
            response = self.chatbot.ask(user_input)
            type_out(response)

if __name__ == "__main__":
    assistant = ChatAssistant()
    assistant.run()