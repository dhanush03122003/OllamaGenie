import subprocess
import sys
import time
import os
import tempfile
import sounddevice as sd
import speech_recognition as sr
import soundfile as sf
import keyboard
from gtts import gTTS
from ollama_model import OllamaModel  # Import the updated OllamaModel class
from chat import Chat

class SpeechHandler:
    """
    Handles text-to-speech and speech-to-text conversion.
    """

    def speak(self, text):
        """
        Converts text to speech and plays it with spacebar interrupt support.

        Args:
            text (str): The text to be converted to speech.
        """
        try:
            # Generate temporary MP3 file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                tts = gTTS(text=text, lang="en")
                temp_audio_path = temp_audio.name
                tts.save(temp_audio_path)

            # Read audio data
            data, samplerate = sf.read(temp_audio_path)

            # Start playback in a separate thread
            self.is_playing = True

            def play_audio():
                sd.play(data, samplerate)
                sd.wait()  # Wait until playback finishes
                self.is_playing = False

            import threading  # Use threading for non-blocking playback
            playback_thread = threading.Thread(target=play_audio)
            playback_thread.start()

            # Listen for spacebar interrupt
            while self.is_playing:
                if keyboard.is_pressed("space"):
                    print("\nPlayback interrupted by user.")
                    sd.stop()  # Stop playback immediately
                    self.is_playing = False
                    break

        except Exception as e:
            print(f"Speech generation error: {e}")

    def listen(self):
        """
        Converts speech to text.

        Returns:
            str or None: The recognized text if successful, otherwise None.
        """
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            print("\nListening... (Speak now)")
            recognizer.adjust_for_ambient_noise(source, duration=1)

            try:
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
                text = recognizer.recognize_google(audio).lower().strip()
                print(f"You said: {text}")
                return text
            except sr.WaitTimeoutError:
                print("Timeout! No speech detected.")
                return None
            except sr.UnknownValueError:
                print("Sorry, I couldn't understand.")
                return None
            except sr.RequestError as e:
                print(f"Speech recognition service error: {e}")
                return None


class Chatbot:
    """
    Manages chatbot interactions while delegating logic to ChatProcessor.
    """
    def __init__(self, chat):
        """
        Initialize the Chatbot.

        Args:
            chat (Chat): An instance of the Chat class.
        """
        self.processor = chat

    def ask(self, question):
        """
        Delegates question processing to ChatProcessor.

        Args:
            question (str): The user's question.

        Returns:
            str: The chatbot's response.
        """
        return self.processor.process_question(question)


class ChatAssistant:
    """
    Handles user queries and AI chatbot interactions.
    """

    def __init__(self, mongo_client_url="mongodb://localhost:27017/", database="AI_MODEL", collection="chat_history"):
        """
        Initialize ChatAssistant with model selection, input mode, and components.

        Args:
            mongo_client_url (str): The MongoDB connection URL. Defaults to localhost.
            database (str): The name of the MongoDB database. Defaults to "AI_MODEL".
            collection (str): The name of the MongoDB collection. Defaults to "chat_history".
        """
        # Initialize model selection
        self.ollama_model = OllamaModel()
        self.model = self.ollama_model.model_selection()

        if not self.model:  # If no model is selected
            print("No model selected. Redirecting to use model selection menu...")
            self.model = self.ollama_model.model_selection()
            if not self.model:  # If still no model is selected
                print("No model selected. Exiting...")
                sys.exit(1)

        # Initialize input mode
        while True:
            self.input_mode = input("Choose input mode: '1' for typing, '2' for speaking: ").strip()
            if self.input_mode in ["1", "2"]:
                break
            print("Invalid choice. Please enter '1' or '2'.")

        # Initialize speech handler and chat components
        self.speech_handler = SpeechHandler()
        self.chat = Chat(self.model, mongo_client_url, database, collection)
        self.chatbot = Chatbot(self.chat)

    def welcome_user(self):
        """
        Welcomes the user.
        """
        welcome_message = f"Hello, how can I help you?"
        print(welcome_message)
        if self.input_mode == "2":
            self.speech_handler.speak(welcome_message)

    def run(self):
        """
        Runs the assistant in a loop.
        
        Continuously listens for user input (text or speech) and generates chatbot responses.
        """
        if not self.model:  # Check if a model was selected during initialization
            print("No model selected. Exiting...")
            return

        while True:
            # Prompt user for input based on input mode
            user_input = (
                input("\nAsk me anything (or type 'exit' to quit): ")
                if self.input_mode == "1"
                else self.speech_handler.listen()
            )

            # Skip empty inputs
            if not user_input:
                continue

            # Handle exit commands
            if user_input.lower() in ["exit", "quit", "goodbye"]:
                print(f"Goodbye, Session ended.")
                break

            # Process user input and generate response
            response = self.chatbot.ask(user_input)

            # Speak the response if input mode is speech
            if self.input_mode == "2":
                self.speech_handler.speak(response)


if __name__ == "__main__":
    assistant = ChatAssistant()
    assistant.run()
