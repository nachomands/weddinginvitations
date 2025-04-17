import time
import random
from datetime import datetime, timedelta
import pygetwindow as gw
import pyautogui
import numpy as np
import easyocr
from PIL import ImageGrab, Image


class RecruitmentHandler:
    def __init__(self, main_window, current_time="2025-04-16 23:53:40", current_user="nachomands"):
        self.main_window = main_window
        self.window_title = "Star Wars™: The Old Republic™"

        # Initialize JsonHandler with current time and user
        self.json_handler = JsonHandler(main_window, current_user, current_time)

        # Initialize EasyOCR with proven settings
        self.reader = easyocr.Reader(
            ['en', 'fr', 'es', 'de', 'pt'],
            gpu=True
        )

        self.allowlist = (
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
            '\'-'
        )

        self.init_regions()
        self.last_who = datetime.now() - timedelta(minutes=5)
        self.current_range = None
        self.names_to_invite = []

    def init_regions(self):
        self.regions = {
            'who': (23, 51, 255, 105),
            'text_entry': (62, 126, 436, 164),
            'results': (776, 122, 1222, 172),
            'scroll': (1187, 239, 1216, 1023),
            'names': (58, 240, 400, 1016)
        }

    def move_to_scroll_area(self):
        """Move mouse to a random position in the scroll area"""
        x = random.randint(self.regions['scroll'][0], self.regions['scroll'][2])
        y = random.randint(self.regions['scroll'][1], self.regions['scroll'][3])
        pyautogui.moveTo(x, y)

    def capture_region(self, region_name):
        """Capture and preprocess a screenshot of the specified region"""
        region = self.regions[region_name]
        screenshot = ImageGrab.grab(bbox=region)
        # Double the size using LANCZOS resampling
        screenshot = screenshot.resize(
            (screenshot.width * 2, screenshot.height * 2),
            Image.LANCZOS
        )
        return np.array(screenshot)

    def extract_names(self, faction="ls"):
        """Extract player names from the WHO results using proven settings"""
        try:
            # Wait for WHO results to populate
            time.sleep(random.uniform(1.5, 2.0))

            names = set()

            # Initial capture
            image = self.capture_region('names')
            results = self.reader.readtext(
                image,
                detail=0,
                paragraph=False,
                allowlist=self.allowlist,
                contrast_ths=0.1,
                text_threshold=0.7
            )

            initial_names = [name.strip() for name in results if name.strip()]
            self.main_window.log_console.log_message(f"Initial names found: {initial_names}", "blue")
            names.update(initial_names)

            # Scroll and capture 4 more times
            for i in range(4):
                # Move to scroll area before scrolling
                self.move_to_scroll_area()
                time.sleep(0.5)

                # Scroll down
                pyautogui.scroll(-20 * 120)
                time.sleep(0.5)

                # Capture and process
                image = self.capture_region('names')
                results = self.reader.readtext(
                    image,
                    detail=0,
                    paragraph=False,
                    allowlist=self.allowlist,
                    contrast_ths=0.1,
                    text_threshold=0.7
                )

                new_names = [name.strip() for name in results if name.strip()]
                self.main_window.log_console.log_message(f"Scroll {i + 1} names found: {new_names}", "blue")
                names.update(new_names)

            # Filter out names in DND list using JsonHandler
            valid_names = [name for name in names if not self.json_handler.is_in_dnd(name, faction)]
            self.main_window.log_console.log_message(f"Total valid names found: {len(valid_names)}", "green")

            # Update invite list with valid names
            self.json_handler.update_invite_list(valid_names, faction)

            return sorted(valid_names)

        except Exception as e:
            self.main_window.log_console.log_message(f"Name Extraction Error: {str(e)}", "red")
            return []

    def send_who_command(self, level_range):
        """Send WHO command for the specified level range"""
        try:
            if (datetime.now() - self.last_who).total_seconds() < 60:
                self.main_window.log_console.log_message("Waiting for WHO cooldown...", "yellow")
                return False

            window = self.get_game_window()
            if not window:
                return False

            # Click text entry area first
            entry_x = self.regions['text_entry'][0] + 10
            entry_y = self.regions['text_entry'][1] + 10
            pyautogui.click(entry_x, entry_y)
            time.sleep(random.uniform(0.2, 0.3))

            # Type WHO command
            pyautogui.write(f"/who {level_range}")
            time.sleep(random.uniform(0.3, 0.5))
            pyautogui.press('enter')

            self.last_who = datetime.now()
            return True
        except Exception as e:
            self.main_window.log_console.log_message(f"WHO Command Error: {str(e)}", "red")
            return False

    def get_game_window(self):
        """Get the SWTOR game window"""
        try:
            for window in gw.getWindowsWithTitle(self.window_title):
                if self.window_title in window.title:
                    return window
            return None
        except Exception as e:
            self.main_window.log_console.log_message(f"Window Error: {str(e)}", "red")
            return None
