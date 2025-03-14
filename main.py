import subprocess
import datetime
import sys
import time
import threading
import sounddevice as sd
import soundfile as sf
import numpy
import gtts  # Text-to-Speech
import speech_recognition as sr
import webbrowser
import os  # For fetching system environment variables
from ollama import chat
from gtts import gTTS

def speak(text):
    """Convert text to speech, save it as an MP3 file, and play it."""
    try:
        tts = gTTS(text=text, lang="en")
        tts.save("temp_output.mp3")
        data, samplerate = sf.read("temp_output.mp3")
        sd.play(data, samplerate)
        sd.wait()
    except Exception as e:
        print(f"❌ Speech generation error: {e}")

def listen():
    """Captures user voice input with improved handling."""
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
    except sr.UnknownValueError:
        print("❌ Sorry, I couldn't understand.")
        return None
    except sr.RequestError:
        print("❌ Speech recognition service is unavailable.")
        return None

def open_website(command):
    """Opens a website based on user input."""
    sites = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "github": "https://github.com",
        "facebook": "https://www.facebook.com",
        "instagram": "https://www.instagram.com"
    }

    for site in sites:
        if site in command:
            webbrowser.open(sites[site])
            print(f"\n🌐 Opening {site}...")
            speak(f"Opening {site}.")
            return

    speak("Sorry, I don't have that website in my list.")

def list_ollama_models():
    """Fetch available Ollama models and return a cleaned list."""
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

def loading_animation(event):
    """Displays bouncing dots animation while the chatbot processes."""
    frames = ["   ", ".  ", ".. ", "..."]
    i = 0
    while not event.is_set():
        sys.stdout.write(f"\rThinking {frames[i]} ")
        sys.stdout.flush()
        time.sleep(0.5)
        i = (i + 1) % len(frames)
    sys.stdout.write("\r                 \r")

def ask_me_anything(question: str, model: str, input_mode: str):
    """Handles user commands or queries AI chatbot."""
    if "open" in question:
        open_website(question)
        return "Opening website."

    print("\nThinking ", end="")
    event = threading.Event()
    animation_thread = threading.Thread(target=loading_animation, args=(event,))
    animation_thread.start()

    try:
        response = chat(model=model, messages=[{'role': 'user', 'content': question}])
        cleaned_response = response.get('message', {}).get('content', "Unexpected response format.").strip()
    except Exception as e:
        cleaned_response = f"Error communicating with Ollama: {str(e)}"

    event.set()  # Stop animation
    animation_thread.join()

    # Start speaking **immediately** while printing the response  
    if input_mode == "2":  
        threading.Thread(target=speak, args=(cleaned_response,), daemon=True).start()

    print("\n" + cleaned_response)  # Print after speaking starts  
    return cleaned_response


def choose_model():
    """Lists available models and allows the user to select one via typing only."""
    available_models = list_ollama_models()
    if not available_models:
        print("\nNo Ollama models found. Install at least one model.")
        sys.exit(1)

    print("\nAvailable models:")
    for idx, model in enumerate(available_models, start=1):
        print(f"{idx}. {model}")

    while True:
        try:
            choice = int(input("\nSelect a model by entering its number: "))
            if 1 <= choice <= len(available_models):
                return available_models[choice - 1]
            else:
                print("❌ Invalid choice. Enter a valid number.")
        except ValueError:
            print("❌ Please enter a valid number.")

def get_input_mode():
    """Ask user to choose between typing or speaking, ensuring active reminders."""
    attempts = 0
    max_attempts = 3  # After 3 failed attempts, default to typing

    while attempts < max_attempts:
        speak("Gonna speak or type?")
        print("\n🗣️ Gonna speak or type?")

        user_choice = listen()
        
        if user_choice:
            user_choice = user_choice.lower().strip()
            print(f"🗣️ You said: {user_choice}")

            if user_choice in ["speak", "speaking", "two", "2"]:
                return "2"
            if user_choice in ["type", "typing", "one", "1"]:
                return "1"

        # If input is not recognized or times out
        attempts += 1
        print(f"❌ Attempt {attempts}/{max_attempts}: Couldn't understand.")
        speak("Still active. Speak now if you want.")

    # After max attempts, default to typing
    print("⚠️ Too many failed attempts. Defaulting to typing mode.")
    speak("Too many failed attempts. Switching to typing mode.")
    return "1"

def get_username():
    """Fetch the current user's name dynamically."""
    return os.getenv('USERNAME') or os.getenv('USER') or "there"  # Fallback to "there" if name can't be fetched

if __name__ == "__main__":
    user_name = get_username()
    welcome_message = f"Hello {user_name}, how can I help you?"
    print(welcome_message)

    # Speak the welcome message only if "speak" mode is chosen later
    selected_model = choose_model()
    choice = get_input_mode()

    if choice == "2":  # Speak mode
        speak(welcome_message)

    while True:
        if choice == "1":
            user_input = input("\nAsk me anything (or type 'change model' to switch models): ").strip()
        elif choice == "2":
            user_input = listen()
            if not user_input:
                continue
        else:
            print("❌ Invalid choice. Try again.")
            continue

        if user_input.lower() in ["exit", "quit", "bye"]:
            goodbye_message = f"Goodbye, {user_name}! Session ended. 👋"
            print(goodbye_message)
            if choice == "2":  # Speak mode
                speak(goodbye_message)
            break
        
        if user_input.lower() == "change model":
            selected_model = choose_model()
            continue
        
        ask_me_anything(user_input, selected_model, choice)
