import sys
import time

def type_out(text, delay=0.007):
    """Simulates a smooth typing effect by printing characters one by one."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print("")  # Move to the next line after completing

response = "Hello! How can I assist you today?"
type_out(response)
