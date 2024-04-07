import json

from objects.StreamHandler import StreamHandler
from pathlib import Path

class Worker:
    """
    Worker is a class that creates a worker object.

    Args:
        model (str): The name of the model to use.
    
    Returns:
        None
    """
    def __init__(self, model):
        self.model = model
        self.config = self.load_config()
        
    def load_config(self):
        config_path = Path(__file__).resolve().parent.parent / 'configs' / 'config.json'
        with config_path.open('r', encoding='utf-8') as f:
            config = json.load(f)
        return config