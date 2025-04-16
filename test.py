import time
import json
from datetime import datetime, UTC
import pygetwindow as gw
import pyautogui
import easyocr
import numpy as np
from PIL import ImageGrab, Image
import unicodedata


class TestExtraction:
    def __init__(self):
        self.window_title = "Star Wars™: The Old Republic™"

        # Initialize EasyOCR
        print("Initializing EasyOCR...")
        self.reader = easyocr.Reader(
            ['en', 'fr', 'es', 'de', 'pt'],
            gpu=True
        )

        self.regions = {
            'who': (23, 51, 255, 105),
            'text_entry': (62, 126, 436, 164),
            'results': (776, 122, 1222, 172),
            'scroll': (1187, 239, 1216, 1023),
            'names': (58, 240, 400, 1016)
        }

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

    def log(self, message):
        """Log message with timestamp"""
        date = datetime.now(UTC).strftime('%Y-%m-%d')
        print(f"[{date}] {message}")

    def sort_names(self, names):
        """Sort names while properly handling accented characters"""
        return sorted(names, key=lambda x: unicodedata.normalize('NFKD', x).encode('ASCII', 'ignore').decode())

    def get_game_window(self):
        """Verify game window is available"""
        for window in gw.getWindowsWithTitle(self.window_title):
            if self.window_title in window.title:
                return window
        return None

    def get_total_players(self):
        """Get total number of players from results region"""
        try:
            image = self.capture_region('results')
            results = self.reader.readtext(
                image,
                detail=0,
                paragraph=False,
                allowlist='0123456789 ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                # Allow all letters and numbers
                contrast_ths=0.1,
                text_threshold=0.7
            )

            # Look for "Showing X results" pattern
            for result in results:
                # Try to find a number in the text
                numbers = ''.join(filter(str.isdigit, result))
                if numbers and "result" in result.lower():  # Make sure we have both a number and the word "result"
                    total_players = int(numbers)
                    # Validate the number is within acceptable range (1-100)
                    if 1 <= total_players <= 100:
                        self.log(f"Total players found: {total_players}")
                        return total_players
                    else:
                        self.log(f"WARNING: Invalid player count ({total_players}), defaulting to 20")
                        return 20

            self.log("WARNING: Could not determine player count")
            return 20  # Default to one page if we can't determine
        except Exception as e:
            self.log(f"Error getting player count: {str(e)}")
            return 20  # Default to one page on error

    def calculate_required_captures(self, total_players):
        """Calculate how many captures needed based on total players"""
        # Each page shows 20 players
        required_captures = (total_players + 19) // 20  # Round up division
        self.log(f"Required captures: {required_captures} for {total_players} players")
        return required_captures

    def capture_region(self, region_name):
        """Capture and preprocess a screenshot of the specified region"""
        region = self.regions[region_name]
        self.log(f"Capturing region {region_name}: {region}")

        screenshot = ImageGrab.grab(bbox=region)
        # Save original screenshot for verification
        screenshot.save(f"test_capture_{region_name}_original.png")

        # Resize and save processed version
        processed = screenshot.resize(
            (screenshot.width * 2, screenshot.height * 2),
            Image.LANCZOS
        )
        processed.save(f"test_capture_{region_name}_processed.png")

        return np.array(processed)

    def test_extraction(self):
        """Test the name extraction process"""
        self.log("Starting extraction test...")

        # Check game window
        window = self.get_game_window()
        if not window:
            self.log("ERROR: Game window not found!")
            return

        self.log("Game window found, proceeding with test...")
        window.activate()
        time.sleep(0.5)

        # Get total number of players and calculate required captures
        total_players = self.get_total_players()
        required_captures = self.calculate_required_captures(total_players)

        # Store all captured names
        all_captures = []
        names_set = set()

        # Initial capture
        self.log("Performing initial capture...")
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
        all_captures.append({
            "capture": "initial",
            "names": initial_names
        })
        names_set.update(initial_names)

        self.log(f"Initial names found: {initial_names}")

        # Only perform additional captures if needed
        for i in range(required_captures - 1):  # -1 because we already did initial capture
            self.log(f"Performing scroll capture {i + 1}/{required_captures - 1}...")

            # Move to scroll area
            x = self.regions['scroll'][0] + 5
            y = self.regions['scroll'][1] + ((self.regions['scroll'][3] - self.regions['scroll'][1]) // 2)
            pyautogui.moveTo(x, y)
            time.sleep(0.5)

            # Scroll
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
            all_captures.append({
                "capture": f"scroll_{i + 1}",
                "names": new_names
            })
            names_set.update(new_names)

            self.log(f"Names found in scroll {i + 1}: {new_names}")

        # Save results to JSON
        test_results = {
            "test_info": {
                "date": datetime.now(UTC).strftime('%Y-%m-%d'),
                "total_players_reported": total_players,
                "captures_required": required_captures
            },
            "total_unique_names": len(names_set),
            "all_captures": all_captures,
            "unique_names_sorted": self.sort_names(list(names_set))
        }

        with open('test_results.json', 'w', encoding='utf-8') as f:
            json.dump(test_results, f, ensure_ascii=False, indent=4)

        self.log(f"Test complete! Found {len(names_set)} unique names.")
        self.log("Results saved to test_results.json")
        self.log("Screenshots saved as test_capture_*.png")


if __name__ == "__main__":
    tester = TestExtraction()
    tester.test_extraction()