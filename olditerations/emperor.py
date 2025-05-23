import time
import json
import pygetwindow as gw
import pyautogui
import random
from PIL import ImageGrab, Image
import easyocr
import numpy as np

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
time.sleep(0.5)  # Step 2: Delay for 0.5 seconds

# Coordinates of the region to extract text from
region = (59, 247, 391, 1008)  # (left, top, right, bottom)

# Function to move the mouse to a random position within 5 pixels of the rightmost edge of the box
def move_mouse_to_random_right_edge(region):
    x = random.randint(region[2] - 5, region[2])
    y = random.randint(region[1], region[3])
    pyautogui.moveTo(x, y)

# Move the mouse to the random position on the right edge of the box
move_mouse_to_random_right_edge(region)

# Initialize EasyOCR reader with specified settings
reader = easyocr.Reader(['en', 'fr', 'es', 'de', 'pt'], gpu=True)  # Including multiple languages to support accented characters

# Function to capture text from the specified region
def capture_text_from_region(region):
    screenshot = ImageGrab.grab(bbox=region)
    screenshot = screenshot.resize((screenshot.width * 2, screenshot.height * 2), Image.LANCZOS)  # Double the size
    screenshot_np = np.array(screenshot)  # Convert PIL Image to numpy array
    allowlist = (
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ '
        'ÀÁÂÄÃÆÅ'
        'ÈÉÊË'
        'ÌÍÎÏ'
        'ÒÓÔÖÕØ'
        'ÙÚÛÜ'
        'Ý'
        'Ñ'
        'Ç'
        'ß'
        '\'-'  # Apostrophe and dash
    )
    extracted_text = reader.readtext(screenshot_np,
                                     detail=0,
                                     paragraph=False,
                                     allowlist=allowlist,  # Use the updated allowlist
                                     contrast_ths=0.1,  # Adjust as needed
                                     text_threshold=0.7)  # Adjust as needed
    text_lines = [line.replace("\\", "").strip() for line in extracted_text if line.strip()]
    return text_lines

# Path to save the JSON file
json_file_path = r"C:\Users\Chris\PycharmProjects\emperor\.venv\data\extracted_text.json"

# Load existing names from the JSON file if it exists
try:
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        existing_text_lines = set(json.load(json_file))
except FileNotFoundError:
    existing_text_lines = set()

# Perform initial text extraction
initial_text_lines = capture_text_from_region(region)
print(f"Extracted text: {initial_text_lines}")  # Print extracted text for debugging
final_text_lines = existing_text_lines.union(set(initial_text_lines))

# Scroll and extract text 4 more times
for i in range(4):
    time.sleep(0.5)  # Small delay before scrolling
    pyautogui.scroll(-20 * 120)  # Scroll down 20 times (120 is a typical scroll amount)
    time.sleep(0.5)  # Small delay after scrolling
    move_mouse_to_random_right_edge(region)  # Move mouse to the right edge again before next capture
    new_text_lines = capture_text_from_region(region)
    print(f"Extracted text: {new_text_lines}")  # Print extracted text for debugging
    final_text_lines.update(new_text_lines)  # Add new text lines, avoiding duplicates

# Convert the final set to a list and sort it alphabetically
final_text_lines = sorted(list(final_text_lines))

# Save the extracted text to a JSON file without escaping Unicode characters
with open(json_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(final_text_lines, json_file, ensure_ascii=False, indent=4)

print(f"Extracted text saved to {json_file_path}")