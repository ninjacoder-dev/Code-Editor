import json
import os

class ConfigManager:
    def __init__(self, filename="config.json"):
        self.filename = filename
        self.config = {
            "c_compiler": "gcc",
            "cpp_compiler": "g++",
            "java_compiler": "javac",
            "java_runtime": "java",
            "csharp_compiler": "csc",
            "php_runtime": "php"
        }
        self.load_config()

    def load_config(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    data = json.load(f)
                    self.config.update(data)
            except Exception:
                pass # Use defaults if error

    def save_config(self):
        try:
            with open(self.filename, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception:
            pass

    def get(self, key):
        return self.config.get(key, "")

    def set(self, key, value):
        self.config[key] = value
        self.save_config()
