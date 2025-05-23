import time
import json
import pygetwindow as gw
import pyautogui
import random
from datetime import datetime

# Step 1: Bring the specified window to the foreground
window_title = "Star Wars™: The Old Republic™"
window = None

for w in gw.getWindowsWithTitle(window_title):
    if window_title in w.title:
        window = w
        break

if not window:
    print(f"Window with title '{window_title}' not found.")
    exit(1)

window.activate()
time.sleep(1)  # Step 2: Delay for 1 second

# Path to the JSON files
extracted_text_path = r"C:\Users\Chris\PycharmProjects\emperor\.venv\data\extracted_text.json"
dnd_path = r"C:\Users\Chris\PycharmProjects\emperor\.venv\data\dnd.json"

# Load the JSON arrays
with open(extracted_text_path, 'r', encoding='utf-8') as json_file:
    names = json.load(json_file)

# Load or initialize the dnd.json
try:
    with open(dnd_path, 'r', encoding='utf-8') as dnd_file:
        dnd = json.load(dnd_file)
except FileNotFoundError:
    dnd = {}

# Get today's date as a string
today_str = datetime.now().strftime('%Y-%m-%d')

# Ensure today's date is in the dnd dictionary
if today_str not in dnd:
    dnd[today_str] = []

# Function to invite a player
def invite_player(name):
    pyautogui.press('enter')
    time.sleep(random.uniform(0.2, 0.5))  # Random delay between 0.2 to 0.5 seconds
    command = "/ginvite "
    for char in command:
        pyautogui.typewrite(char)
        time.sleep(0.1)  # Small delay between each character to ensure they are typed correctly
    pyautogui.typewrite(name)
    pyautogui.press('enter')
    time.sleep(0.5)  # Pause for 0.5 seconds before ending the script

# Iterate over the names and invite each one
while names:
    name = names[0]
    if name not in dnd[today_str]:
        try:
            print(f"Inviting {name}...")
            invite_player(name)
            dnd[today_str].append(name)  # Add the name to dnd under today's date
            names.pop(0)  # Remove the name from the extracted text list
            # Save the updated extracted text list
            with open(extracted_text_path, 'w', encoding='utf-8') as json_file:
                json.dump(names, json_file, ensure_ascii=False, indent=4)
            # Save the updated dnd list
            with open(dnd_path, 'w', encoding='utf-8') as dnd_file:
                json.dump(dnd, dnd_file, ensure_ascii=False, indent=4)
            print(f"Invited {name} to the guild.")
        except Exception as e:
            print(f"Error inviting {name}: {str(e)}")
    else:
        print(f"{name} is already in the DND list for today.")
        names.pop(0)  # Remove the name from the extracted text list since it's already in the DND list
        # Save the updated extracted text list
        with open(extracted_text_path, 'w', encoding='utf-8') as json_file:
            json.dump(names, json_file, ensure_ascii=False, indent=4)
    time.sleep(random.uniform(0.2, 0.75))  # Random delay between 0.2 to 0.75 seconds before the next invite

print("Processed all invitations and updated dnd list.")
