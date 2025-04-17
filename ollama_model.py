import subprocess
import re
import requests
import sys
import keyboard
import msvcrt

class OllamaModel:
    """
    A class to manage Ollama models, including scraping model data, installing recommended models,
    searching for specific models, and using existing models.
    """
    def __init__(self):
        """
        Initialize the OllamaModel class.

        Attributes:
            models (dict): A dictionary containing model names as keys and their sizes as values.
            model_names (list): A list of all available model names.
            current_suggestions (list): A list of current search suggestions for models.
        """
        self.models = {}
        self.model_names = []
        self.current_suggestions = []
        self.scrape()

    def model_selection(self):
        """
        Main model selection menu with dynamic cursor visibility.

        Allows the user to:
        1. Install a recommended model or search for a specific model.
        2. Use existing models (if any).
        3. Exit the program.

        Returns:
            str: The selected model name.
        """
        while True:
            print("\nModel Selection Menu:")
            print("1. Install a recommended model or search for a specific model")
            print("2. Use existing models(if any)")
            print("3. Exit")
            
            choice = input("Select an option (1-3): ").strip()

            if choice == "1":
                print("\033[?25l", end="", flush=True)
                try:
                    selected_model = self.search_and_install()
                    if selected_model:
                        return selected_model
                finally:
                    print("\033[?25h", end="", flush=True)
            elif choice == "2":
                return self.use_existing()
            elif choice == "3":
                print("Exiting...")
                sys.exit(0)
            else:
                print("Invalid choice. Please try again.")

    def scrape(self, url='https://ollama.com/library'):
        """
        Scrape model data from the Ollama library.

        Args:
            url (str): The URL of the Ollama library page to scrape. Defaults to 'https://ollama.com/library'.

        Populates:
            self.models: A dictionary of model names and their sizes.
            self.model_names: A list of all available model names.
        """
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text

        model_blocks = re.findall(r'<a[^>]*href="/library/[^"]+"[^>]*>.*?</a>', html_content, re.DOTALL)
        for block in model_blocks:
            title_match = re.search(r'x-test-model-title[^>]*title="([^"]+)"', block)
            if not title_match:
                continue
            model_name = title_match.group(1).strip()

            sizes = re.findall(r'x-test-size[^>]*>([^<]+)', block)
            sizes = [s.strip() for s in sizes if s.strip()]
            self.models[model_name] = sizes

        self.model_names = list(self.models.keys())

    def install_recommended(self):
        """
        Install a recommended model from the top 10 available models.

        Returns:
            str: The name of the selected and installed model.
        """
        print("\nTop 10 Recommended Models:")
        top_models = list(self.models.keys())[:10]
        for idx, name in enumerate(top_models, 1):
            print(f"{idx}. {name}")

        choice = int(input("\nSelect a model by number: ")) - 1
        return self.handle_model_installation(top_models[choice])

    def search_and_install(self):
        """
        Perform a live search for a specific model and install it.

        Provides clean in-place updates as the user types their query.

        Returns:
            str: The name of the selected and installed model, or None if canceled.
        """
        query = []
        suggestion_lines = 0
        print("\033[?25l")  
        print("Start typing your model name (Enter = select, ESC = cancel):")
        
        while True:
            # Update suggestions and display them
            self.current_suggestions = self.get_suggestions(''.join(query))
            suggestion_lines = self._update_display(query, suggestion_lines)    
            char = self._getch()
            
            if char in ('\r', '\n'):  
                if self.current_suggestions:
                    return self._handle_selection(self.current_suggestions)
                continue
            
            elif char == '\x1b': 
                print("\nSearch cancelled.")
                return None
            
            elif char in ('\x7f', '\x08'):  # Backspace pressed
                if query:
                    query.pop()
            
            else:  # Add character to query
                query.append(char)
            
    def use_existing(self):
        """
        Use installed models and allow pressing ESC to return to the model selection menu.

        Returns:
            str or None: The selected model name or None if ESC is pressed.
        """
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)

        if result.returncode != 0:
            print("No existing models found.")
            return None

        lines = result.stdout.strip().split("\n")[1:]

        if not lines:
            print("No existing models found.")
            return None

        print("\nExisting Models:")
        models = [line.split()[0] for line in lines]

        for idx, model in enumerate(models, 1):
            print(f"{idx}. {model}")

        print("\nPress ESC to return to the model selection menu or type a number to select a model.")

        selected_model = ""
        while True:
            if msvcrt.kbhit():  # Check if a key is pressed
                key = msvcrt.getch()  # Get the pressed key
                
                # Check if ESC key is pressed
                if key == b'\x1b':  # ESC key
                    print("\nReturning to the model selection menu...")
                    return None
                
                # Handle numeric input
                elif key.isdigit():
                    selected_model += key.decode()
                    print(f"\rSelect a model by number: {selected_model}", end="", flush=True)
                
                # Handle Enter key to confirm selection
                elif key == b'\r':  # Enter key
                    try:
                        choice = int(selected_model) - 1
                        if 0 <= choice < len(models):
                            return models[choice]
                        else:
                            print("\nInvalid choice. Please try again.")
                            selected_model = ""
                    except ValueError:
                        print("\nInvalid input. Please try again.")
                        selected_model = ""

    def get_suggestions(self, query):
        """Get search suggestions"""
        if len(query) == 0:
            return list(self.models.keys())[:10]
        return [name for name in self.model_names if query.lower() in name.lower()][:5]

    def _handle_selection(self, suggestions):
        """Handle model selection from current suggestions"""
        print("\nSelect a model:")
        for i, name in enumerate(suggestions, 1):
            print(f"{i}. {name}")
        try:
            choice = int(input("Enter number: ")) - 1
            return self.handle_model_installation(suggestions[choice])
        except (ValueError, IndexError):
            print("Invalid selection.")
            return None

    def _update_display(self, query, prev_lines):
        """Update the terminal display in-place"""
        # Clear previously printed suggestion lines

        for _ in range(prev_lines):
            sys.stdout.write('\033[F\033[K')  # Move cursor up and clear line
        sys.stdout.flush()

        # Now print the updated block
        current_query = ''.join(query)
        print(f"Search: {current_query}")

        if self.current_suggestions:
            print("Matching models:")
            for i, name in enumerate(self.current_suggestions, 1):
                print(f"  {i}. {name}")
            return len(self.current_suggestions) + 2  # lines printed
        # elif len(query) == 0:
        #     print("Suggested models:")
        #     for i, name in enumerate(list(self.models.keys())[:10], 1):
        #         print(f"  {i}. {name}")
        #     return 12  
        else:
            print("No matches found")
            return 2  # lines printed when no matches

    def _getch(self):
        """Cross-platform input handling"""
        try:
            import msvcrt
            return msvcrt.getch().decode()
        except ImportError:
            import sys, tty, termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

    def handle_model_installation(self, model):
        """Handle model installation"""
        sizes = self.models.get(model, [])
        size = None

        if sizes:
            print(f"\nAvailable sizes for {model}:")
            for idx, s in enumerate(sizes, 1):
                print(f"{idx}. {s}")
            size_choice = int(input("Select size by number (Enter to skip): ") or 0) - 1
            size = sizes[size_choice] if size_choice >= 0 else None

        full_model = f"{model}:{size}" if size else model
        self.install(full_model)
        return full_model

    def install(self, model_name):
        """Install model using ollama pull"""
        process = subprocess.Popen(
            ["ollama", "pull", model_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        for line in iter(process.stdout.readline, ''):
            print(line.strip())


if __name__ == "__main__":
    ollama = OllamaModel()
    selected_model = ollama.model_selection()
    print(f"\nSelected model: {selected_model}")