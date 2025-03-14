import subprocess
import sys
import time
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import webbrowser
import os
from gtts import gTTS
from ollama import chat

class SpeechHandler:
    """Handles text-to-speech and speech-to-text conversion."""
    def speak(self, text):
        try:
            tts = gTTS(text=text, lang="en")
            tts.save("temp_output.mp3")
            data, samplerate = sf.read("temp_output.mp3")
            sd.play(data, samplerate)
            sd.wait()  # Ensures it waits until speech is finished
        except Exception as e:
            print(f"❌ Speech generation error: {e}")
    
    def listen(self):
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

class WebsiteOpener:
    """Handles opening predefined websites based on user commands."""
    sites = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "github": "https://github.com",
        "facebook": "https://www.facebook.com",
        "instagram": "https://www.instagram.com"
    }
    
    def open_website(self, command, speech_handler):
        for site, url in self.sites.items():
            if site in command:
                webbrowser.open(url)
                print(f"\n🌐 Opening {site}...")
                speech_handler.speak(f"Opening {site}.")
                return
        speech_handler.speak("Sorry, I don't have that website in my list.")

class OllamaModelHandler:
    """Handles selection and listing of available AI models."""
    def list_ollama_models(self):
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
        self.website_opener = WebsiteOpener()
        self.model_handler = OllamaModelHandler()
        self.model = self.model_handler.choose_model()
        self.input_mode = self.get_input_mode()
        self.user_name = self.get_username()
        self.welcome_user()
    
    def get_input_mode(self):
        for _ in range(3):
            self.speech_handler.speak("Gonna speak or type?")
            print("\n🗣️ Gonna speak or type?")
            
            user_choice = self.speech_handler.listen()
            if user_choice in ["speak", "speaking", "two", "2"]:
                return "2"
            if user_choice in ["type", "typing", "one", "1"]:
                return "1"
        
        print("⚠️ Too many failed attempts. Defaulting to typing mode.")
        return "1"
    
    def get_username(self):
        return os.getenv('USERNAME') or os.getenv('USER') or "there"
    
    def welcome_user(self):
        welcome_message = f"Hello {self.user_name}, how can I help you?"
        print(welcome_message)
        if self.input_mode == "2":
            self.speech_handler.speak(welcome_message)
    
    def ask_me_anything(self, question):
        if "open" in question:
            self.website_opener.open_website(question, self.speech_handler)
            return "Opening website."
        
        print("\nThinking...")
        response = chat(model=self.model, messages=[{'role': 'user', 'content': question}])
        cleaned_response = response.get('message', {}).get('content', "Unexpected response format.").strip()
        
        if self.input_mode == "2":
            self.speech_handler.speak(cleaned_response)  # Blocking call (waits for speech to finish)
        
        print("\n" + cleaned_response)
        return cleaned_response
    
    def run(self):
        while True:
            if self.input_mode == "1":
                user_input = input("\nAsk me anything (or type 'change model' to switch models): ").strip()
            else:
                time.sleep(1)  # Small delay to prevent immediate re-triggering
                user_input = self.speech_handler.listen()
                if not user_input:
                    continue
            
            if user_input.lower() in ["exit", "quit", "goodbye"]:
                goodbye_message = f"Goodbye, {self.user_name}! Session ended. 👋"
                print(goodbye_message)
                if self.input_mode == "2":
                    self.speech_handler.speak(goodbye_message)
                break
            
            if user_input.lower() == "change your model":
                self.model = self.model_handler.choose_model()
                continue
            
            self.ask_me_anything(user_input)

if __name__ == "__main__":
    assistant = ChatAssistant()
    assistant.run()
