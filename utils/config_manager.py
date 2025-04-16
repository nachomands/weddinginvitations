import json
from PyQt5.QtCore import QPoint, QSize


class ConfigManager:
    def __init__(self):
        self.config_file = 'config.json'
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                'window_geometry': None,
                'last_range': '',
                'faction': "Light Side",
                'total_recruits': 0,
                'state': {
                    'is_running': False,
                    'is_paused': False,
                    'current_range': None,
                    'recruits_count': 0,
                    'total_processed': 0,
                    'failed_invites': 0
                }
            }
            self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def save_window_geometry(self, pos, size):
        self.config['window_geometry'] = [pos.x(), pos.y(), size.width(), size.height()]
        self.save_config()

    def get_window_geometry(self):
        geometry = self.config.get('window_geometry')
        return geometry if geometry else None

    def save_faction(self, faction):
        self.config['faction'] = faction
        self.save_config()

    def save_state(self, state):
        self.config['state'] = state
        self.save_config()

    def get_state(self):
        return self.config.get('state', {})