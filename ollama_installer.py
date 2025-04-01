import os
import time
import shutil
import requests
import subprocess
from datetime import datetime
from tqdm import tqdm
from requests.adapters import HTTPAdapter, Retry
import argparse


class OllamaInstaller:
    def __init__(self, install_dir=None, setup_file_dir=None,  models_path=None, mode=None, debug=False ):
        """
        Initialize the Ollama Installer.

        Args:
            install_dir (str, optional): Directory where Ollama should be installed.
            mode (str, optional): Installation mode (e.g., "silent" "VERYSILENT").
            debug (bool, optional): If True, prints real-time installation logs.
        """
        self.installer_name = "OllamaSetup.exe"
        self.install_dir = install_dir
        self.mode = mode
        self.debug = debug
        self.models_path = models_path

        if setup_file_dir:
           self.installer_path = setup_file_dir
        else:
            self.installer_path = os.path.join(self.install_dir, self.installer_name) if self.install_dir else self.installer_name
        self.log_file = self.get_log_filename()
        
        # Ensure save directory exists
        if self.install_dir:
            normalized_path = os.path.normpath(self.install_dir)  # Normalize path to remove trailing slashes
            if os.path.basename(normalized_path) != "ollama":  # Check if the last directory is "ollama"
                self.install_dir = os.path.join(self.install_dir, "ollama")
            os.makedirs(self.install_dir, exist_ok=True)
        if self.models_path:
            os.makedirs(self.models_path, exist_ok=True)

    def kill_ollama(self):
        """Kill all Ollama processes."""
        processes = ["ollama.exe", "ollama app.exe"]

        for process in processes:
            try:
                task_list_process = subprocess.run(["tasklist"], capture_output=True, text=True)
                if "ollama.exe" not in task_list_process.stdout:
                    self.write_log("Ollama is not running.")
                    print("Ollama is not running.")
                    return
                result = subprocess.run(["taskkill", "/F", "/IM", process], capture_output=True, text=True)

                if "SUCCESS" in result.stdout:
                    log_message = f"Successfully killed: {process}"
                elif "not found" in result.stdout or result.returncode != 0:
                    log_message = f"Process not found: {process}"
                else:
                    log_message = f"Error killing {process}: {result.stderr.strip()}"

                self.write_log(log_message)
                print(log_message)

            except Exception as e:
                error_message = f"Exception occurred while killing {process}: {str(e)}"
                self.write_log(error_message)
                print(error_message)

    def start_ollama(self):
        """Restart Ollama server and print its output."""
        try:
            ollama_path = os.path.join(self.install_dir, "ollama app.exe")
            process = subprocess.Popen(
                ollama_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            time.sleep(3)  # Wait for 3 seconds

            # Try to read output without blocking
            stdout, stderr = process.communicate(timeout=1)

            if not stdout.strip():
                self.write_log("ollama process started")
                print("ollama process started")
            if stderr.strip():
                self.write_log("Error while starting Ollama: " + stderr.strip())
                print("Error while starting Ollama:", stderr.strip())

        except subprocess.TimeoutExpired:
            process.kill()  # Ensure it stops after 3 seconds
            self.write_log("ollama process started (forced timeout)")
            print("ollama process started (forced timeout)")

        except Exception as e:
            self.write_log(f"An error occurred while starting Ollama: {e}")
            print(f"An error occurred while starting Ollama: {e}")

    def restart_ollama(self):
        self.kill_ollama()
        self.start_ollama()

    def get_log_filename(self):
        """Generate a unique log filename in the format: {base_name}_{dd-mm-yyyy}_{hrs-mins-secs}.log"""
        base_log_file = "ollama_install.log"
        if not os.path.exists(base_log_file):
            return base_log_file
        timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        return f"ollama_install_{timestamp}.log"

    def write_log(self, message):
        """Writes a message to the log file with a timestamp."""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

    def download_installer(self, chunk_size=1024, max_retries=5):
        """Downloads the Ollama setup file with a progress bar and retry logic."""
        url = "https://ollama.com/download/OllamaSetup.exe"

        if os.path.exists(self.installer_path):
            print(f"File already exists at {self.installer_path}. Skipping download.")
            return

        # Setup session with retry logic
        session = requests.Session()
        retries = Retry(total=max_retries, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        session.mount("https://", HTTPAdapter(max_retries=retries))

        try:
            with session.get(url, stream=True, timeout=10) as response:
                response.raise_for_status()  # Handle HTTP errors
                total_size = int(response.headers.get("content-length", 0))

                print(f"Downloading Ollama setup to {self.installer_path}...")
                with open(self.installer_path, "wb") as file, tqdm(
                    desc="Downloading",
                    total=total_size,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                ) as bar:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            file.write(chunk)
                            bar.update(len(chunk))

            print("Download complete!")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to download the file: {e}")

    def tail_log_file(self, process):
        """Reads and prints new lines from the log file while the installation process is running."""
        last_size = 0
        while process.poll() is None:  # Stop when process ends
            try:
                if os.path.exists(self.log_file):
                    with open(self.log_file, "r", encoding="utf-8") as f:
                        f.seek(last_size)  # Move to last read position
                        new_data = f.read()
                        if new_data:
                            print(new_data.strip(), flush=True)
                        last_size = f.tell()  # Update position
                time.sleep(0.5)
            except PermissionError:
                time.sleep(0.5)  # Retry if file is locked

    def check_ollama_installed(self):
        command = (
            'powershell -Command '
            '"@(Get-Package | Where-Object { $_.Name -like \'*ollama*\' })"'
        )
        result = subprocess.run(command, capture_output=True, text=True, shell=True)

        if result.returncode != 0:
            print("Error running PowerShell command:", result.stderr)
            return False

        if not result.stdout.strip():
            print("Ollama is NOT installed.")
            return False
        else:
            print("Ollama is installed.")
            return True

    def is_ollama_installed(self):
        print("Checking if Ollama is installed...")
        """Checks if Ollama is installed by looking for its executable."""
        try:
            if self.install_dir:
                os.environ["PATH"] = self.install_dir + os.pathsep + os.environ["PATH"] # Add install directory to PATH variables temporarily
            ollama_path = shutil.which("ollama")
            if ollama_path:
                return ollama_path  # Ollama is installed
            else:
                return None  # Ollama is not installed

        except Exception as e:
            print(f"Error checking Ollama installation: {e}")
            return False  # Assume not installed on error
        
    def install_ollama(self):
        """Installs Ollama using the downloaded installer."""
        self.write_log("Starting Ollama installation...")
        ollama_installed = self.check_ollama_installed()
        if ollama_installed:
            print(f"Skipping installation ollama already found.")
            self.write_log(f"Skipping installation ollama already found.")
            return

        if not os.path.exists(self.installer_path):
            self.write_log("Error: Installer file not found.")
            print("Error: Installer not found.")
            return
        
        # Build installation command
        install_command = [self.installer_path]
        if self.mode:
            install_command.append(f"/{self.mode}")
        if self.install_dir:
            install_command.append(f"/DIR={self.install_dir}")
        install_command.append(f"/LOG={self.log_file}")

        self.write_log(f"Running command: {' '.join(install_command)}")
        print(f"Log file: {self.log_file}")

        try:
            process = subprocess.Popen(
                install_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            # Real-time log monitoring
            if self.debug:
                self.tail_log_file(process)

            stdout, stderr = process.communicate()

            if process.returncode == 0:
                ollama_path = self.is_ollama_installed()
                if ollama_path:
                    if self.set_ollama_env_var():
                        self.write_log(f"{self.install_dir} is added to PATH variable")
                    else:
                        self.write_log(f"failed to add {self.install_dir} to PATH variable")
                    self.write_log(f"Ollama installed successfully at {ollama_path}")
                    print(f"\nOllama installed successfully at {ollama_path}")
            else:
                self.write_log(f"Installation failed. Error: {stderr.strip()}")
                print(f"\nInstallation failed. Error: {stderr.strip()}")

        except Exception as e:
            self.write_log(f"Unexpected error: {str(e)}")
            print(f"Unexpected error: {e}")

    def system_var_exists(self, var_name):
        """Check if a system environment variable exists."""
        try:
            result = subprocess.run(
                ["powershell", "-Command", f"[System.Environment]::GetEnvironmentVariable('{var_name}', 'Machine')"],
                capture_output=True, text=True
            )
            return result.stdout.strip()  # Returns the value if exists, empty string otherwise
        except Exception as e:
            print(f"Error checking system variable: {e}")
            return None
        
    def set_models_location(self,models_path):
        # if models_path is not None and not os.path.exists(models_path):
        #     print("Invalid path location for saving the models")
        #     return 
        existing_value = self.system_var_exists("OLLAMA_MODELS")
        if existing_value and existing_value != models_path :
            print(f"Environment variable OLLAMA_MODELS already exists with value: {existing_value}")
            choice = input(f"Do you want to override it with {models_path}? (y/N): ").strip().lower()
            if choice != "y":
                print(f"Ollama models will be installed in {existing_value}.")
                return
        else:
            return
        command = f"cmd /c setx OLLAMA_MODELS \"{models_path}\" /M"

        process = subprocess.Popen([
            "powershell", 
            "-Command", 
            f"Start-Process -FilePath cmd -ArgumentList '/c {command}' -Verb RunAs"
        ], shell=True)
        self.write_log(f"Running command: {' '.join(command)}")

        process.wait()

        if process.returncode == 0:
            self.write_log(f"Successfully added system variable: OLLAMA_MODELS={models_path}")
            print(f"Successfully added system variable: OLLAMA_MODELS={models_path}")
        else:
            print("Admin access denied or UAC prompt was closed!")
            self.write_log("Admin access denied or UAC prompt was closed!")
            return

    def set_ollama_env_var(self):
        print("Adding Ollama executable directory to system PATH")

        command = f'setx PATH "%PATH%;{self.install_dir}" /M'

        # Run the command as administrator using PowerShell
        process = subprocess.Popen([
            "powershell",
            "-Command",
            f"Start-Process cmd -ArgumentList '/c {command}' -Verb RunAs"
        ], shell=True)

        self.write_log(f"🛠 Running command: {command}")

        process.wait()

        if process.returncode == 0:
            self.write_log(f"Successfully added Ollama to PATH: {self.install_dir}")
            print(f"Ollama path added: {self.install_dir}")
            return True
        else:
            print("Admin access denied or UAC prompt was closed! while trying to add the Ollama path to PATH variable")
            self.write_log("Admin access denied or UAC prompt was closed! while trying to add the Ollama path to PATH variable")
            return False


if __name__ == "__main__":
    # Demo Usage:
    # python ollama_installer.py -i "C:/path/to/install" -m "C:/path/to/models" -M silent -d -s "C:/path/to/OllamaSetup.exe"
    # This command installs Ollama to the specified install directory, sets models location, and enables debug mode.
    parser = argparse.ArgumentParser(description="Ollama Installer Script")
    parser.add_argument("-i", "--install_dir", type=str, help="Directory where Ollama should be installed", required=False)
    parser.add_argument("-m", "--models_path", type=str, help="Path where models should be stored", required=False)
    parser.add_argument("-M", "--mode", type=str, help="Installation mode (e.g., silent, VERYSILENT)", required=False, default="silent")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("-s", "--setup_path", type=str, help="Path to an existing Ollama setup file (if available)", required=False)

    args = parser.parse_args()

    # Check if the specified setup file path exists
    if args.setup_path and not os.path.exists(args.setup_path):
        print(f"Error: The specified setup file path '{args.setup_path}' does not exist.")
        exit(1)

    installer = OllamaInstaller(args.install_dir, args.setup_path, args.models_path, args.mode, args.debug)

    # Check if Ollama is already installed
    if installer.check_ollama_installed():
        print("Ollama is already installed.")
        if not installer.is_ollama_installed():
            print("Warning! No environment variable is set for Ollama.")
    else:
        installer.download_installer()
        installer.install_ollama()
        if args.models_path:
            installer.set_models_location(args.models_path)
        installer.restart_ollama()

