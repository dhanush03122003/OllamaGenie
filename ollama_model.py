import subprocess
import re
import requests

class OllamaModel:
    def __init__(self):
        self.models = {}
        self.model_names = []
        self.scrape()

    def scrape(self, url='https://ollama.com/library'):
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text

        model_blocks = re.findall(r'<a[^>]*href="/library/[^"]+"[^>]*>.*?<\/a>', html_content, re.DOTALL)

        for block in model_blocks:
            title_match = re.search(r'x-test-model-title[^>]*title="([^"]+)"', block)
            if not title_match:
                continue
            model_name = title_match.group(1).strip()

            sizes = re.findall(r'<span[^>]*x-test-size[^>]*>([^<]+)</span>', block)
            sizes = [s.strip() for s in sizes if s.strip()]
            self.models[model_name] = sizes

        self.model_names = list(self.models.keys())

    def install(self, model_name):
        if not model_name:
            raise ValueError("Model name must be provided for installation.")

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

        process.stdout.close()
        process.wait()

    def model_selection(self):
        print("Available Models:\n")
        for idx, name in enumerate(self.model_names):
            print(f"{idx + 1}. {name}")

        choice = int(input("\nSelect a model by number: ")) - 1
        model = self.model_names[choice]
        sizes = self.models[model]

        size = None
        if sizes:
            print(f"\nAvailable sizes for {model}:")
            for idx, s in enumerate(sizes):
                print(f"{idx + 1}. {s}")
            size_choice = int(input("Select a size by number: ")) - 1
            size = sizes[size_choice]

        full_model = f"{model}:{size}" if size else model
        self.install(full_model)

# Example usage
ollama_model = OllamaModel()
ollama_model.model_selection()
