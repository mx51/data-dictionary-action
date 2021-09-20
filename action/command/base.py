import logging
import json
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Optional


class Command(metaclass=ABCMeta):
    def __init__(self, workspace: str):
        self.data_path = Path(workspace) / "data.json"

    @abstractmethod
    def execute(self):
        pass

    def read_data(self) -> Optional[dict]:
        if self.data_path.exists():
            try:
                with open(self.data_path, mode="r", encoding="utf-8") as f:
                    return json.load(f)
            except json.decoder.JSONDecodeError:
                logging.warning("Failed to parse existing data.json")
        else:
            logging.warning("Failed to find data.json")

        return None

    def write_data(self, data: dict):
        with open(self.data_path, mode="w", encoding="utf-8") as f:
            json.dump(data, f, skipkeys=True, indent=4)
